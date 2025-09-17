#!/bin/bash

# Initialize Let's Encrypt certificates for nginx on port 23232
# This script uses DNS challenge since we can't use port 80

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

domains=(${DOMAIN:-localhost})
rsa_key_size=4096
data_path="./certbot"
email=${EMAIL:-"admin@example.com"}
staging=${STAGING:-0}

echo "=== Let's Encrypt Setup for Port 23232 ==="
echo "Domain: ${domains[0]}"
echo "Email: $email"
echo "Staging: $staging"
echo ""

if [ -d "$data_path" ]; then
  read -p "Existing data found for ${domains[0]}. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

# Download recommended TLS parameters
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

# Create dummy certificate for initial nginx startup
echo "### Creating dummy certificate for ${domains[0]} ..."
path="/etc/letsencrypt/live/default"
mkdir -p "$data_path/conf/live/default"
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=${domains[0]}'" certbot
echo

echo "### Starting nginx ..."
docker-compose up --force-recreate -d nginx
echo

echo "### Deleting dummy certificate for ${domains[0]} ..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/default && \
  rm -Rf /etc/letsencrypt/archive/default && \
  rm -Rf /etc/letsencrypt/renewal/default.conf" certbot
echo

echo "### Requesting Let's Encrypt certificate for ${domains[0]} ..."
echo "NOTE: Since we're using port 23232, you need to use DNS challenge."
echo "Please set up DNS TXT record as prompted by certbot."
echo ""

# Join $domains to -d args
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

# Use manual DNS challenge since we can't use port 80
docker-compose run --rm --entrypoint "\
  certbot certonly --manual --preferred-challenges dns \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal \
    --cert-name default" certbot
echo

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload

echo ""
echo "=== Setup Complete ==="
echo "Your app is now available at: https://${domains[0]}:23232"
echo "Certificate will auto-renew every 12 hours via the certbot container."
