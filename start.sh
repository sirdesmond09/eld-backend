#!/bin/bash

# Build the images
docker-compose build

# Start the database in the background
docker-compose up -d db redis

# Run migrations and tests
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations core && python manage.py migrate"

# If tests pass, start all services
if [ $? -eq 0 ]; then
    echo "Tests passed! Starting all services..."
    docker-compose up
else
    echo "Tests failed! Please fix the issues before starting the services."
    exit 1
fi
