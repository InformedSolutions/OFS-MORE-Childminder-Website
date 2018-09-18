"""
Tests targetting the Your Children task
"""

from unittest import mock

from django.test import TestCase, tag
from django.urls import reverse

from .base import ApplicationTestBase
from ...models import Child, ChildAddress


class YourChildrenTests(TestCase, ApplicationTestBase):

    test_1_forename = 'TEST FIRST FORENAME'
    test_2_forename = 'TEST SECOND FORENAME'

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

    def __submit_test_children_details(self):
        """
        Test helper method for setting up test children in the Your Children Task
        :return: HTTP response object from request library
        """

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

    def __submit_no_children_living_with_childminder_response(self):
        """
        Test helper method for marking that no children live with the childminder in the Your Children Task
        :return: HTTP response object from request library
        """

        return self.client.post(
            reverse('Your-Children-Living-With-You-View'),
            {
                'id': self.app_id,
                'children_living_with_childminder_selection': ['none'],
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
        self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': self.test_1_forename,
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
        self.assertTrue(self.test_1_forename in str(get_response.content))

    @tag('http')
    def test_error_raised_if_child_dob_makes_them_over_16(self):
        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': self.test_1_forename,
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

    @tag('http')
    def test_error_raised_if_additional_child_dob_makes_them_over_16(self):
        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': self.test_1_forename,
                '1-middle_names': 'TEST MIDDLE NAMES',
                '1-last_name': 'TEST LAST NAME',
                '1-date_of_birth_0': '22',
                '1-date_of_birth_1': '1',
                '1-date_of_birth_2': '2016',
                '2-first_name': self.test_2_forename,
                '2-middle_names': 'TEST SECOND MIDDLE NAMES',
                '2-last_name': 'TEST SECOND LAST NAME',
                '2-date_of_birth_0': '17',
                '2-date_of_birth_1': '2',
                '2-date_of_birth_2': '1990',
                'children': '2',
                'submit': ''
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')
        self.assertIsNotNone(response.context['errors']['date_of_birth'])

    @tag('http')
    def test_can_add_more_children(self):

        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
                '1-first_name': self.test_1_forename,
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

    @tag('http')
    def test_can_remove_child(self):
        self.__submit_test_children_details()

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

    @tag('http')
    def test_can_remove_first_child_when_multiple_present(self):
        self.__submit_test_children_details()

        # Fetch record to pull ID of child
        first_child_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_1_forename).first()

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
                'remove': first_child_record.child,
            },
            follow=True
        )

        self.assertEqual(get_removed_response.status_code, 200)
        self.assertFalse(self.test_1_forename in str(get_removed_response.content))

    @tag('http')
    def test_child_names_shown_on_children_living_with_you_page(self):
        response = self.__submit_test_children_details()

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

    @tag('http')
    def test_error_raised_on_children_living_with_childminder_page_if_mutually_exclusive_options_selected(self):
        self.__submit_test_children_details()

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

    @tag('http')
    def test_if_all_children_living_with_childminder_redirected_to_summary(self):
        self.__submit_test_children_details()

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

    @tag('http')
    def test_asked_for_first_child_address_if_not_living_with_any_children(self):
        self.__submit_test_children_details()
        response = self.__submit_no_children_living_with_childminder_response()

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to address capture page
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-View')

        # Check child 1's name is present in the response content
        self.assertTrue(self.test_1_forename in str(response.content))
        self.assertTrue('Find address' in str(response.content))

    @tag('http')
    def test_asked_for_second_child_address_if_living_with_first_children(self):
        self.__submit_test_children_details()

        response = self.client.post(
            reverse('Your-Children-Living-With-You-View'),
            {
                'id': self.app_id,
                'children_living_with_childminder_selection': ['1'],
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to address capture page
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-View')

        self.assertTrue(self.test_2_forename in str(response.content))
        self.assertTrue('Find address' in str(response.content))

    @tag('http')
    def test_error_raised_if_postcode_not_entered_on_child_address_lookup(self):
        self.__submit_test_children_details()

        response = self.client.post(
            reverse('Your-Children-Address-View'),
            {
                'id': self.app_id,
                'child': '1',
                'postcode-search': '',
                'postcode': '',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to address capture page
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-View')
        self.assertIsNotNone(response.context['errors']['postcode'])

    @tag('http')
    def test_address_lookup_renders_list(self):
        with mock.patch('application.address_helper.AddressHelper.create_address_lookup_list') as address_lookup_mock:

            address_lookup_response_object = [(None, 2), ('0', 'test address string')]

            address_lookup_mock.return_value = address_lookup_response_object
            self.__submit_test_children_details()

            response = self.client.post(
                reverse('Your-Children-Address-View'),
                {
                    'id': self.app_id,
                    'child': '1',
                    'postcode-search': '',
                    'postcode': 'WA14 4PA',
                },
                follow=True
            )

            self.assertEqual(response.status_code, 200)

            # Check user is redirected to address capture page
            self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-Select-View')
            self.assertTrue('Select address' in str(response.content))

    @tag('http')
    def test_posting_address_lookup_creates_record(self):
        with mock.patch('application.address_helper.AddressHelper.create_address_lookup_list') as address_lookup_mock, \
                mock.patch('application.address_helper.AddressHelper.get_posted_address') as full_address_mock:

            address_lookup_response_object = [(None, 2), ('0', 'test address string')]

            test_address_line_1 = 'Informed Solutions'

            full_address_mock_response_object = {
                'line1': test_address_line_1,
                'line2': ' OLD MARKET PLACE',
                'townOrCity': 'ALTRINCHAM',
                'postcode': 'WA14 4PA',
            }

            address_lookup_mock.return_value = address_lookup_response_object
            full_address_mock.return_value = full_address_mock_response_object

            self.__submit_test_children_details()

            self.__submit_no_children_living_with_childminder_response()

            self.client.post(
                reverse('Your-Children-Address-View'),
                {
                    'id': self.app_id,
                    'child': '1',
                    'postcode-search': '',
                    'postcode': 'WA14 4PA',
                },
                follow=True
            )

            postcode_selection_response = self.client.post(
                reverse('Your-Children-Address-Select-View'),
                {
                    'id': self.app_id,
                    'child': '1',
                    'address': 0,
                },
                follow=True
            )

            self.assertEqual(postcode_selection_response.status_code, 200)

            # Check user is redirected to capture page for second child
            self.assertEqual(postcode_selection_response.resolver_match.view_name, 'Your-Children-Address-View')

            # Check address was properly set
            child_address_record = ChildAddress.objects.get(application_id=self.app_id, child=1)
            self.assertEqual(child_address_record.street_line1, test_address_line_1)

            self.assertTrue(self.test_2_forename in str(postcode_selection_response.content))
            self.assertTrue('Find address' in str(postcode_selection_response.content))

    @tag('http')
    def test_can_render_manual_address_entry_page(self):
            self.__submit_test_children_details()
            self.__submit_no_children_living_with_childminder_response()

            response = self.client.get(
                reverse('Your-Children-Address-Manual-View'),
                {
                    'id': self.app_id,
                    'child': '1',
                },
                follow=True
            )

            self.assertEqual(response.status_code, 200)

            self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-Manual-View')
            self.assertTrue('Address line 1' in str(response.content))

    @tag('http')
    def test_manual_address_required_field_validation_applied(self):
        self.__submit_test_children_details()
        self.__submit_no_children_living_with_childminder_response()

        response = self.client.post(
            reverse('Your-Children-Address-Manual-View'),
            {
                'id': self.app_id,
                'child': '1',
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to capture page for second child
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-Manual-View')
        self.assertIsNotNone(response.context['errors']['street_line1'])
        self.assertIsNotNone(response.context['errors']['town'])
        self.assertIsNotNone(response.context['errors']['postcode'])

    @tag('http')
    def test_manual_address_required_field_validation_applied(self):
        self.__submit_test_children_details()
        self.__submit_no_children_living_with_childminder_response()

        response = self.client.post(
            reverse('Your-Children-Address-Manual-View'),
            {
                'id': self.app_id,
                'child': '1',
                'street_line1': 'Test Line 1',
                'town': 'Test Town',
                'postcode': 'testinvalidregex'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check validation has been triggered against postcode field only
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-Manual-View')
        self.assertIsNotNone(response.context['errors']['postcode'])

    @tag('http')
    def test_can_add_manual_address_for_child(self):
        self.__submit_test_children_details()
        self.__submit_no_children_living_with_childminder_response()

        test_address_line_1 = 'Test Line 1'
        test_address_line_2 = 'Test Line 2'
        test_town = 'Test Town'
        test_county = 'Test County'
        test_postcode = 'WA14 4PA'

        response = self.client.post(
            reverse('Your-Children-Address-Manual-View'),
            {
                'id': self.app_id,
                'child': '1',
                'street_line1': test_address_line_1,
                'street_line2': test_address_line_2,
                'town': test_town,
                'county': test_county,
                'postcode': test_postcode
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to capture page for second child
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Address-View')

    def test_if_child_not_living_with_childminder_asked_for_address(self):
        response = self.__submit_test_children_details()

        self.assertEqual(response.status_code, 200)

        # Check user is redirected to page asking them which of their children live with them
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Living-With-You-View')

        child1_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_1_forename).first()
        child2_record = Child.objects.filter(application_id=self.app_id, first_name=self.test_2_forename).first()

        # Check child names have been rendered
        self.assertTrue(child1_record.get_full_name() in str(response.content))
        self.assertTrue(child2_record.get_full_name() in str(response.content))
