import socket

from .base import *

DEBUG = True

PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL', 'http://localhost:8000/childminder')

ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL', 'http://localhost:8002/addressing-service')

NOTIFY_URL = os.environ.get('APP_NOTIFY_URL', 'http://localhost:8003/notify-gateway')

# Base URL of payment gateway
PAYMENT_URL = os.environ.get('APP_PAYMENT_URL', 'http://localhost:8001/payment-gateway')

INTERNAL_IPS = ["127.0.0.1", "localhost"]

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

EMAIL_EXPIRY = 1

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'ofs'),
        'USER': os.environ.get('POSTGRES_USER', 'ofs'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ofs'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432')
    }
}

MIDDLEWARE = MIDDLEWARE + MIDDLEWARE_DEV
INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + DEV_APPS + PROJECT_APPS

SECRET_KEY = '-asdasdsad322432maq#j23432*&(*&DASl6#mhak%8rbh$px8e&9c6b9@c7df=m'

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        },
  'handlers': {
    'file': {
        'level': 'DEBUG',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': 'logs/output.log',
        'formatter': 'console',
        'when': 'midnight',
        'backupCount': 10
    },
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler'
    },
   },
   'loggers': {
     '': {
       'handlers': ['console'],
         'level': 'DEBUG',
           'propagate': True,
      },
      'django.server': {
       'handlers': ['console'],
         'level': 'INFO',
           'propagate': True,
      },
    },
}