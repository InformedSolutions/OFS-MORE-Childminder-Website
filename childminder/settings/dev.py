import socket
import os

from .base import *

DEBUG = True

# Override default url for local dev
PUBLIC_APPLICATION_URL = 'http://localhost:8000/childminder'

INTERNAL_IPS = ["127.0.0.1", ]

# Workdaround for docker
INTERNAL_IPS += [socket.gethostbyname(socket.gethostname())[:-1] + '1']

ALLOWED_HOSTS = ['*']

TEST_NOTIFY_CONNECTION = False

DEV_APPS = [
    'debug_toolbar',
    'django_extensions'
]

MIDDLEWARE_DEV = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

URL_PREFIX = '/childminder'
STATIC_URL = URL_PREFIX + '/static/'

AUTHENTICATION_URL = URL_PREFIX + '/sign-in/'

AUTHENTICATION_EXEMPT_URLS = (
    r'^' + URL_PREFIX + '/$',
    r'^' + URL_PREFIX + '/account/account/$',
    r'^' + URL_PREFIX + '/account/email/$',
    r'^' + URL_PREFIX + '/security-question/$',
    r'^' + URL_PREFIX + '/email-sent/$',
    r'^' + URL_PREFIX + '/validate/.*$',
    r'^' + URL_PREFIX + '/code-resent/.*$',
    r'^' + URL_PREFIX + '/security-code/.*$',
    r'^' + URL_PREFIX + '/link-used/$',
    r'^' + URL_PREFIX + '/link-expired/$',
    r'^' + URL_PREFIX + '/new-code/.*$',
    r'^' + URL_PREFIX + '/djga/+',
    r'^' + URL_PREFIX + '/sign-in/',
    r'^' + URL_PREFIX + '/sign-in/check-email/',
    r'^' + URL_PREFIX + '/email-resent/',
    r'^' + URL_PREFIX + '/sign-in/new-application/',
    r'^' + URL_PREFIX + '/new-application/',
    r'^' + URL_PREFIX + '/new-application/check-email/',
    r'^' + URL_PREFIX + '/service-unavailable/',
    r'^' + URL_PREFIX + '/help-contact/',
    r'^' + URL_PREFIX + '/costs/',
    r'^' + URL_PREFIX + '/application-saved/$',
    r'^' + URL_PREFIX + '/health-check/(?P<id>[\w-]+)/$',
    r'^' + URL_PREFIX + '/feedback/',
    r'^' + URL_PREFIX + '/feedback-submitted/'
)

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
