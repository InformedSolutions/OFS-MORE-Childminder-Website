from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from .base import ApplicationTestBase
from django.urls import reverse


class AdultInHomeTests(TestCase, ApplicationTestBase):
    """
    Test class for assuring adults in home functionality.
    """
    def setUp(self):
        # Load fixtures to populate a test application
        call_command("loaddata", "adult_in_home.json", verbosity=0)

    def authenticate_client(self):
        return self.client.get(
            reverse('Health-Check-Authentication', args={'1318336'}),
            follow=True
        )

    def test_can_access_healthcheck_pages_as_additional_adult(self):
        # Note login token taken from adult_in_home dump file
        response = self.authenticate_client()

        self.assertEqual(response.status_code, 200)

        # Assert user taken is taken to the date of birth validation page
        self.assertTrue('We need to ask all adults in the home about their health '
                        'to make sure the home is safe for children.' in str(response.content))

    def test_incorrect_additional_adult_dob_produces_raises_error(self):

        self.authenticate_client()

        endpoint = reverse('Health-Check-Dob') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        # Invoke login command to create session
        response = self.client.post(
            endpoint,
            {
                'date_of_birth_0': '26',
                'date_of_birth_1': '1',
                'date_of_birth_2': '1990',
                'times_wrong': '0',
            }
        )

        self.assertEqual(response.status_code, 200)

        # Check an error has been returned against the invalid DOB
        self.assertIsNotNone(response.context['errors']['date_of_birth'])

    def test_can_progress_with_valid_additional_adult_dob(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Dob') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        # Note valid DOB is taken from loaded fixture
        response = self.client.post(
            endpoint,
            {
                'date_of_birth_0': '6',
                'date_of_birth_1': '12',
                'date_of_birth_2': '1991',
                'times_wrong': '0',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is progressed to guidance page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Guidance')

    def test_can_get_current_illnesses(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Current') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.get(
            endpoint,
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is progressed to guidance page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Current')

    def test_no_response_to_current_illnesses_raises_error(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Current') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Current')

        # Check error has been raised against question about whether user is currently ill
        self.assertIsNotNone(response.context['errors']['currently_ill'])

    def test_can_submit_current_illnesses_with_responses(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Current') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'currently_ill': 'True',
                'illness_details': 'Test'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious-Start')

    def test_no_response_to_serious_illnesses_raises_error(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious-Start') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        # Post with an empty body to emulate no response being provided
        response = self.client.post(
            endpoint,
            {
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious-Start')

        # Check error has been raised against question about whether user is currently ill
        self.assertIsNotNone(response.context['errors']['has_illnesses'])

    def test_saying_yes_to_serious_illnesses_prompts_details(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious-Start') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'has_illnesses': 'True'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to details page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious')

    def test_no_response_to_serious_illnesses_details_raises_error(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious')

        # Check errors are raised against mandatory fields
        self.assertIsNotNone(response.context['errors']['description'])
        self.assertIsNotNone(response.context['errors']['start_date'])
        self.assertIsNotNone(response.context['errors']['end_date'])

    def test_responding_to_serious_illnesses_details_redirects_to_summary_of_details(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'description': 'Test serious illness',
                'start_date_0': '26',
                'start_date_1': '1',
                'start_date_2': '2017',
                'end_date_0': '26',
                'end_date_1': '2',
                'end_date_2': '2018',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious-More')

    def test_can_add_additional_serious_illness(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious-More') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'more_illnesses': 'True'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to serious illness detail page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Serious')

    def test_saying_no_to_additional_serious_illness_routes_to_hospital_admissions(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Serious-More') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'more_illnesses': 'False'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to serious illness detail page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Hospital-Start')

    def test_no_response_to_hospital_admissions_raises_error(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Hospital-Start') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Hospital-Start')

        # Check errors are raised against mandatory fields
        self.assertIsNotNone(response.context['errors']['has_illnesses'])

    def test_saying_yes_to_hospital_admissions_prompts_details(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Hospital-Start') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'has_illnesses': 'True'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to details page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Hospital')

    def test_no_response_to_hospital_admission_details_raises_error(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Hospital') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Hospital')

        # Check errors are raised against mandatory fields
        # Check errors are raised against mandatory fields
        self.assertIsNotNone(response.context['errors']['description'])
        self.assertIsNotNone(response.context['errors']['start_date'])
        self.assertIsNotNone(response.context['errors']['end_date'])

    def test_responding_to_hospital_admission_details_redirects_to_summary_of_details(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Hospital') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'description': 'Test serious illness',
                'start_date_0': '26',
                'start_date_1': '1',
                'start_date_2': '2017',
                'end_date_0': '26',
                'end_date_1': '2',
                'end_date_2': '2018',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to same page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Hospital-More')

    def test_saying_no_to_hospital_admissions_redirect_to_check_answers(self):
        self.authenticate_client()

        endpoint = reverse('Health-Check-Hospital-Start') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

        response = self.client.post(
            endpoint,
            {
                'has_illnesses': 'False'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is returned to details page
        self.assertEqual(response.resolver_match.view_name, 'Health-Check-Summary')

    def test_can_get_confirmation_page(self):
        with mock.patch('application.views.magic_link.magic_link_confirmation_email') as magic_link_email_mock, \
                mock.patch('application.views.magic_link.magic_link_text') as magic_link_text_mock, \
                mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:
            notify_connection_test_mock.return_value.status_code = 201
            magic_link_email_mock.return_value.status_code = 201
            magic_link_text_mock.return_value.status_code = 201

            self.authenticate_client()

            endpoint = reverse('Health-Check-Thank-You') + '?person_id=a82295f2-d3a1-4ccc-85f6-ac3acc028265'

            response = self.client.get(
                endpoint,
                follow=True
            )

            self.assertEqual(response.status_code, 200)

            # Check user is returned to details page
            self.assertEqual(response.resolver_match.view_name, 'Health-Check-Thank-You')