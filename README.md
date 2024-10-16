# ft_transcendence
## Description
This is the final project of School 42 common core.

## Installation
How to get started:

```bash
git@github.com:bbird-21/Transcendence.git
cd Transcendence
```
### config dotenv
Make sure to look .env.template and make a .env file from it
For more info on [django secret key](#django-secret-key)

### build
Then you can run the following command to start the project:

```bash
make all
```

## Usage

You can access the website at the following address: `localhost:8000`

## Contributing

For the commits we use [commitizen](https://commitizen-tools.github.io/commitizen)
Thanks install and use it for contributing

## Dev tips
### django manage.py
Once the containers are runnings, thanks to the volume you can freely edit the code in the django folder, it follow in the django container
**If you wanna use `manage.py`** you can use `docker compose exec django python manage.py <cmd>`
_I know the command is quite long so use an alias_

### [django secret key](#django-secret-key)
If you need to generate a django secret key, you can use the following command:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
