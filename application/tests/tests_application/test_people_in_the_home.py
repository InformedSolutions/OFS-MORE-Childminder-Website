from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from django.test import TestCase
from django.urls import reverse

from application import dbs
from application import models
from application import views
from application.views import PITH_views
from application.tests import testutils


class PITHFunctionalTestCase(testutils.NoMiddlewareTestCase):

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
        testutils.assertView(response, PITH_views.PITHGuidanceView)

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
        testutils.assertView(response, views.other_people_adult_details)

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
        testutils.assertView(response, PITH_views.PITHLivedAbroadView)

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
        testutils.assertView(response, PITH_views.PITHAbroadCriminalView)

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
        testutils.assertView(response, PITH_views.PITHMilitaryView)

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
        testutils.assertView(response, PITH_views.PITHMinistryView)

    def test_MOD_checks_page_renders_with_all_adults_who_lived_on_a_military_base(self):
        self.skipTest('testNotImplemented')

    def test_post_to_MOD_checks_page_redirects_to_dbs_checks_page(self):
        self.skipTest('testNotImplemented')


@patch('application.dbs.read')
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

    def make_adult(self, dbs_read_mock, dbs_number=None, dbs_saved_yet=True, record_found=True, correct_dob=True,
                   issue_recent=True, dbs_info=None, capita_answer=None, on_update_answer=None, first_name=None,
                   middle_names=None, last_name=None):

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
        if dbs_number is not None and dbs_saved_yet:
            kwargs['dbs_certificate_number'] = dbs_number
        if capita_answer is not None:
            kwargs['capita'] = capita_answer
        if on_update_answer is not None:
            kwargs['on_update'] = on_update_answer

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

        # this is re-executed for each adult, but that's ok
        dbs_read_mock.side_effect = lambda d: self.mock_dbs_responses.get(d, self.mock_404_response)

        return adult

    def test_can_render_dbs_checks_page(self, dbs_read):

        response = self.client.get(reverse('PITH-DBS-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)

    def test_dbs_checks_page_renders_with_one_form_per_adult(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        response = self.client.get(reverse('PITH-DBS-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertXPath(response, "//input[@type='number' and @name='dbs_certificate_number{}']".format(adult1.pk))
        testutils.assertXPath(response, "//input[@type='number' and @name='dbs_certificate_number{}']".format(adult2.pk))

    def test_short_dbs_number_entered_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '12345678901',  # only 11 digits
            'dbs_certificate_number{}'.format(adult2.pk): '123456789013',
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)
        testutils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                         "/preceding-sibling::*[@class='error-message']").format(adult1.pk))

    def test_long_dbs_number_entered_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789011',
            'dbs_certificate_number{}'.format(adult2.pk): '1234567890123',  # 13 digits
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)
        testutils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                         "/preceding-sibling::*[@class='error-message']").format(adult2.pk))

    def test_same_dbs_number_as_applicant_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789012',  # same as applicant
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)
        testutils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                         "/preceding-sibling::*[@class='error-message']").format(adult1.pk))

    def test_adults_with_same_dbs_number_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',  # \ same dbs numbers
            'dbs_certificate_number{}'.format(adult2.pk): '123456789013',  # /
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)
        testutils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                         "/preceding-sibling::*[@class='error-message']").format(adult1.pk))

    def test_search_made_against_capita_dbs_list_for_each_adult_dbs_if_basic_field_validation_passes(self, dbs_read):

        adult1 = self.make_adult(dbs_read)
        adult2 = self.make_adult(dbs_read)

        self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertTrue(dbs.read.called_once_with('123456789013'))
        self.assertTrue(dbs.read.called_once_with('123456789014'))

    def test_any_adult_not_in_capita_list_redirects_to_type_of_check_page(self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_saved_yet=False)
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', dbs_saved_yet=False, record_found=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Type-Of-Check-View')+'?id='+self.app_id)

    def test_any_adult_dbs_on_capita_list_but_does_not_match_date_of_birth_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_saved_yet=False, correct_dob=False)
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', dbs_saved_yet=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSCheckView)
        testutils.assertXPath(response, ("//input[@type='number' and @name='dbs_certificate_number{}']"
                                         "/preceding-sibling::*[@class='error-message']").format(adult1.pk))

    def test_any_adult_dbs_on_capita_list_with_matching_date_of_birth_but_not_issued_in_last_three_months_redirects_to_type_of_check_page(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_saved_yet=False)
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', dbs_saved_yet=False, issue_recent=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Type-Of-Check-View')+'?id='+self.app_id)

    def test_all_adult_dbs_on_capita_list_with_matching_date_of_birth_and_was_issued_in_last_three_months_redirects_to_children_question_page(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_saved_yet=False)
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', dbs_saved_yet=False)

        response = self.client.post(reverse('PITH-DBS-Check-View'), data={
            'id': self.app_id,
            'dbs_certificate_number{}'.format(adult1.pk): '123456789013',
            'dbs_certificate_number{}'.format(adult2.pk): '123456789014',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-Children-Check-View') + '?id=' + self.app_id)

    def test_can_render_type_of_check_page(self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014')

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_not_on_the_capita_dbs_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False)
        adult3 = self.make_adult(dbs_read, dbs_number='123456789015', record_found=False)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        # we SHOULDN'T find this one
        testutils.assertNotXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                           .format(id=adult1.pk))
        # we SHOULD find these
        testutils.assertXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                        .format(id=adult2.pk))
        testutils.assertXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                        .format(id=adult3.pk))

    def test_type_of_check_page_renders_with_one_form_per_adult_whose_dbs_number_is_on_the_capita_dbs_list_but_was_not_issued_in_last_three_months(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', issue_recent=False)
        adult3 = self.make_adult(dbs_read, dbs_number='123456789015', issue_recent=False)

        response = self.client.get(reverse('PITH-DBS-Type-Of-Check-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        # we SHOULDN'T find this one
        testutils.assertNotXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                           .format(id=adult1.pk))
        # we SHOULD find these
        testutils.assertXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                        .format(id=adult2.pk))
        testutils.assertXPath(response, "//input[@type='radio' and (@name='capita{id}' or @name='on_update{id}')]"
                                        .format(id=adult3.pk))

    def test_any_adult_not_on_capita_list_and_hasnt_answered_capita_question_raises_form_error(self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            # no radio button response posted
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        testutils.assertXPath(response, ("//input[@type='radio' and @name='capita{}']/parent::*"
                                         "/preceding-sibling::*[@class='error-message']").format(adult2.pk))

    def test_any_adult_not_on_capita_list_responded_yes_to_capita_but_hasnt_answered_on_update_question_raises_form_error(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'capita{}'.format(adult2.pk): 'True',
            # no on_update response posted
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        testutils.assertXPath(response, ("//input[@type='radio' and @name='on_update{}']/parent::*"
                                         "/preceding-sibling::*[@class='error-message']").format(adult2.pk))

    def test_any_adult_on_capita_list_but_not_last_three_months_and_hasnt_answered_on_update_question_raises_form_error(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', issue_recent=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            # no radio button response posted
        })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSTypeOfCheckView)
        testutils.assertXPath(response, ("//input[@type='radio' and @name='on_update{}']/parent::*"
                                         "/preceding-sibling::*[@class='error-message']").format(adult2.pk))

    def test_any_adult_not_on_capita_list_and_does_not_have_enhanced_check_redirects_to_before_you_submit_page(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456790014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'capita{}'.format(adult2.pk): 'False',   # responded 'no' to has-enhanced
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)


    def test_any_adult_not_on_capita_list_and_has_an_enhanced_check_and_is_on_the_dbs_update_service_redirects_to_before_you_submit_page(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456790014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'capita{}'.format(adult2.pk): 'True',
            'on_update{}'.format(adult2.pk): 'True',  # responded 'yes' to on-update
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)

    def test_any_adults_not_on_capita_list_and_has_an_enhanced_check_and_is_not_on_the_dbs_update_service_redirects_to_before_you_submit_page(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456790014', record_found=False)

        response = self.client.post(reverse('PITH-DBS-Type-Of-Check-View'), data={
            'id': self.app_id,
            'capita{}'.format(adult2.pk): 'True',
            'on_update{}'.format(adult2.pk): 'False',  # responded 'no' to on-update
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('PITH-DBS-Post-Or-Apply-View') + '?id=' + self.app_id)

    def test_can_render_before_you_submit_page(self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, capita_answer=True,
                                 on_update_answer=True)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)

    def test_any_adult_not_on_capita_list_and_does_not_have_enhanced_check_appears_under_apply_for_dbs_check_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, capita_answer=False,
                                 first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertXPath(response, "(//h2[normalize-space(text())='Apply for new DBS check']"
                                            "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_not_on_capita_list_and_has_enhanced_check_and_is_not_on_the_dbs_update_service_appears_under_sign_up_to_update_service_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, capita_answer=True,
                                 on_update_answer=False, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertXPath(response, "(//h2[normalize-space(text())='Sign up to the Update Service']"
                                        "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_not_on_capita_list_and_has_enhanced_check_and_is_on_the_dbs_update_service_appears_under_update_service_check_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, capita_answer=True,
                                 on_update_answer=True, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertXPath(response, "(//h2[normalize-space(text())='DBS Update check']"
                                        "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_not_been_issued_in_the_last_3_months_and_is_on_the_update_service_appears_under_dbs_check_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=True, issue_recent=False,
                                 on_update_answer=True, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertXPath(response, "(//h2[normalize-space(text())='DBS Update check']"
                                        "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_not_been_issued_in_the_last_3_months_and_is_not_on_the_update_service_appears_under_sign_up_to_update_service_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=True, issue_recent=False,
                                 on_update_answer=False, first_name='Joe', middle_names='Alan', last_name='Bloggs')

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertXPath(response, "(//h2[normalize-space(text())='Sign up to the Update Service']"
                                        "/following-sibling::ul)[1]"
                                        "/li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_been_issued_in_the_last_3_months_and_does_contain_information_does_not_appear_in_any_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_info='Test',
                                 first_name='Joe', middle_names='Alan', last_name='Bloggs')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, issue_recent=False,
                                 on_update_answer=False)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertNotXPath(response, "//li[normalize-space(text())='Joe Alan Bloggs']")

    def test_any_adult_on_the_capita_list_and_has_been_issued_in_the_last_3_months_and_does_not_contain_information_does_not_appear_in_any_list(
            self, dbs_read):

        adult1 = self.make_adult(dbs_read, dbs_number='123456789013', dbs_info='',
                                 first_name='Joe', middle_names='Alan', last_name='Bloggs')
        adult2 = self.make_adult(dbs_read, dbs_number='123456789014', record_found=False, issue_recent=False,
                                 on_update_answer=False)

        response = self.client.get(reverse('PITH-DBS-Post-Or-Apply-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHDBSPostOrApplyView)
        testutils.assertNotXPath(response, "//li[normalize-space(text())='Joe Alan Bloggs']")


class PITHChildrenInHomeDetailsFunctionalTests(PITHFunctionalTestCase):

    def test_can_render_children_question_page(self):
        response = self.client.get(reverse('PITH-Children-Check-View'),
                                   data={
                                       'id': self.app_id,
                                   })

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHChildrenCheckView)

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
        testutils.assertView(response, PITH_views.PITHChildrenDetailsView)

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
        testutils.assertView(response, views.other_people_approaching_16)

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
        testutils.assertView(response, PITH_views.PITHOwnChildrenCheckView)

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
        testutils.assertView(response, PITH_views.PITHOwnChildrenDetailsView)

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

        application = models.Application.objects.get(pk=self.app_id)
        # create applicant's additional info models
        personal_details = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )
        home_address = models.ApplicantHomeAddress.objects.create(
            application_id=application,
            personal_detail_id=personal_details,
            move_in_month=7, move_in_year=2005,
            current_address=True,
        )
        childcare_type = models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=True,
        )

    def test_can_render_summary_page(self):

        response = self.client.get(reverse('PITH-Summary-View'), data={'id': self.app_id})

        self.assertEqual(response.status_code, 200)
        testutils.assertView(response, PITH_views.PITHCheckYourAnswersView)

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
