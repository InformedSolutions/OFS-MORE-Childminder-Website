from django.core.management import call_command
from django.test import TestCase, Client, modify_settings
from .base import ApplicationTestBase
from django.urls import reverse

from ...models import Application

@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
class NoMiddlewareTestCase(TestCase):
    pass

class DBSGuidanceViewTests(NoMiddlewareTestCase):

    # TODO -test

    def setUp(self):
        self.client = Client()
        self.view_name = 'DBS-Guidance-View'
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        Application.objects.create(application_id=self.application_id)

    def test_view_rendered_on_get(self):
        response = self.client.get(reverse(self.view_name)+'?id='+self.application_id)
        print('Returned a {0} response'.format(response.status_code))
        self.assertTrue(response.status_code == 200)

    def test_redirect(self):
        response = self.client.post(reverse(self.view_name)+'?id='+self.application_id)
        print('Returned a {0} response'.format(response.status_code))
        self.assertTrue(response.status_code == 302)

    def test_redirect_to_correct_url(self):
        correct_url = reverse('DBS-Type-View')+'?id='+self.application_id
        response = self.client.post(reverse(self.view_name)+'?id='+self.application_id)
        print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
        self.assertTrue(response.url == correct_url)

class DBSLivedAbroadViewTests(TestCase):

    #TODO -test

    def setUp(self):
        pass

    def test_view_rendered_on_get(self):
        pass

    def test_redirect_on_post(self):
        pass

    def test_redirect_on_post_to_correct_url(self):
        correct_url = reverse('DBS-Type-Page')
        pass

    def test_form_valid_callable(self):
        pass

    def test_radio_error_message(self):
        pass

    def test_radio_yes_redirect(self):
        pass

    def test_radio_yes_redirect_to_correct_url(self):
        pass

    def test_radio_no_redirect(self):
        pass

    def test_radio_no_redirect_to_correct_url(self):
        pass