#!/bin/bash

# Deployment Helper Script

cd "$(dirname "$0")/.."

echo "Deploying..."

# Pull latest code
git pull origin main

# Build and start containers
docker compose -f deployment/docker-compose.yml up -d --build

# Run migrations
docker compose -f deployment/docker-compose.yml exec web python manage.py migrate

# Collect static files
docker compose -f deployment/docker-compose.yml exec web python manage.py collectstatic --noinput

echo "Deployment completed!"
