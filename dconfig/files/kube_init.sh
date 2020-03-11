#!/bin/bash

export DJANGO_ADMIN_USERNAME=${DJANGO_ADMIN_USERNAME-'admin'}
export DJANGO_ADMIN_EMAIL=${DJANGO_ADMIN_EMAIL-'admin@example.com'}
export DJANGO_ADMIN_PASSWORD=${DJANGO_ADMIN_PASSWORD-'adminpass'}

if [ "$1" == "init" ]; then
    echo "Initialized Django Project."
    python manage.py migrate
    python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('$DJANGO_ADMIN_USERNAME', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD')"
    python manage.py collectstatic --noinput
elif [ "$1" == "migrate" ]; then
    echo "Migrate Django Project."
    python manage.py migrate
    python manage.py collectstatic --noinput
else
    echo "init.sh require arg e.g. init or migrate"
fi
