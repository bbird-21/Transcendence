#!/bin/sh

python3 manage.py makemigrations
python3 manage.py migrate
gunicorn -b 0.0.0.0:8000 ft_transcendence.wsgi:application
# gunicorn ft_transcendence.wsgi
# daphne -e ssl:443:privateKey=key.pem:certKey=crt.pem ft_transcendence.asgi:application

