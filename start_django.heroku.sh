#!/bin/bash

until mysqladmin ping -h $DB_HOST --silent; do
    echo 'waiting for mysqld to be connectable...'
    sleep 2
done

python color_diary_project/manage.py makemigrations
python color_diary_project/manage.py migrate
cd color_diary_project
python -m gunicorn --bind 0.0.0.0:$PORT color_diary_project.wsgi