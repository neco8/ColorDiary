from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

try:
    from .heroku import *
except:
    pass