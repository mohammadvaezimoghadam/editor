#!/bin/sh
set -e

echo "==> [1/4] Running Django database migrations..."
python testmanage.py migrate --noinput

echo "==> [2/4] Creating database cache table..."
python testmanage.py createcachetable || true

echo "==> [3/4] Collecting static files..."
python testmanage.py collectstatic --noinput

# Create default superuser if credentials are provided in .env
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "==> [4/4] Setting up superuser ($DJANGO_SUPERUSER_USERNAME)..."
    python testmanage.py createsuperuser --noinput || true
else
    echo "==> [4/4] Skipping automatic superuser creation (credentials not provided)."
fi

echo "==> Starting Gunicorn WSGI Server on port 8000..."
exec gunicorn testapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
