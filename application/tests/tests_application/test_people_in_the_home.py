from unittest import mock

from django.test import TestCase
from django.urls import resolve, reverse

from application import models

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


class PeopleInTheHomeTestSuite(TestCase, ApplicationTestBase):

    def setUp(self):
        with mock.patch('application.views.magic_link.magic_link_confirmation_email') as magic_link_email_mock, \
                mock.patch('application.views.magic_link.magic_link_text') as magic_link_text_mock, \
                mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:

            notify_connection_test_mock.return_value.status_code = 201
            magic_link_email_mock.return_value.status_code = 201
            magic_link_text_mock.return_value.status_code = 201

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
        pass



