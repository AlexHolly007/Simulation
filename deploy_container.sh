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
  openssl req -x509 -newkey rsa:4096 -keyout certs/live/localhost/privkey.pem -out certs/live/localhost/fullchain.pem -days 365 -nodes -subj "/CN=localhost"

  #load the hidden localhost(developemet) conf, to test 443, htttps to work, but with self made cert only
  #this was not being seen before moved to conf.d folder
  mv nginx/hidden_local_ssl.conf nginx/conf.d/ssl.conf

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


#move the new confid file that uses ssl 443 because we have our cert
#this was not active before because nginx is looking in nginx/conf.d for more config files previously
mv nginx/hidden_prod_ssl.conf nginx/conf.d/ssl.conf

#reload nginx to get the updated ssl
#nginx uses the last loaded config block, so now http port 80 requests gotot the new block above instead
#of the originially loaded nginx/nginx.conf file..
docker exec nginx_gateway nginx -s reload

echo "HTTPS enabled for ${DOMAIN}. Visit: https://${DOMAIN}"
