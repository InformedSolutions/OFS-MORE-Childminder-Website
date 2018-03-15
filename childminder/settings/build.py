from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']
PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL')

INTERNAL_IPS = "127.0.0.1"

# Base URL of notify gateway
NOTIFY_URL = "http://" + os.environ.get('APP_NOTIFY_URL') + "/notify-gateway"

# Base URL of payment gateway
PAYMENT_URL = "http://" + os.environ.get('APP_PAYMENT_URL') + "/payment-gateway"

# Base URL of arc-service gateway
ADDRESSING_URL = "http://" + os.environ.get('APP_ADDRESSING_URL') + "/addressing-service"


# Visa Validation
VISA_VALIDATION = False

DEV_APPS = [
    'debug_toolbar'
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

SECRET_KEY = '-as82jskhad322432maq#j23432*&(*&DASl6#mhak%8rbh$px8e&9c6b9@c7df=m'
