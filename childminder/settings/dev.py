import socket

from .base import *

DEBUG = True

EXECUTING_AS_TEST = 'True'

SESSION_COOKIE_SECURE = False

PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL', 'http://localhost:8000/childminder')

PAYMENT_URL = os.environ.get('APP_PAYMENT_URL', 'http://localhost:8001/payment-gateway')

ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL', 'http://localhost:8002/addressing-service')

NOTIFY_URL = os.environ.get('APP_NOTIFY_URL', 'http://localhost:8003/notify-gateway')

# Base URL of integration adapter for interfacing with NOO
INTEGRATION_ADAPTER_URL = os.environ.get('APP_INTEGRATION_ADAPTER', 'http://localhost:8004/integration-adapter')

INTERNAL_IPS = ["127.0.0.1", "localhost"]

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

# AWS SQS keys
AWS_SQS_ACCESS_KEY_ID = os.environ.get('AWS_SQS_ACCESS_KEY_ID')
AWS_SQS_SECRET_ACCESS_KEY = os.environ.get('AWS_SQS_SECRET_ACCESS_KEY')

SQS_QUEUE_PREFIX = os.environ.get('SQS_QUEUE_PREFIX', 'DEV')
PAYMENT_NOTIFICATIONS_QUEUE_NAME = SQS_QUEUE_PREFIX + '_PAYMENT_NOTIFICATIONS'

# The prefix added before a URN for finance system reconciliation purposes
PAYMENT_URN_PREFIX = 'EY'

# The prefix used to distinguish Worldpay payment entries for MORE
PAYMENT_REFERENCE_PREFIX = 'MO'
