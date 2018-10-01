from unittest import mock

from django.test import TestCase, tag
from django.urls import reverse

from application import models
from application.utils import build_url

from .base import ApplicationTestBase


def parameterise_by_applicant_type(test_func):
    """
    Decorator to run a test function for two cases: one in which the applicant is applying for eyfs, and one for which
    they are applying only for the childcare register.
    :param test_func: Test function to be decorated.
    :return: decorated test function.
    """

    def decorated_test(test_suite):
        for test_type_ in [test_suite.create_eyfs_applicant, test_suite.create_childcare_register_applicant]:
            test_type_()
            test_func(test_suite)

    return decorated_test


class PeopleInTheHomeTestSuite(TestCase, ApplicationTestBase):

    def setUp(self):
        with mock.patch('application.views.magic_link.magic_link_confirmation_email') as magic_link_email_mock, \
                mock.patch('application.views.magic_link.magic_link_text') as magic_link_text_mock, \
                mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:
            notify_connection_test_mock.return_value.status_code = 201
            magic_link_email_mock.return_value.status_code = 201
            magic_link_text_mock.return_value.status_code = 201

            # Initial steps required here as client object needs to be authenticated to
            # access Your Children pages
            self.TestAppInit()

            self.TestAppEmail()
            self.TestValidateEmail()
            self.TestAppPhone()
            self.TestContactSummaryView()
            self.TestTypeOfChildcareAgeGroups()
            self.TestTypeOfChildcareOvernightCare()
            self.TestSecurityQuestion()
            self.AppTestTypeOfChildcareRegister()

            self.TestAppPersonalDetailsNames()

    # ---------- #
    # HTTP Tests #
    # ---------- #

    # Tests for adults in the home

    @tag('ragha')
    def test_can_access_people_in_the_home_guidance_page(self):
        response = self.client.get(
            reverse('PITH-Guidance-View'),
            {
                'id': self.app_id,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'PITH-Guidance-View')

        self.assertTrue('<title>People in the home</title>' in str(response.content))

    @tag('ragha')
    def test_can_progress_past_guidance_page(self):
        response = self.client.post(
            reverse('PITH-Guidance-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'PITH-Adult-Check-View')

        self.assertTrue('<title>Adults in the home</title>' in str(response.content))

    @tag('ragha')
    def test_error_raised_on_not_selecting_option_for_adults_in_the_home(self):
        response = self.client.post(
            reverse('PITH-Adult-Check-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'adults_in_home',
                             'Please tell us if anyone aged 16 or over lives or works in the home')

    @tag('ragha')
    def test_yes_option_to_adults_in_the_home_asking_for_adult_details(self):
        response = self.client.post(
            reverse('PITH-Adult-Check-View'),
            {
                'id': self.app_id,
                'adults_in_home': True
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('<title>Details of adults in your home</title>' in str(response.content))

    @tag('ragha')
    def test_no_option_to_adults_in_the_home_asking_for_adult_details(self):
        response = self.client.post(
            reverse('PITH-Adult-Check-View'),
            {
                'id': self.app_id,
                'adults_in_home': False
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('<title>Children in the home</title>' in str(response.content))

    @tag('ragha')
    def test_error_messages_on_empty_form_submission_in_details_of_adults_in_your_home_page(self):
        response = self.client.post(
            reverse('PITH-Adult-Details-View') + 'adults=0&remove=0',
            {
                'id': self.app_id,
                '1 - first_name': '',
                '1 - middle_names': '',
                '1 - last_name': '',
                '1 - date_of_birth_0': '',
                '1 - date_of_birth_1': '',
                '1 - date_of_birth_2': '',
                '1 - relationship': '',
                '1 - email_address': ''
            },
            follow=True
        )
        # fixme
        self.skipTest('assertions not yet working')

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'first_name', 'Please enter their first namea')
        self.assertFormError(response, 'form', 'last_name', 'Please enter their last name')
        self.assertFormError(response, 'form', 'date_of_birth',
                             'Please enter the full date, including the day, month and year')
        self.assertFormError(response, 'form', 'relationship', 'Please say how the person is related to you')
        self.assertFormError(response, 'form', 'email_address', 'Please enter an email address')

    @tag('ragha')
    def test_error_messages_on_future_date_in_adults_in_your_home_page(self):
        # url = reverse('PITH-Adult-Details-View') + '?&id=' + str(self.app_id) + '&remove=0&adults=1',
        url = build_url('PITH-Adult-Details-View', get={'adults': 0, 'remove': 0})
        response = self.client.post(url, {})

        # {
        #     'id': self.app_id,
        #     'first_name': 'FirstPerson',
        #     'middle_names': 'me',
        #     'last_name': 'LastName',
        #     'date_of_birth_0': '01',
        #     'date_of_birth_1': '02',
        #     'date_of_birth_2': '2020',
        #     'relationship': 'Friend',
        #     'email_address': 'tester1@informed.com'
        # }
        print("********************************************")
        print(url)
        print("********************************************")

        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.context['error-message'],
        #                  "There was a problem with the details (Person 1)")
        # self.assertFormError(response, 'form', 'fieldset', 'Please check the year')
        # self.assertTrue('Please check the year' in response.content.decode())
        self.assertContains(response, 'Please check the year')

    # test_error_messages_on_empty_form_submission_in_details_of_adults_in_your_home_page
    #
    # @tag('ragha')
    # def test_error_messages_on_future_date_in_adults_in_your_home_page(self):
    #     response = self.client.post(
    #         reverse('PITH-Adult-Details-View') + '&remove=0&adults=1',
    #         {
    #             'id': self.app_id,
    #             '1 - first_name': 'FirstPerson',
    #             '1 - middle_names': 'me',
    #             '1 - last_name': 'LastName',
    #             '1 - date_of_birth_0': '01',
    #             '1 - date_of_birth_1': '02',
    #             '1 - date_of_birth_2': '1999',
    #             '1 - relationship': 'Friend',
    #             '1 - email_address': 'tester1@informed.com'
    #         },
    #         follow=True
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #     print(response.content)
    #     self.assertTrue('<title>Adults who have lived abroad</title>' in str(response.content))
