import datetime

from django.test import TestCase, modify_settings
from uuid import UUID

from django.urls import reverse

from ...models import ChildcareType, Application
from django.test import Client


class TestChildcareTypeLogic(TestCase):

    test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
    test_childcare_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
    test_application = None
    test_childcare_record = None

    # Clients for HTTP level tests
    client = Client()

    def setUp(self):
        # Clear-down any previous instances prior to executing test
        ChildcareType.objects.filter(application_id=self.test_application_id).delete()
        Application.objects.filter(application_id=self.test_application_id).delete()

        # Instantiate new test objects
        self.test_application = Application.objects.create(
            application_id=(UUID(self.test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='NOT_STARTED',
            first_aid_training_status='NOT_STARTED',
            childcare_training_status='NOT_STARTED',
            criminal_record_check_status='NOT_STARTED',
            health_status='NOT_STARTED',
            references_status='NOT_STARTED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )

        self.test_childcare_record = ChildcareType.objects.create(
            childcare_id=(UUID(self.test_childcare_id)),
            application_id=Application.objects.get(application_id=self.test_application_id),
            zero_to_five='False',
            five_to_eight='False',
            eight_plus='False'
        )

    def retrieve_test_chilcare_record(self):
        """
        Helper method to retrieve stub childcare record for testing purposes
        """
        return ChildcareType.objects.filter(application_id=self.test_application_id)

    def test_logic_to_create_new_record(self):
        assert (ChildcareType.objects.filter(application_id=self.test_application_id).count() == 1)

    # HTTP web tier tests

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_eligible_to_apply_for_ages_zero_to_five_only(self):
        """
        Test to assert childminder can apply using service when looking after children aged only between zero and five
        """
        data = {
            'id': self.test_application_id,
            'type_of_childcare': ['0-5']
        }

        response = self.client.post(
            reverse('Type-Of-Childcare-Age-Groups-View'),
            data,
            follow=True)

        expected_redirect_url = reverse('Type-Of-Childcare-Register-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)
        self.assertContains(response, 'Early Years Register')

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_eligible_to_apply_for_ages_zero_to_five_and_five_to_eight(self):
        """
        Test to assert childminder can apply using service when looking after children aged only between zero and five
        and five to eight
        """
        data = {
            'id': self.test_application_id,
            'type_of_childcare': ['0-5', '5-8']
        }

        response = self.client.post(
            reverse('Type-Of-Childcare-Age-Groups-View'),
            data,
            follow=True)

        expected_redirect_url = reverse('Type-Of-Childcare-Register-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)
        self.assertContains(response, 'Early Years and Childcare Register (compulsory part)')

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_eligible_to_apply_for_all_ages(self):
        """
        Test to assert childminder can apply using service for children of all ages
        """
        data = {
            'id': self.test_application_id,
            'type_of_childcare': ['0-5', '5-8', '8over']
        }

        response = self.client.post(
            reverse('Type-Of-Childcare-Age-Groups-View'),
            data,
            follow=True)

        expected_redirect_url = reverse('Type-Of-Childcare-Register-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)
        self.assertContains(response, 'Early Years and Childcare Register (both parts)')

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_eligible_to_apply_for_ages_five_to_eight_and_above_only(self):
        """
        Test to assert childminder can not apply using service when looking after children aged five and above only
        """
        data = {
            'id': self.test_application_id,
            'type_of_childcare': ['5-8', '8over']
        }

        response = self.client.post(
            reverse('Type-Of-Childcare-Age-Groups-View'),
            data,
            follow=True)

        expected_redirect_url = reverse('Type-Of-Childcare-Register-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_eligible_to_apply_for_ages_eight_and_above_only(self):
        """
        Test to assert childminder can not apply using service when looking after children aged eight and above only
        """
        data = {
            'id': self.test_application_id,
            'type_of_childcare': ['8over']
        }

        response = self.client.post(
            reverse('Type-Of-Childcare-Age-Groups-View'),
            data,
            follow=True)

        expected_redirect_url = reverse('Type-Of-Childcare-Register-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    # Routing checks for accessing other parts of application

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_can_access_personal_details_task_if_personal_details_not_started(self):
        """
        Test to assert a user is progressed to the personal details task on the premise they are
        eligible to apply given childcare ages
        """
        self.test_childcare_record.zero_to_five = True
        self.test_childcare_record.five_to_eight = False
        self.test_childcare_record.eight_plus = False
        self.test_childcare_record.save()

        self.test_application.personal_details_status = 'NOT_STARTED'
        self.test_application.save()

        response = self.client.get(
            reverse('Task-List-View') + '?id=' + self.test_application_id,
            follow=True)

        expected_redirect_url = reverse('Personal-Details-Name-View') + '?id=' + self.test_application_id

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_can_access_task_list_if_eligible_based_on_childcare_ages_and_personal_details_complete(self):
        """
        Test to assert a user can continue to access the task list if they are eligible to apply
        based on the age of children they will be looking after once they have completed
        the personal details task.
        """
        self.test_childcare_record.zero_to_five = True
        self.test_childcare_record.five_to_eight = False
        self.test_childcare_record.eight_plus = False
        self.test_childcare_record.save()

        self.test_application.personal_details_status = 'COMPLETE'
        self.test_application.save()

        response = self.client.get(
            reverse('Task-List-View') + '?id=' + self.test_application_id)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fill in the sections below to apply.')

