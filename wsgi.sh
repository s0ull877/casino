#!/bin/bash

sleep 5
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py create_superuser

uwsgi --socket=:9000 --module=app.wsgi:application --py-autoreload=1