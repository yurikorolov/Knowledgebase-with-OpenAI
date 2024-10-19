#!/bin/sh

set -e

# Load environment variables
DOMAIN=${DOMAIN:-"localhost"}  # Default to localhost if not set
EMAIL=${EMAIL:-"your_email@example.com"}  # Default email if not set

if [ "$IS_PROD" = "true" ]; then
    echo "Starting Let's Encrypt certificate generation..."

    # Run Certbot to generate Let's Encrypt certificates
    certbot certonly --standalone --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN"

    # Copy generated certificates to the appropriate location
    cp /etc/letsencrypt/live/"$DOMAIN"/fullchain.pem /etc/nginx/ssl/fullchain.pem
    cp /etc/letsencrypt/live/"$DOMAIN"/privkey.pem /etc/nginx/ssl/privkey.pem
else
    echo "Using self-signed snakeoil certificates..."

    # Generate self-signed certificates
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/privkey.pem \
        -out /etc/nginx/ssl/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
fi

# Start Nginx
nginx -g "daemon off;"

