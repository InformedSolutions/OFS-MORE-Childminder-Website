#!/bin/sh

echo Waiting for database to start...;
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT;
   do
    sleep 1;
   done;
echo Connected!;

# Create database migration files
echo "Create database migration files"
python manage.py makemigrations --settings=$PROJECT_SETTINGS
python manage.py makemigrations application --settings=$PROJECT_SETTINGS

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --settings=$PROJECT_SETTINGS
python manage.py migrate application --settings=$PROJECT_SETTINGS

#Collect static resources
echo "Collecting static assets"
python manage.py collectstatic --settings=$PROJECT_SETTINGS --noinput

# Start server
echo "Starting server"
python manage.py runserver --settings=$PROJECT_SETTINGS 0.0.0.0:8000
