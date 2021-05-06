import dj_database_url


ALLOWED_HOSTS.append('.herokuapp.com')

DATABASES['default'] = dj_database_url.config(conn_max_age=600)

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')