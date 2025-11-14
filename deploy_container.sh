#!/bin/bash

set -euo pipefail

# Load .env
if [ -f .env ]; then
  # export only non-empty lines not starting with #
  export $(grep -v '^\s*#' .env | xargs -r)
else
  echo "config Error: .env file not found. Copy .env.example to .env and configure it"
  exit 1
fi

DOMAIN=${DOMAIN:-localhost}
EMAIL=${EMAIL:-alex@gmail.com}

docker-compose down --remove-orphans || true
docker rmi sim_main_api_img sim_micro_img -f 2>/dev/null || true

mkdir -p certs certbot-data nginx/conf.d

#local runs use self-signed cert
if [ "$DOMAIN" = "localhost" ]; then
  mkdir -p certs/live/localhost
  openssl req -x509 -newkey rsa:4096 \
    -keyout certs/live/localhost/privkey.pem \
    -out certs/live/localhost/fullchain.pem \
    -days 365 -nodes -subj "/CN=localhost"

  #create the final nginx conf
  cat > nginx/conf.d/ssl.conf <<EOF
server {
    listen 80;
    server_name localhost;

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/letsencrypt/live/localhost/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/localhost/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://sim_main_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

  #start up service for localhost
  docker-compose up --build -d
  echo "Deployed with self-signed localhost certificate. Visit: https://localhost"
  exit 0
fi


#PRODUCTION
#if domain isnt set to localhost, then we move here
if [ -f nginx/conf.d/ssl.conf ]; then
  rm -f nginx/conf.d/ssl.conf
fi

#start up app with the nginx.conf WHICH ONLY HAS HTTP IN IT
#because certbot needs http running before giving the ssl cert
docker-compose up --build -d sim-main-api sim-micro-api nginx

#loop i found to wait until nginx http setup is good
for i in {1..30}; do
  if docker exec nginx_gateway nginx -t >/dev/null 2>&1; then
    break
  fi
  sleep 1
done


docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
  -d "${DOMAIN}" -m "${EMAIL}" --agree-tos --non-interactive --register-unsafely-without-email


#now we create the nginx with the https(443) being used
cat > nginx/conf.d/ssl.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        alias /var/www/certbot/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://sim_main_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

#reload nginx to get the updated ssl
#nginx uses the last loaded config block, so now http port 80 requests gotot the new block above instead
#of the originially loaded nginx/nginx.conf file..
docker exec nginx_gateway nginx -s reload

echo "HTTPS enabled for ${DOMAIN}. Visit: https://${DOMAIN}"
