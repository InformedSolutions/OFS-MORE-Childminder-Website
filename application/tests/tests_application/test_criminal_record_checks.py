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

class DBSTemplateViewTestCase(NoMiddlewareTestCase):

    def setUp(self):
        self.client = Client()
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        # Set the following variables when inheriting
        self.view_name = None
        self.correct_url = None

        Application.objects.create(application_id=self.application_id)

    def test_view_rendered_on_get(self):
        if self.view_name is not None:
            response = self.client.get(reverse(self.view_name)+'?id='+self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

    def test_redirect(self):
        if self.view_name is not None:
            response = self.client.post(reverse(self.view_name)+'?id='+self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 302)

    def test_redirect_to_correct_url(self):
        if self.view_name is not None and self.correct_url is not None:
            correct_url = reverse(self.correct_url)+'?id='+self.application_id
            response = self.client.post(reverse(self.view_name)+'?id='+self.application_id)
            print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
            self.assertTrue(response.url == correct_url)


class DBSGuidanceViewTests(DBSTemplateViewTestCase):

    def setUp(self):
        super().setUp()
        self.view_name = 'DBS-Guidance-View'
        self.correct_url = 'DBS-Type-View'


class DBSLivedAbroadViewTests(NoMiddlewareTestCase):

    #TODO -test

    def setUp(self):
        pass

    def test_view_rendered_on_get(self):
        pass

    def test_redirect_on_post(self):
        pass

    def test_redirect_on_post_to_correct_url(self):
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

class DBSGoodConductViewTests(DBSTemplateViewTestCase):

    def setUp(self):
        super().setUp()
        self.view_name = 'DBS-Good-Conduct-View'
        self.correct_url = 'DBS-Email-Certificates-View'

class DBSSendCertificateViewTests(DBSTemplateViewTestCase):

    def setUp(self):
        super().setUp()
        self.view_name = 'DBS-Email-Certificates-View'
        self.correct_url = ''
