import datetime
from uuid import UUID

from django.conf import settings
from django.test import Client
from django.test import TestCase
from django.urls import resolve, reverse

from ... import models
from ...views import eyfs_guidance, eyfs_details, eyfs_certificate, eyfs_summary
from ...views import ChildcareTrainingGuidanceView, \
    ChildcareTrainingCourseRequiredView, \
    ChildcareTrainingCourseTypeView, \
    ChildcareTrainingCertificateView, \
    ChildcareTrainingDetailsView, \
    ChildcareTrainingSummaryView, \
    task_list


class ChildcareTrainingTestSuite(TestCase):
    test_app_id = UUID
    url_suffix  = '?id=' + str(UUID)

    # ---------- #
    # HTTP Tests #
    # ---------- #

    def test_can_render_guidance_page(self):
        response = self.client.get(reverse('Childcare-Training-Guidance') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingGuidanceView.as_view().__name__)

    def test_if_childcare_register_only_guidance_redirects_to_type_of_course(self):
        pass

    def test_can_render_type_of_course_page(self):
        response = self.client.get(reverse('Type-Of-Childcare-Training') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingCourseTypeView.as_view().__name__)

    def test_if_no_training_then_redirect_to_go_on_a_course(self):
        response = self.client.post(reverse('Type-Of-Childcare-Training') + self.url_suffix,
                                    data={
                                        'efys_training': False,
                                        'common_core_training': False,
                                        'no_training': True
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCourseRequiredView.as_view().__name__)

    def test_can_render_go_on_a_course_page(self):
        response = self.client.get(reverse('Go-On-A-Childcare-Training-Course') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingCourseRequiredView.as_view().__name__)

    def test_post_to_go_an_a_course_redirects_to_task_list_with_started_task_status(self):
        response = self.client.post(reverse('Go-On-A-Childcare-Training-Course') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, task_list.__name__)
        self.assertEqual(models.Application.objects.get(pk=self.UUID).eyfs_status, 'STARTED')

    def test_if_eyfs_training_then_redirect_to_training_certificate_page(self):
        response = self.client.post(reverse('Type-Of-Childcare-Training') + self.url_suffix,
                                    data={
                                        'efys_training': True,
                                        'common_core_training': False,
                                        'no_training': False
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_if_common_core_training_then_redirect_to_training_certificate_page(self):
        response = self.client.post(reverse('Type-Of-Childcare-Training') + self.url_suffix,
                                    data={
                                        'efys_training': False,
                                        'common_core_training': True,
                                        'no_training': False
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_if_both_training_options_then_redirect_to_training_certificate_page(self):
        response = self.client.post(reverse('Type-Of-Childcare-Training') + self.url_suffix,
                                    data={
                                        'efys_training': True,
                                        'common_core_training': True,
                                        'no_training': False
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_can_render_training_certificate_page(self):
        response = self.client.get(reverse('Childcare-Training-Certificate') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_if_early_years_guidance_redirects_to_childcare_training_details(self):
        pass

    def test_can_render_childcare_training_details_page(self):
        response = self.client.get(reverse('Childcare-Training-Details') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingDetailsView.as_view().__name__)

    def test_valid_post_request_to_childcare_training_redirects_to_training_certificate_page(self):
        response = self.client.post(reverse('Childcare-Training-Details') + self.url_suffix,
                                    data={
                                        'eyfs_course_name': 'Horses for Courses',
                                        'eyfs_course_date': '01-01-2018',
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_post_request_to_training_certificate_redirects_to_summary_page(self):
        response = self.client.post(reverse('Childcare-Training-Certificate') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingSummaryView.as_view().__name__)

    def test_can_render_summary_page(self):
        response = self.client.get(reverse('Childcare-Training-Summary') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingSummaryView.as_view().__name__)

    def test_post_to_summary_redirects_to_task_list_with_done_task_status(self):
        response = self.client.post(reverse('Childcare-Training-Summary') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, task_list.__name__)
        self.assertEqual(models.Application.objects.get(pk=self.UUID).eyfs_status, 'COMPLETED')

    # ---------- #
    # UNIT tests #
    # ---------- #

    def test_selecting_none_and_another_training_course_raises_validation_error(self):
        pass

    def test_selecting_no_training_options_raises_validation_error(self):
        pass

    def test_entering_no_course_title_raises_validation_error(self):
        pass

    def test_entering_no_course_date_raises_validation_error(self):
        pass


# class EYFSTest(TestCase):
#
#     def test_url_resolves_to_page(self):
#         found = resolve(settings.URL_PREFIX + '/early-years/')
#         self.assertEqual(found.func, eyfs_guidance)
#
#     def test_page_not_displayed_without_id(self):
#         c = Client()
#         try:
#             c.get(settings.URL_PREFIX + '/early-years?id=')
#             self.assertEqual(1, 0)
#         except:
#             self.assertEqual(0, 0)
#
#     def test_url_resolves_to_page(self):
#         found = resolve(settings.URL_PREFIX + '/early-years/details/')
#         self.assertEqual(found.func, eyfs_details)
#
#     def test_page_not_displayed_without_id(self):
#         c = Client()
#         try:
#             c.get(settings.URL_PREFIX + '/early-years/details?id=')
#             self.assertEqual(1, 0)
#         except:
#             self.assertEqual(0, 0)
#
#     def test_url_resolves_to_page(self):
#         found = resolve(settings.URL_PREFIX + '/early-years/certificate/')
#         self.assertEqual(found.func, eyfs_certificate)
#
#     def test_page_not_displayed_without_id(self):
#         c = Client()
#         try:
#             c.get(settings.URL_PREFIX + '/early-years/certificate?id=')
#             self.assertEqual(1, 0)
#         except:
#             self.assertEqual(0, 0)
#
#     def test_url_resolves_to_page(self):
#         found = resolve(settings.URL_PREFIX + '/early-years/check-answers/')
#         self.assertEqual(found.func, eyfs_summary)
#
#     def test_page_not_displayed_without_id(self):
#         c = Client()
#         try:
#             c.get(settings.URL_PREFIX + '/early-years/check-answers?id=')
#             self.assertEqual(1, 0)
#         except:
#             self.assertEqual(0, 0)
#
#     def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
#         test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
#         test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
#
#         application = models.Application.objects.create(
#             application_id=(UUID(test_application_id)),
#             application_type='CHILDMINDER',
#             application_status='DRAFTING',
#             cygnum_urn='',
#             login_details_status='COMPLETED',
#             personal_details_status='COMPLETED',
#             childcare_type_status='COMPLETED',
#             first_aid_training_status='COMPLETED',
#             eyfs_training_status='NOT_STARTED',
#             criminal_record_check_status='COMPLETED',
#             health_status='COMPLETED',
#             references_status='COMPLETED',
#             people_in_home_status='COMPLETED',
#             declarations_status='NOT_STARTED',
#             date_created=datetime.datetime.today(),
#             date_updated=datetime.datetime.today(),
#             date_accepted=None,
#         )
#         user = models.UserDetails.objects.create(
#             login_id=(UUID(test_login_id)),
#             application_id=application,
#             email='',
#             mobile_number='',
#             add_phone_number='',
#             email_expiry_date=None,
#             sms_expiry_date=None,
#             magic_link_email='',
#             magic_link_sms=''
#         )
#         assert (models.Application.objects.get(pk=test_application_id).eyfs_training_status != 'COMPLETED')
#
#     def delete(self):
#         models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
#         models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
