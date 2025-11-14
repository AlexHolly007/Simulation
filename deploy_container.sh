#!/bin/bash

#check config .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
else
  echo "config Error: .env file not found. Copy .env.example to .env and configure it"
  exit 1
fi

DOMAIN=${DOMAIN:-localhost}
EMAIL=${EMAIL:-alex@gmail.com}

docker-compose down --remove-orphans
docker rmi sim_main_api_img sim_micro_img -f 2>/dev/null

mkdir -p certs certbot-data

#self-gen certis when on localhost to check https with nginx
if [ "$DOMAIN" = "localhost" ]; then
  mkdir -p certs/live/localhost
  openssl req -x509 -newkey rsa:4096 -keyout certs/live/localhost/privkey.pem -out certs/live/localhost/fullchain.pem -days 365 -nodes -subj "/CN=localhost"
else
  #get real encrypt cert for production
  docker-compose run --rm certbot
fi

docker-compose up --build
