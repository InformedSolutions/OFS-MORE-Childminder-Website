from django.test import modify_settings, TestCase


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class PeopleInTheHomeTestSuite(TestCase):
    def test_can_render_guidance_page(self):
        pass

    def test_post_request_to_guidance_page_redirects_to_adults_in_home_page(self):
        pass

    def test_post_request_to_guidance_sets_task_status_to_started(self):
        pass

    def test_yes_to_adults_in_home_redirects_to_details_page(self):
        pass

    def test_no_to_adults_in_home_redirects_to_children_in_home_page(self):
        pass

    def test_can_render_adult_details_page(self):
        pass

    def test_can_add_one_adult(self):
        pass

    def test_post_request_to_add_another_adult_adds_extra_form(self):
        pass

    def test_can_add_two_adults(self):
        pass

    def test_post_request_to_adult_details_page_redirects_to_lived_abroad_page(self):
        pass

    def test_can_render_lived_abroad_page(self):
        pass

    def test_lived_abroad_page_renders_with_one_form_per_adult(self):
        pass

    def test_no_adults_lived_abroad_redirects_to_dbs_check_if_childcare_register_only_applicant(self):
        pass

    def test_no_adults_lived_abroad_redirects_to_military_base_page_if_not_childcare_register_only_applicant(self):
        pass

    def test_any_adults_lived_abroad_redirects_to_abroad_criminal_record_checks_page(self):
        pass

    def test_can_render_abroad_criminal_record_checks_page(self):
        pass

    def test_abroad_criminal_record_checks_page_renders_with_all_adults_who_lived_abroad(self):
        pass

    def test_post_request_to_abroad_criminal_record_checks_page_redirects_to_dbs_check_if_childcare_register_only_applicant(self):
        pass

    def test_post_request_to_abroad_criminal_record_checks_page_redirects_to_military_base_page_if_not_childcare_register_only_applicant(self):
        pass

    def test_can_render_military_base_page(self):
        pass

    def test_no_for_all_adults_military_base_redirects_to_dbs_checks_page(self):
        pass

    def test_yes_for_any_adults_military_base_redirects_to_MOD_checks_page(self):
        pass

    def test_can_render_MOD_checks_page(self):
        pass

    def test_MOD_checks_page_renders_with_all_adults_who_lived_on_a_military_base(self):
        pass

    def test_post_to_MOD_checks_page_redirects_to_dbs_checks_page(self):
        pass
