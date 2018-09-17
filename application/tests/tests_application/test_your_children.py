"""
Tests targetting the payment process
"""

from unittest import mock

from django.test import TestCase, tag
from django.urls import reverse, resolve

from .base import ApplicationTestBase
from ...payment_service import *
from ...models import Payment, Application, Child


class YourChildrenTests(TestCase, ApplicationTestBase):

    test_1_forename = 'TEST FIRST FORENAME'
    test_2_forename = 'TEST SECOND FORENAME'

    def setUp(self):
        with mock.patch('application.notify.send_email') as notify_mock, \
            mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:

            notify_connection_test_mock.return_value.status_code = 201
            notify_mock.return_value.status_code = 201

            # Initial steps required here as client object needs to be authenticated to
            # access payment pages
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

    def __submit_children_details(self):
        return self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': self.test_1_forename,
                '1-middle_names': 'TEST FIRST MIDDLE NAMES',
                '1-last_name': 'TEST FIRST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '2015',
                '2-first_name': self.test_2_forename,
                '2-middle_names': 'TEST SECOND MIDDLE NAMES',
                '2-last_name': 'TEST SECOND LAST NAME',
                '2-date_of_birth_0': '17',
                '2-date_of_birth_1': '2',
                '2-date_of_birth_2': '2013',
                'children': '2',
                'submit': ''
            },
            follow=True
        )

    @tag('http')
    def test_can_access_own_children_guidance_page(self):
        response = self.client.get(
            reverse('Your-Children-Guidance-View'),
            {
                'id': self.app_id,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Guidance-View')

        self.assertTrue('<title>Your children</title>' in str(response.content))

    @tag('http')
    def test_can_progress_past_guidance_page(self):
        response = self.client.post(
            reverse('Your-Children-Guidance-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')

        self.assertTrue('<title>Details of your children</title>' in str(response.content))

    @tag('http')
    def test_can_submit_details_of_single_child(self):
        test_forename = 'TEST FORENAME'

        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': test_forename,
                '1-middle_names': 'TEST MIDDLE NAMES',
                '1-last_name': 'TEST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '2015',
                'children': '1',
                'submit': ''
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Living-With-You-View')
        
        child_count = Child.objects.filter(application_id=self.app_id).count()

        # Ensure just the one child has been added to the application
        self.assertEqual(child_count, 1)

        # Check child is same as submitted value
        single_child_record = Child.objects.filter(application_id=self.app_id).first()
        self.assertEqual(single_child_record.first_name, test_forename)

    def test_can_retrieve_previously_entered_child_details(self):
        test_forename = 'TEST FORENAME'

        self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': test_forename,
                '1-middle_names': 'TEST MIDDLE NAMES',
                '1-last_name': 'TEST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '2015',
                'children': '1',
                'submit': ''
            },
            follow=True
        )

        get_response = self.client.get(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.resolver_match.view_name, 'Your-Children-Details-View')
        self.assertTrue(test_forename in str(get_response.content))

    @tag('http')
    def test_error_raised_if_child_dob_makes_them_over_16(self):
        test_forename = 'TEST FORENAME'

        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': test_forename,
                '1-middle_names': 'TEST MIDDLE NAMES',
                '1-last_name': 'TEST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '1990',
                'children': '1',
                'submit': ''
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')
        self.assertIsNotNone(response.context['errors']['date_of_birth'])

    def test_can_add_more_children(self):
        test_forename = 'TEST FORENAME'

        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': test_forename,
                '1-middle_names': 'TEST MIDDLE NAMES',
                '1-last_name': 'TEST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '2015',
                'children': '1',
                'add_person': ''
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # User should be redirected back to the same page
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')

        # Make sure placeholder was returned for child 2 details
        self.assertTrue('Child 2' in str(response.content))

    def test_can_remove_child(self):
        self.__submit_children_details()

        # Fetch record to pull ID of child
        second_child_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_2_forename).first()

        get_response = self.client.get(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                'children': '2'
            },
            follow=True
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertTrue(self.test_2_forename in str(get_response.content))

        get_removed_response = self.client.get(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                'children': '2',
                'remove': second_child_record.child,
            },
            follow=True
        )

        self.assertEqual(get_removed_response.status_code, 200)
        self.assertFalse(self.test_2_forename in str(get_removed_response.content))

    def test_child_names_shown_on_children_living_with_you_page(self):
        response = self.__submit_children_details()

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to page asking them which of their children live with them
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Living-With-You-View')

        child1_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_1_forename).first()
        child2_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_2_forename).first()

        # Check child names have been rendered
        self.assertTrue(child1_record.get_full_name() in str(response.content))
        self.assertTrue(child2_record.get_full_name() in str(response.content))

        # Also check none appears as an option in the presented checkboxes on the resulting page
        self.assertTrue('none' in str(response.content))

    def test_error_raised_on_children_living_with_childminder_page_if_mutually_exclusive_options_selected(self):
        self.__submit_children_details()

        response = self.client.post(
            reverse('Your-Children-Living-With-You-View'),
            {
                'id': self.app_id,
                'children_living_with_childminder_selection': ['1', '2', 'none'],
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to page asking them which of their children live with them
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Living-With-You-View')
        self.assertIsNotNone(response.context['errors']['children_living_with_childminder_selection'])

    def test_if_all_children_living_with_childminder_redirected_to_summary(self):
        self.__submit_children_details()

        response = self.client.post(
            reverse('Your-Children-Living-With-You-View'),
            {
                'id': self.app_id,
                'children_living_with_childminder_selection': ['1', '2'],
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to page asking them which of their children live with them
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Summary-View')

    def test_if_child_not_living_with_childminder_asked_for_address(self):
        response = self.__submit_children_details()

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to page asking them which of their children live with them
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Living-With-You-View')

        child1_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_1_forename).first()
        child2_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_2_forename).first()

        # Check child names have been rendered
        self.assertTrue(child1_record.get_full_name() in str(response.content))
        self.assertTrue(child2_record.get_full_name() in str(response.content))
