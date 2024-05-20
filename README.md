# ft_transcendence

## Description

This is the final project of School 42 common core.

## Installation

How to get started:

```bash
git clone git@github.com:shocquen/ft_transcendence.git
cd ft_transcendence
```

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
Once the containers are runnings, thanks to the volume you can freely edit the code in the django folder, it follow in the django container
**If you wanna use `manage.py`** you can use `docker compose exec django python manage.py <cmd>`
*I know the command is quite long so use an alias*
