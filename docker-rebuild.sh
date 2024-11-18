#!/usr/bin/env bash
# Totally rebuild docker compose deployment from scratch
# Use if stuck
set -e

docker compose down -v
docker compose up -d --build
echo "Waiting a little for database to get up..."
sleep 5
docker compose exec web python manage.py migrate
docker compose exec web python manage.py postmigrate
