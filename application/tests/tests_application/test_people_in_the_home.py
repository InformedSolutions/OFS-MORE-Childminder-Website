from django.test import modify_settings, TestCase
from django.urls import reverse

from application import models
from application import views


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class PeopleInTheHomeFunctionalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PeopleInTheHomeFunctionalTests, cls).setUpClass()
        cls.app_id = str(models.Application.objects.create().pk)

    def test_can_render_guidance_page(self):
        response = self.client.get(reverse('PITH-Guidance-View'),
                                   data={
                                       'id': self.app_id
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHGuidanceView.__name__)

    def test_post_request_to_guidance_page_redirects_to_adults_in_home_page(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_guidance_sets_task_status_to_started(self):
        self.skipTest('testNotImplemented')

    def test_yes_to_adults_in_home_redirects_to_details_page(self):
        self.skipTest('testNotImplemented')

    def test_no_to_adults_in_home_redirects_to_children_in_home_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_adult_details_page(self):
        response = self.client.get(reverse('PITH-Adult-Details-View'),
                                   data={
                                       'id': self.app_id,
                                       'adults': '0',
                                       'remove': '0'
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.other_people_adult_details.__name__)

    def test_can_add_one_adult(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_add_another_adult_adds_extra_form(self):
        self.skipTest('testNotImplemented')

    def test_can_add_two_adults(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_adult_details_page_redirects_to_lived_abroad_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_lived_abroad_page(self):
        response = self.client.get(reverse('PITH-Lived-Abroad-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHLivedAbroadView.__name__)

    def test_lived_abroad_page_renders_with_one_form_per_adult(self):
        self.skipTest('testNotImplemented')

    def test_no_adults_lived_abroad_redirects_to_dbs_check_if_childcare_register_only_applicant(self):
        self.skipTest('testNotImplemented')

    def test_no_adults_lived_abroad_redirects_to_military_base_page_if_not_childcare_register_only_applicant(self):
        self.skipTest('testNotImplemented')

    def test_any_adults_lived_abroad_redirects_to_abroad_criminal_record_checks_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_abroad_criminal_record_checks_page(self):
        response = self.client.get(reverse('PITH-Abroad-Criminal-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHAbroadCriminalView.__name__)

    def test_abroad_criminal_record_checks_page_renders_with_all_adults_who_lived_abroad(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_abroad_criminal_record_checks_page_redirects_to_dbs_check_if_childcare_register_only_applicant(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_abroad_criminal_record_checks_page_redirects_to_military_base_page_if_not_childcare_register_only_applicant(self):
        self.skipTest('testNotImplemented')

    def test_can_render_military_base_page(self):
        response = self.client.get(reverse('PITH-Military-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHMilitaryView.__name__)

    def test_no_for_all_adults_military_base_redirects_to_dbs_checks_page(self):
        self.skipTest('testNotImplemented')

    def test_yes_for_any_adults_military_base_redirects_to_MOD_checks_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_MOD_checks_page(self):
        response = self.client.get(reverse('PITH-Ministry-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHMinistryView.__name__)

    def test_MOD_checks_page_renders_with_all_adults_who_lived_on_a_military_base(self):
        self.skipTest('testNotImplemented')

    def test_post_to_MOD_checks_page_redirects_to_dbs_checks_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_dbs_checks_page(self):
        response = self.client.get(reverse('PITH-DBS-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHDBSCheckView.__name__)

    def test_dbs_checks_page_renders_with_one_form_per_adult(self):
        self.skipTest('testNotImplemented')

    # =========================================== #
    # Tests to be updated in CCN3-2064 start here #
    # =========================================== #

    def test_search_made_against_capita_dbs_list_for_each_adult_dbs_if_basic_field_validation_passes(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_not_in_capita_list_redirects_to_type_of_check_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_dbs_on_capita_list_but_does_not_match_date_of_birth_raises_form_error(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_dbs_on_capita_list_with_matching_date_of_birth_but_not_issued_in_last_three_months_redirects_to_type_of_check_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_dbs_on_capita_list_with_matching_date_of_birth_and_was_issued_in_last_three_months_but_contains_information_redirects_to_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_dbs_on_capita_list_with_matching_date_of_birth_and_was_issued_in_last_three_months_and_does_not_contain_information_redirects_to_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_all_adults_on_capita_list_with_matching_date_of_birth_and_was_issued_in_last_three_months_redirects_to_children_question_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_can_render_type_of_check_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_not_on_the_capita_dbs_list(self):
        self.skipTest('functionalityNotImplemented')

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_is_on_the_capita_dbs_list_but_was_not_issued_in_last_three_months(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_not_on_capita_list_and_does_not_have_enhanced_check_redirects_to_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adult_not_on_capita_list_and_has_an_enhanced_check_and_is_on_the_dbs_update_service_redirects_to_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_any_adults_not_on_capita_list_and_has_an_enhances_check_and_is_not_on_the_dbs_update_service_redirects_to_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_no_selection_made_keeps_applicant_on_the_same_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_can_render_before_you_submit_page(self):
        self.skipTest('functionalityNotImplemented')

    def test_can_render_children_question_page(self):
        response = self.client.get(reverse('PITH-Children-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHChildrenCheckView.__name__)

    def test_yes_to_children_in_the_home_redirects_to_children_details_page(self):
        self.skipTest('testNotImplemented')

    def test_no_to_children_in_the_home_redirects_to_summary_page_if_not_providing_care_in_own_home_and_no_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_no_to_children_in_the_home_redirects_to_own_children_page_if_providing_care_in_own_home(self):
        self.skipTest('testNotImplemented')

    def test_no_to_children_in_the_home_redirects_to_task_list_if_not_providing_care_in_own_home_and_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_can_render_children_details_page(self):
        response = self.client.get(reverse('PITH-Children-Details-View'),
                                   data={
                                       'id': self.app_id,
                                       'children': '0',
                                       'remove': '0'
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHChildrenDetailsView.__name__)

    def test_can_add_one_child_in_home(self):
        self.skipTest('testNotImplemented')

    def test_can_add_two_children_in_the_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_children_details_redirects_to_approaching_16_page_if_any_children_in_home_approaching_16(self):
        self.skipTest('testNotImplemented')

    def test_post_to_children_details_redirects_to_summary_page_if_not_children_approaching_16_and_not_providing_care_in_own_home_and_no_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_post_to_children_details_redirects_to_own_children_page_if_not_children_approaching_16_and_providing_care_in_own_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_children_details_redirects_to_task_list_if_not_children_approaching_16_and_not_providing_care_in_own_home_and_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_can_render_children_turning_16_page(self):
        response = self.client.get(reverse('PITH-Approaching-16-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.other_people_approaching_16.__name__)

    def test_children_turning_16_page_renders_with_children_turning_16(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_to_summary_page_if_not_providing_care_in_own_home_and_no_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_to_own_children_page_if_providing_care_in_own_home(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_task_list_if_not_providing_care_in_own_home_and_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_can_render_own_children_page(self):
        response = self.client.get(reverse('PITH-Own-Children-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHOwnChildrenCheckView.__name__)

    def test_yes_to_own_children_redirects_to_own_children_details_page(self):
        self.skipTest('testNotImplemented')

    def test_no_to_own_children_page_redirects_to_task_list_if_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_no_to_own_children_page_redirects_to_summary_page_if_no_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_can_render_own_children_details_page(self):
        response = self.client.get(reverse('PITH-Own-Children-Details-View'),
                                   data={
                                       'id': self.app_id,
                                       'children': '0',
                                       'remove': '0'
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHOwnChildrenDetailsView.__name__)

    def test_can_add_one_child_not_in_the_home(self):
        self.skipTest('testNotImplemented')

    def test_can_add_two_children_not_in_the_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_own_children_details_page_redirects_to_own_children_address_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_own_children_address_page(self):
        # TODO: Setup test such that child exists in db.
        response = self.client.get(reverse('PITH-Own-Children-Postcode-View'),
                                   data={
                                       'id': self.app_id,
                                       'children': '0'
                                   })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, views.PITHOwnChildrenPostcodeView.__name__)

    # def test_post_to_own_children_address_page_redirects_to_task_list_if_no_further_children_not_in_home_and_adults_without_dbs(self):
    #     self.skipTest('NotImplemented')
    #
    # def test_post_to_own_children_address_page_redirects_to_summary_page_if_no_further_children_not_in_home_and_no_adults_without_dbs(self):
    #     self.skipTest('NotImplemented')
    #
    # def test_post_to_own_children_address_page_redirects_to_own_children_address_page_if_further_children_not_in_home(self):
    #     self.skipTest('NotImplemented')

    def test_can_render_summary_page(self):
        self.skipTest('testNotImplemented')

    def test_all_change_links_in_summary_resolve_to_a_page(self):
        self.skipTest('testNotImplemented')

    def test_post_to_summary_page_redirects_to_email_confirmation_if_adults_in_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_summary_page_sends_email_to_each_adult_in_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_summary_redirects_to_task_list_with_done_status_if_no_adults_in_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_summary_redirects_to_task_list_with_waiting_status_if_adults_health_check_not_done(self):
        self.skipTest('testNotImplemented')

    def test_can_render_email_confirmation_page(self):
        self.skipTest('testNotImplemented')

    def test_post_to_email_confirmation_page_redirects_to_task_list_with_waiting_status(self):
        self.skipTest('testNotImplemented')

    def test_can_render_resend_email_page(self):
        self.skipTest('testNotImplemented')

    def test_post_to_resend_email_page_redirects_to_resend_email_confirmation_page(self):
        self.skipTest('testNotImplemented')

    def test_post_to_resend_email_page_resends_email_to_specified_adult_only(self):
        self.skipTest('testNotImplemented')

    def test_can_render_resend_email_confirmation_page(self):
        self.skipTest('testNotImplemented')

    def test_post_to_resend_email_confirmation_page_redirects_to_task_list_with_waiting_status(self):
        self.skipTest('testNotImplemented')

    def test_resend_health_questions_link_disappears_once_adult_completes_health_check(self):
        self.skipTest('testNotImplemented')


class PeopleInTheHomeFormsTests(TestCase):
    # TODO: Write tests to ensure validation of forms works - particularly those with conditionally revealing fields.
    pass
