from unittest import mock

from django.test import TestCase, tag
from django.urls import reverse

from application import models
from application.utils import build_url

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


class PeopleInTheHomeTestSuite(TestCase):
    pass
