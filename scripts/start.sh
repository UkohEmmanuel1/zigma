#!/bin/sh
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn app.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-30} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${GUNICORN_LOG_LEVEL:-info} \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --worker-class sync
