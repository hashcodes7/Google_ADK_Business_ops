#!/bin/bash
set -e

APP_DIR="/home/ssm-user/apps/gadk-backend"
echo "📁 Ensuring directory structure exists..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ -n "$1" ]; then
  export DOCKER_IMAGE="$1/business-ops-backend:latest"
fi

if [ ! -f .env.prod ]; then
  echo "⚠️ Warning: .env.prod not found, creating an empty placeholder..."
  touch .env.prod
  chmod 600 .env.prod
fi

echo "📦 Pulling latest Docker image (${DOCKER_IMAGE})..."
docker compose -p gadk-backend pull

echo "🔄 Restarting container with zero downtime..."
docker compose -p gadk-backend up -d --remove-orphans

echo "🧹 Pruning unused images..."
docker image prune -f

echo "✅ Deployment completed successfully!"
docker compose -p gadk-backend ps
