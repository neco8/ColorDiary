#!/bin/bash

until mysqladmin ping -h $DB_HOST --silent; do
    echo 'waiting for mysqld to be connectable...'
    sleep 2
done

groupadd -g $UID -o django
useradd -u $UID -g $UID -o django
su django

sudo -E python color_diary_project/manage.py makemigrations
sudo -E python color_diary_project/manage.py migrate
cd color_diary_project
sudo -E python -m gunicorn --bind 127.0.0.1:8000 color_diary_project.wsgi