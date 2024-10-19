# Use Python official image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for caching layers
COPY ./app/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create directories for logs and cache
RUN mkdir -p /var/log/app /transformers_cache

# Copy the app code
COPY ./app /app

# Copy Nginx configuration
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Expose ports for Nginx
EXPOSE 80 443

# Add entrypoint script to wait for database readiness
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Environment variables for transformer cache and model (to be set in Docker Compose)
ENV TRANSFORMERS_CACHE=/transformers_cache

# Start the app with entrypoint
ENTRYPOINT ["/entrypoint.sh"]

