"""
Django settings for childminder project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Server name for showing server that responded to request under load balancing conditions
SERVER_LABEL = os.environ.get('SERVER_LABEL')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Expiry period of Magic Link Emails and Texts in hours
SMS_EXPIRY = 24
EMAIL_EXPIRY = 24

# Cost of making application
APP_COST = 3500

# Visa Validation
VISA_VALIDATION = os.environ.get('VISA_VALIDATION') == 'True'

# Base URL of notify gateway
NOTIFY_URL = os.environ.get('APP_NOTIFY_URL')

# Base URL of payment gateway
PAYMENT_URL = os.environ.get('APP_PAYMENT_URL')

# Base URL of addressing-service gateway
ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL')

# Base URL of integration adapter for interfacing with NOO
INTEGRATION_ADAPTER_URL = os.environ.get('APP_INTEGRATION_ADAPTER')

# Base URL of the DBS check API
DBS_URL = os.environ.get('APP_DBS_URL')

PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL')

EXECUTING_AS_TEST = os.environ.get('EXECUTING_AS_TEST')

FEEDBACK_EMAIL = os.environ.get('FEEDBACK_EMAIL', 'tester@informed.com')

DOMAIN_URL = os.environ.get('APP_DOMAIN')


# AWS SQS keys
AWS_SQS_ACCESS_KEY_ID = os.environ.get('AWS_SQS_ACCESS_KEY_ID')
AWS_SQS_SECRET_ACCESS_KEY = os.environ.get('AWS_SQS_SECRET_ACCESS_KEY')

# Fees
CR_FEE = os.environ.get('CR_FEE')
EY_FEE = os.environ.get('EY_FEE')

TEST_NOTIFY_CONNECTION = True

# The prefix added before a URN for finance system reconciliation purposes
PAYMENT_URN_PREFIX = 'EY'

# The prefix used to distinguish Worldpay payment entries for MORE
PAYMENT_REFERENCE_PREFIX = 'MO'

PAYMENT_PROCESSING_ATTEMPTS = os.environ.get('PAYMENT_PROCESSING_ATTEMPTS', 10)
PAYMENT_STATUS_QUERY_INTERVAL_IN_SECONDS = os.environ.get('PAYMENT_STATUS_QUERY_INTERVAL_IN_SECONDS', 10)

PAYMENT_HTTP_REQUEST_TIMEOUT = 60

SQS_QUEUE_PREFIX = os.environ.get('SQS_QUEUE_PREFIX', 'DEV')

PAYMENT_NOTIFICATIONS_QUEUE_NAME = SQS_QUEUE_PREFIX + '_PAYMENT_NOTIFICATIONS'

GOOGLE_ANALYTICS = {
}

# INSTALLED DJANGO APPLICATIONS

URL_PREFIX = '/childminder'
STATIC_URL = URL_PREFIX + '/static/'

AUTHENTICATION_URL = URL_PREFIX + '/sign-in/'

AUTHENTICATION_EXEMPT_URLS = tuple(u.format(prefix=URL_PREFIX) for u in (
    # omitting the trailing $ will allow *any* url starting with that pattern
    r'^{prefix}/$',
    r'^{prefix}/account/account/$',  # unused?
    r'^{prefix}/account/email/$',  # unused?
    r'^{prefix}/security-question/$',  # unused?
    r'^{prefix}/email-sent/$',
    r'^{prefix}/validate/.*$',
    r'^{prefix}/code-resent/$',  # unused?
    r'^{prefix}/security-code/.*$',
    r'^{prefix}/link-used/$',
    r'^{prefix}/link-expired/$',
    r'^{prefix}/new-code/$',
    r'^{prefix}/djga/+',
    r'^{prefix}/sign-in/$',
    r'^{prefix}/sign-in/check-email/$',
    r'^{prefix}/sign-in/question/$',
    r'^{prefix}/sign-in/question/[\w-]+/$',
    r'^{prefix}/sign-in/new-application/$',
    r'^{prefix}/email-resent/$',
    r'^{prefix}/new-application/$',
    r'^{prefix}/new-application/email-sent/$',
    r'^{prefix}/your-location/$',
    r'^{prefix}/new-application/check-email/$',  # unused?
    r'^{prefix}/service-unavailable/$',
    r'^{prefix}/help-contact/$',
    r'^{prefix}/application-saved/$',
    r'^{prefix}/health-check/(?P<id>[\w-]+)/$',
    r'^{prefix}/feedback/$',
    r'^{prefix}/cookies/$',
    r'^{prefix}/feedback-submitted/$',
    r'^{prefix}/documents-needed/$',
    r'^{prefix}/home-ready/$',
    r'^{prefix}/prepare-interview/$'
))

BUILTIN_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'govuk_forms',
    'govuk_template',
    'govuk_template_base',
    'google_analytics',
    'timeline_logger'
]

PROJECT_APPS = [
    'application.apps.ApplicationConfig',
]

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'application.middleware.CustomAuthenticationHandler',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'childminder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                "application.middleware.globalise_authentication_flag",
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                "application.middleware.globalise_url_prefix",
                "application.middleware.globalise_server_name",
                "application.middleware.register_as_childminder_link_location",
                'govuk_template_base.context_processors.govuk_template_base',
            ],
        },
    },
]

WSGI_APPLICATION = 'childminder.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-GB'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Test outputs
TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = 'xmlrunner'

# Export Settings variables DEBUG to templates context
SETTINGS_EXPORT = [
    'DEBUG',
    'GOOGLE_ANALYTICS',
    'GOOGLE_TAG_MANAGER_ID'
]

# Regex Validation Strings
REGEX = {
    "EMAIL": "^([a-zA-Z0-9_\-\.']+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
    "MOBILE": "^(\+44|0044|0)[7][0-9]{9}$",
    "PHONE": "^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,"
             "5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?["
             "\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$",
    "INTERNATIONAL_PHONE": "^(\+|[0-9])[0-9]{5,20}$",
    "POSTCODE_UPPERCASE": "^[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][ABD-HJLNP-UW-Z]{2}$",
    "TITLE": "^[A-zÀ-ÿ- ']+$",
    "LAST_NAME": "^[A-zÀ-ÿ- ']+$",
    "MIDDLE_NAME": "^[A-zÀ-ÿ- ']+$",
    "FIRST_NAME": "^[A-zÀ-ÿ- ']+$",
    "TOWN": "^[A-Za-z- ]+$",
    "COUNTY": "^[A-Za-z- ]+$",
    "COUNTRY": "^[A-Za-z- ]+$",
    "VISA": "^4[0-9]{12}(?:[0-9]{3})?$",
    "MASTERCARD": "^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
    "MAESTRO": "^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$",
    "CARD_SECURITY_NUMBER": "^[0-9]{3,4}$"
}

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
        'level': 'INFO',
        'class': 'logging.StreamHandler'
    },
   },
   'loggers': {
     '': {
       'handlers': ['file', 'console'],
         'level': 'INFO',
           'propagate': True,
      },
      'django.server': {
       'handlers': ['file', 'console'],
         'level': 'INFO',
           'propagate': True,
      },
    },
}
