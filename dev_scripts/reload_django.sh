# Create a simple script to makemigrations, migrate and create a super user
# This script is useful when you are working with docker and you need to reload the django app
# Usage: ./reload_django.sh

# Make migrations
python manage.py makemigrations

# Migrate
python manage.py migrate

# Create super user
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('super', '', 'superTest123')" | python manage.py shell
