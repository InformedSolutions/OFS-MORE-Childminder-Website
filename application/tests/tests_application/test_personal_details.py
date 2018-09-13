"""
Functional tests for the Your personal details task

NOTE! If it throws you status 200, that means form submission is failing!

"""
from django.test import TestCase, Client, modify_settings, tag
from .base import ApplicationTestBase
from django.urls import reverse

from ...models import Application


@modify_settings(MIDDLEWARE={
    'remove': [
        'application.middleware.CustomAuthenticationHandler'
    ]
})
class NoMiddlewareTestCase(TestCase):
    pass


class PersonalDetailsTests(NoMiddlewareTestCase):

    def setUp(self):
        self.client = Client()
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        # Set the following variables when inheriting
        self.view_url_name = None
        self.correct_url = None

        Application.objects.create(application_id=self.application_id)

    @tag('http')
    def set_own_children_to_true(self):
        """
        Test to assert that the own_children attribute in the Application table is set to True when the applicant says
        they have own children
        """

        # Build env
        application = Application.objects.get(application_id=self.application_id)
        form_data = {
            'id': self.application_id,
            'own_children': 'Yes'
        }

        self.client.post(reverse('Personal-Details-Your-Own-Children-View') + '?id=' + self.application_id, form_data)

        self.assertTrue(application.own_children)

        # Tear down env
        application.delete()
