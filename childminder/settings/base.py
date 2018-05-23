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
SMS_EXPIRY = 1
EMAIL_EXPIRY = 1

# Visa Validation
VISA_VALIDATION = os.environ.get('VISA_VALIDATION') == 'True'

# Base URL of notify gateway
NOTIFY_URL = os.environ.get('APP_NOTIFY_URL')

# Base URL of payment gateway
PAYMENT_URL = os.environ.get('APP_PAYMENT_URL')

# Base URL of addressing-service gateway
ADDRESSING_URL = os.environ.get('APP_ADDRESSING_URL')

PUBLIC_APPLICATION_URL = os.environ.get('PUBLIC_APPLICATION_URL')

EXECUTING_AS_TEST = os.environ.get('EXECUTING_AS_TEST')

TEST_NOTIFY_CONNECTION = True

# INSTALLED DJANGO APPLICATIONS

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
                "application.middleware.hide_costs_link",
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

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
    r'^' + URL_PREFIX + '/new-code/.*$',
    r'^' + URL_PREFIX + '/code-expired/$',
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
    r'^' + URL_PREFIX + '/health-check/(?P<id>[\w-]+)/$'
)

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

GOOGLE_ANALYTICS = {
    'google_analytics_id': "UA-114456515-1"
}

# Export Settings variables DEBUG to templates context
SETTINGS_EXPORT = [
    'DEBUG'
]

# Regex Validation Strings
REGEX = {
    "EMAIL": "^([a-zA-Z0-9_\-\.']+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$",
    "MOBILE": "^(07\d{8,12}|447\d{7,11}|00447\d{7,11}|\+447\d{7,11})$",
    "PHONE": "^(0\d{8,12}|44\d{7,11}|0044\d{7,11}|\+44\d{7,11})$",
    "POSTCODE_UPPERCASE": "^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$",
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
