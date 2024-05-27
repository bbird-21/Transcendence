# Use an official Python runtime as a parent image
FROM python:3.12-alpine3.19

COPY requirements.txt /django
RUN apk add gcc
RUN apk add musl-dev
RUN apk add libffi-dev
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /django
WORKDIR /django/ft_transcendence
RUN chmod +x run.sh
ENTRYPOINT [ "sh", "run.sh" ] 
