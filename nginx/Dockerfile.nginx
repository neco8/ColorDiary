FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx

RUN mkdir -p /var/www/
RUN chown www-data:www-data -R /var/www

ENTRYPOINT nginx -g 'daemon off;'