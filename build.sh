#!/usr/bin/env bash
set -o errexit

echo "=== Starting Build ==="
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "=== Build Complete ==="