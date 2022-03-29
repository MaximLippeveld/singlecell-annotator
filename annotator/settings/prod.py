import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = ['dev.maximl.be', 'localhost', '127.0.0.1', '193.190.80.30']

SECRET_KEY=os.environ["DJANGO_SECRET_KEY"]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/mnt', 'db.sqlite3'),
    }
}

NUM_PER_SET = 10
