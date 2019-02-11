from django.test import TestCase, modify_settings
from lxml import etree


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