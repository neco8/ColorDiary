FROM python:3.9

RUN apt-get update -qq && \
    apt-get install -y \
    sudo \
    default-mysql-client

RUN sed -i /etc/sudoers -re 's/^%sudo.*/%sudo ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^root.*/root ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^#includedir.*/## **Removed the include directive** ##"/g' && \
    echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
    
WORKDIR /code

COPY ./requirements.txt /code/

RUN python -m pip install -r requirements.txt

RUN mkdir -p color_diary_project
COPY ./color_diary_project/ /code/color_diary_project
COPY ./start_django.sh /code/

USER www-data
