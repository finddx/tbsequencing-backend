#!/usr/bin/env bash
set -e

python manage.py collectstatic --no-input --clear
gunicorn --config gunicorn.conf.py
