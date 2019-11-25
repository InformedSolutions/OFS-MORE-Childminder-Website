from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from django.urls import reverse
from django.test import tag

from application import dbs
from application import models
from application import views
from application.views import PITH_views
from application.tests import utils

from application.views import dbs as dbs_view


@tag('http')
class PITHFunctionalTestCase(utils.NoMiddlewareTestCase):

    @classmethod
    def setUpClass(cls):
        super(PITHFunctionalTestCase, cls).setUpClass()
        cls.app_id = str(models.Application.objects.create().pk)


class PITHGuidancePageFunctionalTests(PITHFunctionalTestCase):

    def test_can_render_guidance_page(self):
        response = self.client.get(reverse('PITH-Guidance-View'),
                                   data={
                                       'id': self.app_id
                                   })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHGuidanceView)

    def test_post_request_to_guidance_page_redirects_to_adults_in_home_page(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_guidance_sets_task_status_to_started(self):
        self.skipTest('testNotImplemented')


class PITHAdultDetailsFunctionalTests(PITHFunctionalTestCase):

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
        utils.assertView(response, views.other_people_adult_details)

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
        utils.assertView(response, PITH_views.PITHLivedAbroadView)

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
        utils.assertView(response, PITH_views.PITHAbroadCriminalView)

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
        utils.assertView(response, PITH_views.PITHMilitaryView)

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
        utils.assertView(response, PITH_views.PITHMinistryView)

    def test_MOD_checks_page_renders_with_all_adults_who_lived_on_a_military_base(self):
        self.skipTest('testNotImplemented')

    def test_post_to_MOD_checks_page_redirects_to_dbs_checks_page(self):
        self.skipTest('testNotImplemented')


mock_dbs_read = Mock()


@patch('application.dbs.read', new=mock_dbs_read)
class PITHAdultDBSFunctionalTests(PITHFunctionalTestCase):

    def setUp(self):

        application = models.Application.objects.get(pk=self.app_id)
        # create applicant's DBS details
        models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789012'
        )

        self.mock_404_response = Mock()
        self.mock_404_response.status_code = 404
        del self.mock_404_response.record

        self.mock_dbs_responses = {}
        mock_dbs_read.reset_mock()
        mock_dbs_read.side_effect = lambda d: self.mock_dbs_responses.get(d, self.mock_404_response)

    def test_can_render_dbs_checks_page(self):

        response = self.client.get(reverse('PITH-DBS-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSCheckView)

    def test_dbs_checks_page_renders_with_one_form_per_adult(self):

        adult1 = self.make_adult()
        adult2 = self.make_adult()

        response = self.client.get(reverse('PITH-DBS-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertXPath(response, "//input[@type='number' and @name='dbs_certificate_number{}']".format(adult1.pk))
        utils.assertXPath(response, "//input[@type='number' and @name='dbs_certificate_number{}']".format(adult2.pk))

    def test_invalid_data_entered_returns_to_same_dbs_check_page(self):

        adult1 = self.make_adult()
        adult2 = self.make_adult()

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '12345678901',  # only 11 digits
            'dbs_certificate_number{}'.format(adult2.pk): '123456789013',
        })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSCheckView)

    # Note this test isn't in test_form_validation because the validation compares multiple forms against each
    # other and as such the validation is done in the view logic
    def test_adults_with_same_dbs_number_raises_form_error(self):

        adult1 = self.make_adult()
        adult2 = self.make_adult()

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',  # \ same dbs numbers
            'dbs_certificate_number{}'.format(adult2.pk): '123456789013',  # /
        })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSCheckView)
        utils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                     "/preceding-sibling::*[@class='error-message']").format(adult1.pk))

    def test_search_made_against_capita_dbs_list_for_each_adult_dbs_if_basic_field_validation_passes(self):

        adult1 = self.make_adult()
        adult2 = self.make_adult()

        self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertTrue(dbs.read.called_once_with('123456789013'))
        self.assertTrue(dbs.read.called_once_with('123456789014'))

    def test_any_adult_not_in_capita_list_redirects_to_type_of_check_page(self):

        adult1 = self.make_adult(dbs_number='123456789013')
        adult2 = self.make_adult(dbs_number='123456789014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Type-Of-Check-View')+'?id='+self.app_id)

    def test_any_adult_dbs_on_capita_list_with_matching_date_of_birth_but_not_issued_in_last_three_months_redirects_to_type_of_check_page(
            self):

        adult1 = self.make_adult(dbs_number='123456789013')
        adult2 = self.make_adult(dbs_number='123456789014', issue_recent=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Type-Of-Check-View')+'?id='+self.app_id)

    def test_all_adult_dbs_on_capita_list_with_matching_date_of_birth_and_was_issued_in_last_three_months_redirects_to_children_question_page(
            self):

        adult1 = self.make_adult(dbs_number='123456789013')
        adult2 = self.make_adult(dbs_number='123456789014')

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-Children-Check-View') + '?id=' + self.app_id)

    def test_stores_dbs_numbers_if_validation_passes(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=False, record_found=False)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=False, record_found=True)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        refetched_adult1 = models.AdultInHome.objects.get(pk=adult1.pk)
        self.assertEqual(refetched_adult1.dbs_certificate_number, '123456789013')

        refetched_adult2 = models.AdultInHome.objects.get(pk=adult2.pk)
        self.assertEqual(refetched_adult2.dbs_certificate_number, '123456789014')

    def test_stores_dbs_certificate_info_after_checking_dbs_list(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=False, record_found=False)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=False, record_found=True,
                                 dbs_info='Test info')

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        refetched_adult1 = models.AdultInHome.objects.get(pk=adult1.pk)
        self.assertEqual(refetched_adult1.capita, False)
        self.assertEqual(refetched_adult1.within_three_months, None)
        self.assertEqual(refetched_adult1.certificate_information, '')

        refetched_adult2 = models.AdultInHome.objects.get(pk=adult2.pk)
        self.assertEqual(refetched_adult2.capita, True)
        self.assertEqual(refetched_adult2.within_three_months, True)
        self.assertEqual(refetched_adult2.certificate_information, 'Test info')

    def test_can_render_type_of_check_page(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_not_on_the_capita_dbs_list(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False)
        adult3 = self.make_adult(dbs_number='123456789015', dbs_saved_yet=True, record_found=False)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        # we SHOULDN'T find this one
        utils.assertNotXPath(response,
                             "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                             .format(id=adult1.pk))
        # we SHOULD find these
        utils.assertXPath(response, "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                          .format(id=adult2.pk))
        utils.assertXPath(response, "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                          .format(id=adult3.pk))

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_is_on_the_capita_dbs_list_but_was_not_issued_in_last_three_months(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, issue_recent=False)
        adult3 = self.make_adult(dbs_number='123456789015', dbs_saved_yet=True, issue_recent=False)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        # we SHOULDN'T find this one
        utils.assertNotXPath(response,
                             "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                             .format(id=adult1.pk))
        # we SHOULD find these
        utils.assertXPath(response, "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                          .format(id=adult2.pk))
        utils.assertXPath(response, "//input[@type='radio' and (@name='enhanced_check{id}' or @name='on_update{id}')]"
                          .format(id=adult3.pk))

    def test_type_of_check_page_renders_adult_forms_again_when_returning_to_change_answers(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=True, on_update_answer=False)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=True, issue_recent=False,
                                 on_update_answer=True)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)

        utils.assertXPath(response, "//input[@type='radio' and @name='enhanced_check{id}']".format(id=adult1.pk))
        utils.assertXPath(response, "//input[@type='radio' and @name='on_update{id}']".format(id=adult1.pk))
        utils.assertNotXPath(response, "//input[@type='radio' and @name='enhanced_check{id}']".format(id=adult2.pk))
        utils.assertXPath(response, "//input[@type='radio' and @name='on_update{id}']".format(id=adult2.pk))

    def test_rendering_type_of_check_page_doesnt_remove_previous_answers_from_database(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=True, on_update_answer=False)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=True, issue_recent=False,
                                 on_update_answer=True)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)

        refetched_adult1 = models.AdultInHome.objects.get(pk=adult1.pk)
        self.assertEqual(True, refetched_adult1.enhanced_check)
        self.assertEqual(False, refetched_adult1.on_update)

        refetched_adult2 = models.AdultInHome.objects.get(pk=adult2.pk)
        self.assertIsNone(refetched_adult2.enhanced_check)
        self.assertEqual(True, refetched_adult2.on_update)

    def test_any_invalid_responses_on_type_of_check_page_returns_to_type_of_check_page(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            # no radio button response posted
        })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)

    def test_any_adult_not_on_capita_list_and_does_not_have_enhanced_check_redirects_to_before_you_submit_page(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456790014', dbs_saved_yet=True, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'enhanced_check{}'.format(adult2.pk): 'False',   # responded 'no' to has-enhanced
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)

    def test_any_adult_not_on_capita_list_and_has_an_enhanced_check_and_is_on_the_dbs_update_service_redirects_to_before_you_submit_page(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456790014', dbs_saved_yet=True, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'enhanced_check{}'.format(adult2.pk): 'True',
            'on_update{}'.format(adult2.pk): 'True',  # responded 'yes' to on-update
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)

    def test_any_adults_not_on_capita_list_and_has_an_enhanced_check_and_is_not_on_the_dbs_update_service_redirects_to_before_you_submit_page(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456790014', dbs_saved_yet=True, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'enhanced_check{}'.format(adult2.pk): 'True',
            'on_update{}'.format(adult2.pk): 'False',  # responded 'no' to on-update
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)

    def test_doesnt_search_dbs_list_again_when_posting_to_type_of_check_page(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456790014', dbs_saved_yet=True, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'enhanced_check{}'.format(adult2.pk): 'True',
            'on_update{}'.format(adult2.pk): 'True',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(mock_dbs_read.called)

    def test_can_render_before_you_submit_page(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=True, on_update_answer=True)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)

    def test_any_adult_not_on_capita_list_and_does_not_have_enhanced_check_appears_under_apply_for_dbs_check_list(self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=False, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertXPath(response, "(//h2[normalize-space(text())='Apply for new DBS check']"
                                            "/following-sibling::ul)[1]"
                                    "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_not_on_capita_list_and_has_enhanced_check_and_is_not_on_the_dbs_update_service_appears_under_sign_up_to_update_service_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=True, on_update_answer=False, first_name='Joe', middle_names='Alan',
                                 last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertXPath(response, "(//h2[normalize-space(text())='Sign up to the DBS Update Service']"
                                        "/following-sibling::ul)[1]"
                                    "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_not_on_capita_list_and_has_enhanced_check_and_is_on_the_dbs_update_service_appears_under_update_service_check_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False,
                                 enhanced_answer=True, on_update_answer=True, first_name='Joe', middle_names='Alan',
                                 last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertXPath(response, "(//h2[normalize-space(text())='DBS Update Service check']"
                                        "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_not_been_issued_in_the_last_3_months_and_is_on_the_update_service_appears_under_dbs_check_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=True, issue_recent=False,
                                 on_update_answer=True, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertXPath(response, "(//h2[normalize-space(text())='DBS Update Service check']"
                                        "/following-sibling::ul)[1]"
                                    "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_not_been_issued_in_the_last_3_months_and_is_not_on_the_update_service_appears_under_sign_up_to_update_service_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True)
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=True, issue_recent=False,
                                 on_update_answer=False, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertXPath(response, "(//h2[normalize-space(text())='Sign up to the DBS Update Service']"
                                        "/following-sibling::ul)[1]"
                                    "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_been_issued_in_the_last_3_months_and_does_contain_information_does_not_appear_in_any_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True, dbs_info='Test',
                                 first_name='Joe', middle_names='Alan', last_name='Bloggs')
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False, issue_recent=False,
                                 on_update_answer=False)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertNotXPath(response, "//li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_been_issued_in_the_last_3_months_and_does_not_contain_information_does_not_appear_in_any_list(
            self):

        adult1 = self.make_adult(dbs_number='123456789013', dbs_saved_yet=True, dbs_info='',
                                 first_name='Joe', middle_names='Alan', last_name='Bloggs')
        adult2 = self.make_adult(dbs_number='123456789014', dbs_saved_yet=True, record_found=False, issue_recent=False,
                                 on_update_answer=False)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        utils.assertNotXPath(response, "//li[normalize-space(text())='Joe Alan Bloggs']")

    # ----------------------

    def make_adult(self, dbs_number=None, dbs_saved_yet=False, record_found=True, correct_dob=True, issue_recent=True,
                   dbs_info=None, enhanced_answer=None, on_update_answer=None, first_name=None, middle_names=None,
                   last_name=None):
        """Create a test AdultInHome entry and prepare a mock dbs response for them"""

        application = models.Application.objects.get(pk=self.app_id)
        kwargs = {
            'application_id': application,
            'adult': 1,
            'birth_day': 30,
            'birth_month': 10,
            'birth_year': 1975,
            'first_name': first_name or 'Jane',
            'middle_names': middle_names or 'Samantha',
            'last_name': last_name or 'Doe',
        }
        if dbs_saved_yet:
            if dbs_number is not None:
                kwargs['dbs_certificate_number'] = dbs_number
            if enhanced_answer is not None:
                kwargs['enhanced_check'] = enhanced_answer
            if on_update_answer is not None:
                kwargs['on_update'] = on_update_answer
            if dbs_info is not None:
                kwargs['certificate_information'] = dbs_info
            kwargs['capita'] = record_found
            kwargs['within_three_months'] = issue_recent

        adult = models.AdultInHome.objects.create(**kwargs)

        if dbs_number is not None:

            mock_response = Mock()

            if record_found:
                mock_response.status_code = 200
                issue_date = datetime.now() - timedelta(weeks=1 if issue_recent else 15)
                mock_response.record = {
                    'certificate_number': dbs_number,
                    'date_of_issue': issue_date.strftime('%Y-%m-%d'),
                    'date_of_birth': '1975-10-30' if correct_dob else '1975-09-29',
                    'certificate_information': dbs_info if dbs_info is not None else 'Test',
                }
                self.mock_dbs_responses[dbs_number] = mock_response

        return adult


class PITHChildrenInHomeDetailsFunctionalTests(PITHFunctionalTestCase):

    def test_can_render_children_question_page(self):
        response = self.client.get(reverse('PITH-Children-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHChildrenCheckView)

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
        utils.assertView(response, PITH_views.PITHChildrenDetailsView)

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
        utils.assertView(response, views.other_people_approaching_16)

    def test_children_turning_16_page_renders_with_children_turning_16(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_to_summary_page_if_not_providing_care_in_own_home_and_no_adults_without_dbs(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_to_own_children_page_if_providing_care_in_own_home(self):
        self.skipTest('testNotImplemented')

    def test_post_request_to_children_turning_16_redirects_task_list_if_not_providing_care_in_own_home_and_adults_without_dbs(self):
        self.skipTest('testNotImplemented')


class PITHOwnChildrenDetailsFunctionalTests(PITHFunctionalTestCase):

    def test_can_render_own_children_page(self):
        response = self.client.get(reverse('PITH-Own-Children-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHOwnChildrenCheckView)

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
        utils.assertView(response, PITH_views.PITHOwnChildrenDetailsView)

    def test_can_add_one_child_not_in_the_home(self):
        self.skipTest('testNotImplemented')

    def test_can_add_two_children_not_in_the_home(self):
        self.skipTest('testNotImplemented')

    def test_post_to_own_children_details_page_redirects_to_own_children_address_page(self):
        self.skipTest('testNotImplemented')

    def test_can_render_own_children_address_page(self):
        self.skipTest('testNotImplemented')
        # TODO: Setup test such that child exists in db.
        # response = self.client.get(reverse('PITH-Own-Children-Postcode-View'),
        #                            data={
        #                                'id': self.app_id,
        #                                'children': '0'
        #                            })
        #
        # self.assertEqual(response.status_code, 200)
        # testutils.assertView(response, PITH_views.PITHOwnChildrenPostcodeView)

    # def test_post_to_own_children_address_page_redirects_to_task_list_if_no_further_children_not_in_home_and_adults_without_dbs(self):
    #     self.skipTest('NotImplemented')
    #
    # def test_post_to_own_children_address_page_redirects_to_summary_page_if_no_further_children_not_in_home_and_no_adults_without_dbs(self):
    #     self.skipTest('NotImplemented')
    #
    # def test_post_to_own_children_address_page_redirects_to_own_children_address_page_if_further_children_not_in_home(self):
    #     self.skipTest('NotImplemented')


class PITHSummaryPageFunctionalTests(PITHFunctionalTestCase):

    def setUp(self):

        self.application = models.Application.objects.get(pk=self.app_id)
        # create applicant's additional info models
        self.personal_details = models.ApplicantPersonalDetails.objects.create(
            application_id=self.application,
        )
        self.home_address = models.ApplicantHomeAddress.objects.create(
            application_id=self.application,
            personal_detail_id=self.personal_details,
            current_address=True,
        )
        self.childcare_type = models.ChildcareType.objects.create(
            application_id=self.application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=True,
            childcare_places=3,
            weekday_before_school=True,
            weekday_after_school=True,
            weekend_all_day=True,
            overnight_care=False
        )


    # ----------

    def test_can_render_summary_page(self):

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        utils.assertView(response, PITH_views.PITHCheckYourAnswersView)

    def test_displays_adults_main_fields_that_are_always_shown(self):

        self.application.adults_in_home = True
        self.application.save()

        adult1 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984,
            relationship='Uncle',
            email='foo@example.com',
            PITH_mobile_number='07700 900840',
            PITH_same_address=True,
            dbs_certificate_number='123456789012',
            lived_abroad=False,
        )

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertSummaryField(response, 'Does anyone aged 16 or over live or work in the home?', 'Yes')
        utils.assertSummaryField(response, 'Name', 'Joe Anthony Bloggs', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Date of birth', '1 May 1984', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Relationship', 'Uncle', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Email', 'foo@example.com', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Phone number', '07700 900840', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Address', 'Same as home address', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'DBS certificate number', '123456789012', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Lived abroad in the last 5 years?', 'No', heading='Joe Anthony Bloggs')

    def test_displays_adult_military_base_fields_if_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.save()

        self.childcare_type.zero_to_five = True
        self.childcare_type.save()

        adult1 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984,
            military_base=False, PITH_same_address=True,
        )

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertSummaryField(response, 'Lived or worked in British military base in the last 5 years?', 'No',
                                 heading='Joe Anthony Bloggs')

    def test_doesnt_display_adult_military_base_fields_if_not_caring_for_zero_to_five_year_olds(self):

        self.application.adults_in_home = True
        self.application.save()

        self.childcare_type.zero_to_five = False
        self.childcare_type.save()

        adult1 = models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984, PITH_same_address=True
        )
        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertNotSummaryField(response, 'Lived or worked in British military base in the last 5 years?',
                                    heading='Joe Anthony Bloggs')

    def test_displays_adult_enhanced_dbs_field_only_for_adults_without_dbs_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.save()

        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984,
            dbs_certificate_number='123456789012', capita=True, PITH_same_address=True,
        )
        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joanne', middle_names='Bethanny', last_name='Smith',
            birth_day=5, birth_month=1, birth_year=1948,
            dbs_certificate_number='123456789013', capita=False, enhanced_check=True, PITH_same_address=True,
        )

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertNotSummaryField(response, 'Enhanced DBS check for home-based childcare?',
                                    heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'Enhanced DBS check for home-based childcare?', 'Yes',
                                 heading='Joanne Bethanny Smith')

    def test_displays_adult_dbs_on_update_field_only_for_adults_without_recent_dbs_on_capita_list(self):

        self.application.adults_in_home = True
        self.application.save()

        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984,
            dbs_certificate_number='123456789012', capita=True, PITH_same_address=True,
        )
        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joanne', middle_names='Bethanny', last_name='Smith',
            birth_day=5, birth_month=1, birth_year=1948,
            dbs_certificate_number='123456789013', capita=True, within_three_months=False, on_update=True, PITH_same_address=True,
        )
        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Josef', middle_names='Charlie', last_name='Thompson',
            birth_day=5, birth_month=5, birth_year=1966,
            dbs_certificate_number='123456789014', capita=False, on_update=False, PITH_same_address=True,
        )

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertNotSummaryField(response, 'On the DBS Update Service?', heading='Joe Anthony Bloggs')
        utils.assertSummaryField(response, 'On the DBS Update Service?', 'Yes', heading='Joanne Bethanny Smith')
        utils.assertSummaryField(response, 'On the DBS Update Service?', 'No', heading='Josef Charlie Thompson')

    def test_doesnt_display_fields_relating_to_private_information_for_adults_in_home(self):

        self.application.adults_in_home = True
        self.application.save()

        models.AdultInHome.objects.create(
            application_id=self.application,
            first_name='Joe', middle_names='Anthony', last_name='Bloggs',
            birth_day=1, birth_month=5, birth_year=1984,
            dbs_certificate_number='123456789012', capita=True, PITH_same_address=True,
        )

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        utils.assertNotSummaryField(response, 'Known to council social services in regards to their own children?',
                                    heading='Joe Anthony Bloggs')

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

