#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
exec gunicorn db_portal.wsgi --bind 0.0.0.0:$PORT