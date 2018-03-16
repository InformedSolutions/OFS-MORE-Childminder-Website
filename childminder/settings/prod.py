from .base import *

# You should never enable this in production, even if it's temporarily
# All INSTALLED_APPS in django relies on this variable, like google-analytics app.
DEBUG = False

ALLOWED_HOSTS = ['*']
PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL')

# Base URL of notify gateway
NOTIFY_URL = "http://" + os.environ.get('APP_NOTIFY_URL') + "/notify-gateway"

# Base URL of payment gateway
PAYMENT_URL = "http://" + os.environ.get('APP_PAYMENT_URL') + "/payment-gateway"

# Base URL of arc-service gateway
ADDRESSING_URL = "http://" + os.environ.get('APP_ADDRESSING_URL') + "/addressing-service"

# Visa Validation
VISA_VALIDATION = True

PROD_APPS = [
    'whitenoise',
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROD_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'ofsted'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('POSTGRES_HOST', 'ofsted-postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432')
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-r&u(maq#j68ngj=_ch#l6#mhak%8rbh$px8e&9c6b9@c7df=m'

# Automatic Django logging at the INFO level (i.e everything the comes to the console when ran locally)
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
    'django.server': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'maxBytes': 1 * 1024 * 1024,
        'filename': 'logs/output.log',
        'formatter': 'console',
        'maxBytes': 1 * 1024 * 1024,
        'backupCount': '30'
    },
   },
   'loggers': {
     'django.server': {
       'handlers': ['django.server'],
         'level': 'INFO',
           'propagate': True,
      },
    },
}