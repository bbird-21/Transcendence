#!/bin/sh

python3 manage.py makemigrations
python3 manage.py migrate
#daphne -b 0.0.0.0 -p 8000 ft_transcendence.asgi:application
python3 manage.py runserver 0.0.0.0:8000

