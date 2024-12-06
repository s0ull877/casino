#!/bin/bash

sleep 5
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

daphne app.asgi:application -b 0.0.0.0 -p 8000