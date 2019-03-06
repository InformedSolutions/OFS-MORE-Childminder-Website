from .base import *

# You should never enable this in production, even if it's temporarily
# All INSTALLED_APPS in django relies on this variable, like google-analytics app.
DEBUG = False

ALLOWED_HOSTS = ['*']

PROD_APPS = [
    'whitenoise',
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROD_APPS + PROJECT_APPS

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': from_env('POSTGRES_DB', 'postgres'),
        'USER': from_env('POSTGRES_USER', 'ofsted'),
        'PASSWORD': from_env('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': from_env('POSTGRES_HOST', 'ofsted-postgres'),
        'PORT': from_env('POSTGRES_PORT', '5432')
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = from_env('SECRET_KEY')

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
            'backupCount': 30
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
