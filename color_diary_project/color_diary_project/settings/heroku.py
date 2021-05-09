import dj_database_url



ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'back', 'emotebook.herokuapp.com']

DATABASES['default'] = dj_database_url.config(conn_max_age=600)

MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')