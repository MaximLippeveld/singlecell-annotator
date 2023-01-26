import os

from .base import *

DEBUG=True

ALLOWED_HOSTS = ['0.0.0.0','localhost', '127.0.0.1']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8ex1spmt%_#n!w_rib8krt3ez3^8fr@=&b)e6&42&$an+)g8#v'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
    }
}

NUM_PER_SET = 5
