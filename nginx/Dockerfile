# Use the official Nginx image as a base
FROM nginx:alpine

# Set environment variables
ARG IS_PROD
ENV IS_PROD=${IS_PROD}

# Install Certbot for Let's Encrypt certificate generation
RUN apk add --no-cache certbot openssl

# Copy Nginx configuration
COPY conf.d/ /etc/nginx/conf.d/
COPY ssl/ /etc/nginx/ssl/

# Run script to create SSL certificates
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

