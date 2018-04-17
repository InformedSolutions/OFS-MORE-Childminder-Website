import socket
import os

from .base import *

DEBUG = True

PUBLIC_APPLICATION_URL = 'http://localhost:8000'

INTERNAL_IPS = ["127.0.0.1", ]

# Workdaround for docker
INTERNAL_IPS += [socket.gethostbyname(socket.gethostname())[:-1] + '1']

ALLOWED_HOSTS = ['*']

DEV_APPS = [
    'debug_toolbar',
    'django_extensions'
]

MIDDLEWARE_DEV = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'ofsted'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('POSTGRES_HOST', '130.130.52.132'),
        'PORT': os.environ.get('POSTGRES_PORT', '5462')
    }
}

MIDDLEWARE = MIDDLEWARE + MIDDLEWARE_DEV
INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

SECRET_KEY = '-asdasdsad322432maq#j23432*&(*&DASl6#mhak%8rbh$px8e&9c6b9@c7df=m'
