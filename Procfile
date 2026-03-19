web: python manage.py migrate --run-syncdb && python railway_setup.py && python manage.py collectstatic --noinput --clear && gunicorn db_portal.wsgi --bind 0.0.0.0:$PORT
