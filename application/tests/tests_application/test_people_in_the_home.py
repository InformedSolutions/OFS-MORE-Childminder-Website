from django.test import modify_settings, TestCase


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class PeopleInTheHomeTestSuite(TestCase):
    pass
