#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

gunicorn server.wsgi:application --bind 0.0.0.0:$PORT



