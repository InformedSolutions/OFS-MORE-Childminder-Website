from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = "127.0.0.1"

DEV_APPS = [
    'debug_toolbar'
]

MIDDLEWARE_DEV = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

EMAIL_EXPIRY = 1

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': from_env('POSTGRES_DB', 'postgres'),
        'USER': from_env('POSTGRES_USER', 'ofsted'),
        'PASSWORD': from_env('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': from_env('POSTGRES_HOST', '130.130.52.132'),
        'PORT': from_env('POSTGRES_PORT', '5462')
    }
}


MIDDLEWARE = MIDDLEWARE + MIDDLEWARE_DEV
INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

SECRET_KEY = from_env('SECRET_KEY')
