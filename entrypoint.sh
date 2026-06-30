#!/bin/sh
echo "Running migrations..."

python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn greatkart.wsgi:application --bind 0.0.0.0:8000 --workers 15 --timeout 300
