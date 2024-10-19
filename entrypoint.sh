#!/bin/bash

# Wait for the database to be ready
while ! nc -z db 5432; do
  echo "Waiting for PostgreSQL database connection..."
  sleep 2
done

echo "PostgreSQL database is ready."

# Run the application (with auto-reload)
exec "$@"

