from django.test import TestCase, modify_settings


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class NoMiddlewareTestCase(TestCase):
    """Removes the need for authentication when performing test requests"""
    pass
