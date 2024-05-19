# Use an official Python runtime as a parent image
FROM python:3.12-alpine3.19

WORKDIR /ft_transcendence
COPY requirements.txt /ft_transcendence
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /ft_transcendence 
WORKDIR ./ft_transcendence
ENTRYPOINT [ "python3" ] 
CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]
