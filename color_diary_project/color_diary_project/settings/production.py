from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

try:
    from .heroku import *
except:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'back']