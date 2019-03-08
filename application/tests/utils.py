import unittest
from django.test import TestCase, modify_settings
from lxml import etree

from application import models


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class NoMiddlewareTestCase(TestCase):
    """Removes the need for authentication when performing test requests"""
    pass


# CamelCase naming to match unittest module
def assertXPath(response, xpath):
    """
    Asserts that content described by the given xpath expression can be found in the given response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    """
    result = _do_xpath(response, xpath)
    if result is None or (isinstance(result, list) and len(result) == 0):
        raise AssertionError('"{}" evaluated to {} but content expected'.format(xpath, repr(result)))


def assertNotXPath(response, xpath):
    """
    Asserts that no content can be found at the given xpath in the response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    """
    result = _do_xpath(response, xpath)
    if result is not None and not (isinstance(result, list) and len(result) == 0):
        raise AssertionError('"{}" evaluated to {} but no content expected'.format(xpath, repr(result)))


def assertXPathValue(response, xpath, expected_value):
    """
    Asserts that the given value can be found at the given xpath in the response's HTML

    :param response: The http response object
    :param xpath: An XPath expression to test for
    :param expected_value: The content expected to be found
    """
    result = _do_xpath(response, xpath)
    if expected_value not in result:
        raise AssertionError('Expected {} at "{}", but found {}'.format(repr(expected_value), xpath, repr(result)))


def assertXPathCount(response, xpath, expected_quantity):
    """
    Asserts that the given quantity of instances can be found in the response's HTML for the given xpath expression

    :param response: The http response object
    :param xpath: An XPath expression to test for
    :param expected_quantity: The number of instances expected to be found
    """
    result = _do_xpath(response, xpath)
    if len(result) != expected_quantity:
        raise AssertionError('Expected {} instances of "{}", found {}', expected_quantity, xpath, len(result))


def _do_xpath(response, xpath):
    tree = etree.fromstring(response.content, parser=etree.HTMLParser()).getroottree()
    return tree.xpath(xpath)


def assertView(response, expected_view_obj):
    expected_name = expected_view_obj if isinstance(expected_view_obj, str) else expected_view_obj.__name__
    actual_name = response.resolver_match.func.__name__
    if actual_name != expected_name:
        raise AssertionError('Expected view "{}", found view "{}"'.format(expected_name, actual_name))


def assertSummaryField(response, label, value, heading=None):
    """Raises assertion error if given field is not found on the page with the specified value

    :param response: the http response to check
    :param label: the expected text of the field label
    :param value: the expected text of the field value
    :param heading: (optional) the expected text of the heading the field is found under"""

    if heading is not None:
        assertXPath(response, _heading_xpath(heading))

    assertXPath(response, _field_xpath(label, heading))
    assertXPathValue(response, _field_value_xpath(label, heading), value)


def assertNotSummaryField(response, label, heading=None):
    """Raises assertion error if given field IS found on the page

    :param response: the http response to check
    :param label: the (un)expected text of the field label
    :param heading: (optional) the (un)expected text of the heading the field is (not) found under"""

    if heading is not None:
        assertXPath(response, _heading_xpath(heading))

    assertNotXPath(response, _field_xpath(label, heading))


def _heading_xpath(heading):
    return ("(//h1|//h2|//h3|//h4|//h5|//h6|//thead)"
            "/descendant-or-self::*[normalize-space(text())=\"{}\"]").format(heading)


def _field_xpath(label, heading=None):
    xpath = ""
    if heading is not None:
        xpath += _heading_xpath(heading)
        xpath += "/following::tbody[1]"
    xpath += "//td[normalize-space(text())=\"{}\"]".format(label)
    return xpath


def _field_value_xpath(label, heading=None):
    xpath = _field_xpath(label, heading)
    xpath += "/following-sibling::td[1]/text()"
    return 'normalize-space({})'.format(xpath)


def patch_for_setUp(test_case, *args, **kwargs):
    """
    Performs a unittest.mock.patch such that it will remain in place for the duration of a single test in the given
    TestCase before being undone. Suitable for invoking in a TestCase.setUp method.
    :param test_case: The TestCase instance
    :param args: positional arguments to pass to patch
    :param kwargs: keyword arguments to pass to patch
    :return: The result of the patch call, i.e. either a MagicMock or None
    """
    patcher = unittest.mock.patch(*args, **kwargs)
    test_case.addCleanup(patcher.stop)
    return patcher.start()


def patch_object_for_setUp(test_case, *args, **kwargs):
    """
    Performs a unittest.mock.patch.object such that it will remain in place for the duration of a single test in the
    given TestCase before being undone. Suitable for invoking in a TestCase.setUp method.
    :param test_case: The TestCase instance
    :param args: positional arguments to pass to patch.object
    :param kwargs: keyword arguments to pass to patch.object
    :return: The result of the patch.object call, i.e. either a MagicMock or None
    """
    patcher = unittest.mock.patch.object(*args, **kwargs)
    test_case.addCleanup(patcher.stop)
    return patcher.start()


def make_test_application():
    """
    Create an arbitrary childminder application for tests that don't require any specific field values,
    just that an application exists, or to use as a starting point before tweaking individual fields
    """

    application = models.Application.objects.create(
    )
    models.UserDetails.objects.create(
        application_id=application
    )
    applicant_personal_details = models.ApplicantPersonalDetails.objects.create(
        application_id=application
    )
    models.ApplicantName.objects.create(
        application_id=application,
        personal_detail_id=applicant_personal_details,
        current_name=True,
    )
    models.ApplicantHomeAddress.objects.create(
        application_id=application,
        personal_detail_id=applicant_personal_details,
        move_in_month=1, move_in_year=2001,
        current_address=True,
        childcare_address=True,
    )
    models.ChildcareType.objects.create(
        application_id=application,
        zero_to_five=True, five_to_eight=True, eight_plus=True,
    )
    models.AdultInHome.objects.create(
        application_id=application,
        birth_day=1, birth_month=2, birth_year=1983,
        adult=1,
    )
    models.FirstAidTraining.objects.create(
        application_id=application,
        course_day=1, course_month=2, course_year=2015,
    )
    models.CriminalRecordCheck.objects.create(
        application_id=application,
        certificate_information='',
    )
    models.ChildcareTraining.objects.create(
        application_id=application,
    )
    models.Reference.objects.create(
        application_id=application,
        reference=1,
        years_known=1, months_known=11,
    )
    models.Reference.objects.create(
        application_id=application,
        reference=2,
        years_known=2, months_known=10,
    )
    return application
