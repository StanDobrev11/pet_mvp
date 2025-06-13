#!/bin/bash
cd /repo/pet_mvp || exit 1

# Fetch latest changes
git fetch

# Check if there are new commits
if ! git diff --quiet HEAD origin/main; then
    echo "Changes detected. Pulling..."
    git pull origin main

    echo "Rebuilding Docker images..."
    docker-compose build

    echo "Starting application containers (excluding nginx)..."
    docker-compose up -d redis celery celery-beat app  # any services EXCEPT nginx

    echo "Waiting for backend to become ready..."

    # Health check loop (replace URL/port as needed)
    for i in {1..20}; do
        if curl -s http://localhost:8000/api/health/ > /dev/null; then
            echo "Backend is ready."
            break
        fi
        echo "Waiting... ($i/20)"
        sleep 3
    done

    echo "Starting NGINX..."
    docker-compose up -d nginx
else
    echo "No changes found. Everything is up to date."
fi
