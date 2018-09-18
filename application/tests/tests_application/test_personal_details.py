"""
Functional tests for the Your personal details task

NOTE! If it throws you status 200, that means form submission is failing!

"""
from django.test import TestCase, Client, modify_settings, tag
from django.urls import reverse

from ...models import Application


@modify_settings(MIDDLEWARE={
    'remove': [
        'application.middleware.CustomAuthenticationHandler'
    ]
})
class PersonalDetailsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        # Set the following variables when inheriting
        self.view_url_name = None
        self.correct_url = None

    @tag('http')
    def set_own_children_to_true(self):
        """
        Test to assert that the own_children attribute in the Application table is set to True when the applicant says
        they have own children
        """

        # Build env
        Application.objects.create(application_id=self.application_id)
        form_data = {
            'id': self.application_id,
            'own_children': 'True'
        }

        response = self.client.post(reverse('Personal-Details-Your-Own-Children-View') + '?id=' + self.application_id,
                                    form_data)

        application = Application.objects.get(application_id=self.application_id)

        self.assertTrue(response.status_code == 302)
        self.assertEqual(True, application.own_children)

        # Tear down env
        application.delete()

    @tag('http')
    def set_own_children_to_false(self):
        """
        Test to assert that the own_children attribute in the Application table is set to False when the applicant says
        they don't have own children
        """

        # Build env
        Application.objects.create(application_id=self.application_id)
        form_data = {
            'id': self.application_id,
            'own_children': 'False'
        }

        response = self.client.post(reverse('Personal-Details-Your-Own-Children-View') + '?id=' + self.application_id,
                                    form_data)

        application = Application.objects.get(application_id=self.application_id)

        self.assertTrue(response.status_code == 302)
        self.assertEqual(False, application.own_children)

        # Tear down env
        application.delete()

    @tag('http')
    def set_working_in_other_childminder_home_to_true(self):
        """
        Test to assert that the working_in_other_childminder_home attribute in the Application table is set to True
        when the applicant says they work in another childminder's home
        """

        # Build env
        Application.objects.create(application_id=self.application_id)
        form_data = {
            'id': self.application_id,
            'working_in_other_childminder_home': 'True'
        }

        response = self.client.post(
            reverse('Personal-Details-Childcare-Address-Details-View') + '?id=' + self.application_id, form_data)

        application = Application.objects.get(application_id=self.application_id)

        self.assertTrue(response.status_code == 302)
        self.assertEqual(True, application.working_in_other_childminder_home)

        # Tear down env
        application.delete()

    @tag('http')
    def set_working_in_other_childminder_home_to_false(self):
        """
        Test to assert that the working_in_other_childminder_home attribute in the Application table is set to False
        when the applicant says they don't work in another childminder's home
        """

        # Build env
        Application.objects.create(application_id=self.application_id)
        form_data = {
            'id': self.application_id,
            'working_in_other_childminder_home': 'False'
        }

        response = self.client.post(
            reverse('Personal-Details-Childcare-Address-Details-View') + '?id=' + self.application_id, form_data)

        application = Application.objects.get(application_id=self.application_id)

        self.assertTrue(response.status_code == 302)
        self.assertEqual(False, application.working_in_other_childminder_home)

        # Tear down env
        application.delete()
