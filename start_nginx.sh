#!/bin/bash
sed -i -e 's/user www-data;//g' /etc/nginx/nginx.conf && \
sed -i -e 's/listen 80;/'"listen $PORT;"'/g' /etc/nginx/nginx.conf && \
sed -i -e 's/back/127.0.0.1/g' /etc/nginx/nginx.conf && \

until ping 127.0.0.1 -c 1 ; do
    echo 'waiting for django to be connectable...'
    sleep 5
done
nginx -g 'daemon off;'