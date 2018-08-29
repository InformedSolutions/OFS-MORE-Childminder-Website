from django.test import TestCase
from django.urls import resolve, reverse

from application import models, views
from application.views import ChildcareTrainingGuidanceView, \
    ChildcareTrainingCourseRequiredView, \
    TypeOfChildcareTrainingView, \
    ChildcareTrainingCertificateView, \
    ChildcareTrainingDetailsView, \
    ChildcareTrainingSummaryView, \
    task_list

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


class ChildcareTrainingTestSuite(TestCase, ApplicationTestBase):

    def setUp(self):
        self.TestAppEmail()
        self.TestValidateEmail()
        self.TestAppPhone()
        self.url_suffix = '?id=' + str(self.app_id)

        app = models.Application.objects.get(pk=self.app_id)

        models.ChildcareType.objects.create(
            application_id=app,
            zero_to_five=True,
            five_to_eight=True,
            eight_plus=True,
        )

        models.ChildcareTraining.objects.create(
            application_id=app,
        )

    def create_eyfs_applicant(self):
        record = models.ChildcareType.objects.get(application_id=self.app_id)
        record.zero_to_five = True
        record.save()

    def create_childcare_register_applicant(self):
        record = models.ChildcareType.objects.get(application_id=self.app_id)
        record.zero_to_five = False
        record.save()

    # ---------- #
    # HTTP Tests #
    # ---------- #

    @parameterise_by_applicant_type
    def test_can_render_guidance_page(self):
        response = self.client.get(reverse('Childcare-Training-Guidance-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingGuidanceView.as_view().__name__)

    def test_guidance_redirects_to_type_of_course_if_childcare_register_applicant_only(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Childcare-Training-Guidance-View') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, TypeOfChildcareTrainingView.as_view().__name__)

    def test_can_render_type_of_course_page(self):
        self.create_childcare_register_applicant()

        response = self.client.get(reverse('Type-Of-Childcare-Training-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, TypeOfChildcareTrainingView.as_view().__name__)

    def test_if_no_training_then_redirect_to_go_on_a_course(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                    data={
                                        'childcare_training': ['no_training']
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCourseRequiredView.as_view().__name__)

    def test_can_render_go_on_a_course_page(self):
        response = self.client.get(reverse('Childcare-Training-Course-Required-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingCourseRequiredView.as_view().__name__)

    def test_post_to_go_an_a_course_redirects_to_task_list_with_started_task_status(self):
        response = self.client.post(reverse('Childcare-Training-Course-Required-View') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, task_list.__name__)
        self.assertEqual(models.Application.objects.get(pk=self.app_id).childcare_training_status, 'IN_PROGRESS')

    def test_if_eyfs_training_then_redirect_to_training_certificate_page(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                    data={
                                        'childcare_training': ['eyfs_training']
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_if_common_core_training_then_redirect_to_training_certificate_page(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                    data={
                                        'childcare_training': ['common_core_training']
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_if_both_training_options_then_redirect_to_training_certificate_page(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                    data={
                                        'childcare_training': ['eyfs_training', 'common_core_training']
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_selecting_none_and_another_training_course_raises_validation_error(self):
        self.create_childcare_register_applicant()

        option_combinations = [
            ['eyfs_training', 'no_training'],
            ['common_core_training', 'no_training'],
            ['eyfs_training', 'common_core_training', 'no_training']
        ]

        for combo in option_combinations:
            response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                        {'childcare_training': combo})

            view_class_name = response.resolver_match._func_path
            class_ = getattr(globals()['views'], view_class_name.split('.')[-1])

            self.assertEqual(response.status_code, 200)
            self.assertEqual(class_, TypeOfChildcareTrainingView)
            self.assertFormError(response, 'form', 'childcare_training', 'Please select types of courses or none')

    def test_selecting_no_training_options_raises_validation_error(self):
        self.create_childcare_register_applicant()

        response = self.client.post(reverse('Type-Of-Childcare-Training-View') + self.url_suffix,
                                    {'childcare_training': []})

        view_class_name = response.resolver_match._func_path
        class_ = getattr(globals()['views'], view_class_name.split('.')[-1])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(class_, TypeOfChildcareTrainingView)
        self.assertFormError(response, 'form', 'childcare_training', 'Please select the types of childcare courses you have completed')

    @parameterise_by_applicant_type
    def test_can_render_training_certificate_page(self):
        response = self.client.get(reverse('Childcare-Training-Certificate-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_guidance_redirects_to_childcare_training_details_for_eyfs_applicant(self):
        self.create_eyfs_applicant()

        response = self.client.post(reverse('Childcare-Training-Guidance-View') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingDetailsView.as_view().__name__)

    def test_can_render_childcare_training_details_page(self):
        response = self.client.get(reverse('Childcare-Training-Details-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingDetailsView.as_view().__name__)

    def test_valid_post_request_to_childcare_training_redirects_to_training_certificate_page(self):
        self.create_eyfs_applicant()

        response = self.client.post(reverse('Childcare-Training-Details-View') + self.url_suffix,
                                    data={
                                        'eyfs_course_name': 'Horses for Courses',
                                        'eyfs_course_date_0': '01',
                                        'eyfs_course_date_1': '01',
                                        'eyfs_course_date_2': '2018',
                                    })

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingCertificateView.as_view().__name__)

    def test_entering_no_course_title_raises_validation_error(self):
        self.create_eyfs_applicant()

        response = self.client.post(reverse('Childcare-Training-Details-View') + self.url_suffix,
                                    data={
                                        'eyfs_course_name': '',
                                        'eyfs_course_date_0': '01',
                                        'eyfs_course_date_1': '01',
                                        'eyfs_course_date_2': '2018',
                                    })

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingDetailsView.as_view().__name__)
        self.assertFormError(response, 'form', 'eyfs_course_name', 'Please enter the title of the course')

    def test_entering_no_course_date_raises_validation_error(self):
        self.create_eyfs_applicant()

        response = self.client.post(reverse('Childcare-Training-Details-View') + self.url_suffix,
                                    data={
                                        'eyfs_course_name': 'Horses for Courses',
                                        'eyfs_course_date_0': '',
                                        'eyfs_course_date_1': '',
                                        'eyfs_course_date_2': '',
                                    })

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingDetailsView.as_view().__name__)
        self.assertFormError(response, 'form', 'eyfs_course_date', 'Please enter the full date, including the day, month and year')

    @parameterise_by_applicant_type
    def test_post_request_to_training_certificate_redirects_to_summary_page(self):
        response = self.client.post(reverse('Childcare-Training-Certificate-View') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, ChildcareTrainingSummaryView.as_view().__name__)

    @parameterise_by_applicant_type
    def test_can_render_summary_page(self):
        response = self.client.get(reverse('Childcare-Training-Summary-View') + self.url_suffix)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.resolver_match.func.__name__, ChildcareTrainingSummaryView.as_view().__name__)

    @parameterise_by_applicant_type
    def test_post_to_summary_redirects_to_task_list_with_done_task_status(self):
        response = self.client.post(reverse('Childcare-Training-Summary-View') + self.url_suffix)

        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, task_list.__name__)
        self.assertEqual(models.Application.objects.get(pk=self.app_id).childcare_training_status, 'COMPLETED')
