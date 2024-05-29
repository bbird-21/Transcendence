# Use an official Python runtime as a parent image
FROM python:3.12-alpine3.19

COPY . /django
RUN apk add gcc
RUN apk add musl-dev
RUN apk add libffi-dev
RUN rm -rf /var/cache/apk/*
RUN pip3 install -r /django/requirements.txt --no-cache-dir
WORKDIR /django/ft_transcendence
RUN chmod +x run.sh
ENTRYPOINT [ "sh", "run.sh" ] 
