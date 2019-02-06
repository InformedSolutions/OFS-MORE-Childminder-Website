from django.test import modify_settings, TestCase
from django.urls import reverse

from application import models
from application import views


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })

def test_can_render_guidance_page(self):
    self.skipttest('testNotImplemented')

def test_post_request_to_guidance_page_redirects_to_criminal_details_page(self):
    self.skipTest('testNotImplemented')

def test_can_render_dbs_checks_page(self):
    self.skipTest('testNotImplemented')

def test_search_made_against_capita_dbs_list_if_basic_validation_passes(self):
    self.skipTest('testNotImplemented')

def test_dbs_not_on_capita_list_redirect_to_enhanced_check(self):
    self.skipTest('testNotImplemented')

def test_dbs_on_capita_list_birth_date_not_match_validation_error(self):
    self.skipTest('testNotImplemented')

def test_dbs_on_capita_list_birth_date_match_not_in_last_three_months_redirect_enhanced_check(self):
    self.skipTest('testNotImplemented')

def test_dbs_on_capita_list_birth_date_match_in_last_three_months_redirect_post_dbs(self):
    self.skipTest('testNotImplemented')

def test_dbs_on_capita_list_birth_date_match_in_last_three_months_no_information_redirect_check_your_answers(self):
    self.skipTest('testNotImplemented')

#enhanced check

def test_can_render_enhanced_check(self):
    self.skipTest('testNotImplemented')

def test_not_on_capita_list_previously_entered_dbs_shows_above_enhanced_check_question(self):
    self.skipTest('testNotImplemented')

def test_on_capita_list_not_issued_last_three_months_previously_entered_dbs_shows_above_enhanced_check_question(self):
    self.skipTest('testNotImplemented')

def test_not_on_capita_list_no_enhanced_check_validation_passes_redirects_to_apply(self):
    self.skipTest('testNotImplemented')

def test_enhanced_check_not_on_capita_list_show_dbs_update(self):
    self.skipTest('testNotImplemented')

def test_not_on_capita_list_enhanced_check_on_update_validation_passes_redirects_dbs_update_check(self):
    self.skipTest('testNotImplemented')

def test_not_on_capita_list_enhanced_check_no_update_redirect_to_sign_up(self):
    self.skipTest('testNotImplemented')

def test_enhanced_check_no_selection_validation(self):
    self.skipTest('testNotImplemented')

def test_can_render_dbs_update_check_page(self):
    self.skipTest('testNotImplemented')

def test_dbs_update_check_continue_redirects_to_Post_dbs(self):
    self.skipTest('testNotImplemented')

def test_can_render_apply_new_dbs_check(self):
    self.skipTest('testNotImplemented')

def test_apply_continue_redirects_task_list(self):
    self.skipTest('testNotImplemented')

def test_apply_continue_task_status_started(self):
    self.skipTest('testNotImplemented')

def test_can_render_dbs_updated_check_your_answers(self):
    self.skipTest('testNotImplemented')
