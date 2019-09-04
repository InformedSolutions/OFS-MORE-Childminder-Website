from django.test import tag
from django.urls import reverse

from application.tests import utils
from application import models


@tag('http')
class PersonalDetailsGuidancePageFunctionalTests(utils.NoMiddlewareTestCase):

    def test_can_render_guidance_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_redirects_to_name_page(self):
        self.skipTest('testNotImplemented')


@tag('http')
class NamePageFunctionalTests(utils.NoMiddlewareTestCase):

    def test_post_name_page(self):
        # Build env
        form_data = {
            'id': str(self.application_id),
            'title': 'Miss',
            'first_Name': 'Robin',
            'last_name': 'Hood',
        }

        response = self.client.post(reverse('Personal-Details-Name-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(302, response.status_code)
        self.assertEqual(application.first_name, 'Robin')
        self.assertEqual('Hood', application.last_name)
        self.assertEqual('Miss', application.title)

    def test_submit_returns_to_page_with_error_if_invalid(self):
        form_data = {
            'id': str(self.application_id),
            'title': '',
            'first_Name': 'Robin',
            'last_name': 'Hood',
        }

        response = self.client.post(reverse('Personal-Details-Name-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(200, response.status_code)



@tag('http')
class DOBPageFunctionalTests(utils.NoMiddlewareTestCase):

    def test_can_render_dob_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_returns_to_page_with_error_if_invalid(self):
        self.skipTest('testNotImplemented')

    def test_submit_redirects_to_home_address_search_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class HomeAddressPagesFunctionalTests(utils.NoMiddlewareTestCase):

    def test_can_render_search_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_search_returns_to_page_with_error_if_invalid(self):
        self.skipTest('testNotImplemented')

    def test_submit_search_redirects_to_select_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_manual_choice_redirects_to_manual_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_select_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_selection_returns_to_page_with_error_if_invalid(self):
        self.skipTest('testNotImplemented')

    def test_submit_selection_redirects_to_location_of_care_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_can_render_manual_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_manual_returns_to_page_with_error_if_invalid(self):
        self.skipTest('testNotImplemented')

    def test_submit_manual_redirects_to_location_of_care_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class ChildcareAddressPagesFunctionalTests(utils.NoMiddlewareTestCase):

    def setUp(self):
        self.application = utils.make_test_application()
        self.application_id = self.application.pk

    def test_can_render_loc_of_care_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_redirects_to_search_page_if_specified_different_from_home(self):
        self.skipTest('testNotImplemented')

    def test_submit_redirects_to_summary_page_if_specified_same_as_home(self):
        self.skipTest('testNotImplemented')

    def test_can_render_search_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_search_returns_to_page_with_error_if_not_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_search_redirects_to_select_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_can_render_select_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_selection_returns_to_page_with_error_if_not_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_selection_redirects_to_other_childminder_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_can_render_manual_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_manual_returns_to_page_with_error_if_not_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_manual_redirects_to_other_childminder_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_can_render_other_childminder_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_other_childminder_true_stores_info_in_db_if_valid(self):
        """
        Test to assert that the working_in_other_childminder_home attribute in the Application table is set to True
        when the applicant says they work in another childminder's home
        """

        # Build env
        form_data = {
            'id': str(self.application_id),
            'working_in_other_childminder_home': 'True'
        }

        response = self.client.post(reverse('Personal-Details-Childcare-Address-Details-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(302, response.status_code)
        self.assertTrue(application.working_in_other_childminder_home)

    def test_submit_other_childminder_false_stores_info_in_db_if_valid(self):
        """
        Test to assert that the working_in_other_childminder_home attribute in the Application table is set to False
        when the applicant says they don't work in another childminder's home
        """

        # Build env
        form_data = {
            'id': str(self.application_id),
            'working_in_other_childminder_home': 'False'
        }

        response = self.client.post(reverse('Personal-Details-Childcare-Address-Details-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(302, response.status_code)
        self.assertFalse(application.working_in_other_childminder_home)

    def test_submit_other_childminder_returns_to_page_with_error_if_not_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_other_childminder_redirects_to_children_known_page_if_valid(self):
        self.skipTest('testNotImplemented')

    def test_can_render_children_known_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_children_known_true_stores_info_in_db_if_valid(self):
        """
        Test to assert that the own_children attribute in the Application table is set to True when the applicant says
        they have children known to council services
        """

        # Build env
        form_data = {
            'id': str(self.application_id),
            'own_children': 'True',
            'reasons_known_to_social_services': 'Some test reason',
        }

        response = self.client.post(reverse('Personal-Details-Your-Own-Children-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(302, response.status_code)
        self.assertTrue(application.own_children)
        self.assertEqual('Some test reason', application.reasons_known_to_social_services)

    def test_submit_children_known_false_stores_info_in_db_if_valid(self):
        """
        Test to assert that the own_children attribute in the Application table is set to False when the applicant says
        they don't have own children known to council services
        """

        # Build env
        form_data = {
            'id': str(self.application_id),
            'own_children': 'False'
        }

        response = self.client.post(reverse('Personal-Details-Your-Own-Children-View')
                                    + '?id=' + str(self.application_id),
                                    form_data)

        application = models.Application.objects.get(application_id=self.application_id)

        self.assertEqual(302, response.status_code)
        self.assertFalse(application.own_children)
        self.assertEqual('', application.reasons_known_to_social_services)

    def test_submit_children_known_returns_to_page_with_error_if_not_valid(self):
        self.skipTest('testNotImplemented')

    def test_submit_children_known_redirects_to_summary_page_if_valid(self):
        self.skipTest('testNotImplemented')


@tag('http')
class SummaryPageFunctionalTests(utils.NoMiddlewareTestCase):

    def test_can_render_summary_page(self):
        self.skipTest('testNotImplemented')

    def test_submit_redirects_to_task_list(self):
        self.skipTest('testNotImplemented')

