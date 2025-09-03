#!/bin/sh
set -e

echo "Waiting for PostgreSQL at $POSTGRESQL_HOST:$POSTGRESQL_PORT..."

# loop until the DB is ready
sleep 5

echo "PostgreSQL is up!"

# Run migrations and collect static before starting Gunicorn
python manage.py makemigrations
python manage.py migrate --noinput

python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 albumz.wsgi:application
