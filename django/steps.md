# STEPS USED TO INIT THE PROJECT

## Install

1. Create and activate a virtual environment
   ```bash
   python -m venv ~/.virtualenvs/ft_transcendence
   source ~/.virtualenvs/ft_transcendence/bin/activate
   ```
2. Install Django
   ```bash
   pip install django
   ```
3. Create a Django project
   ```bash
   django-admin startproject ft_transcendence
   ```

## Create the project / app

1. Init the project

```bash
python manage.py startproject project
```

2. Create an app

```bash
python manage.py startapp app
```

3. Add the app to the project:
   `project/settings.py`

```python
INSTALLED_APPS = [
    ...
    'app',
]
```

## Update the project

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

## Create a superUser

1. Init / migrate the builtin DB
   ```bash
   python manage.py migrate
   ```
2. Create a superUser
   ```bash
   python manage.py createsuperuser
   ```

## Run the server

```bash
python manage.py runserver
```
