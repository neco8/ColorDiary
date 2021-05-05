#!/bin/bash

until mysqladmin ping -h $DB_HOST --silent; do
    echo 'waiting for mysqld to be connectable...'
    sleep 2
done

sudo -E python color_diary_project/manage.py makemigrations
sudo -E python color_diary_project/manage.py migrate
sudo -E python color_diary_project/manage.py collectstatic --no-input
cd color_diary_project
sudo -E python -m gunicorn --bind 0.0.0.0:8000 color_diary_project.wsgi