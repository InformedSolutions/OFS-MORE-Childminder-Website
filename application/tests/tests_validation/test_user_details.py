"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_validation.py --
@author: Informed Solutions
"""

import re

from django.conf import settings
from django.test import TestCase


def testing_email(test_email):
    return re.match(settings.REGEX['EMAIL'], test_email)


def testing_mobile_number(test_mobile_number):
    return re.match(settings.REGEX['MOBILE'], test_mobile_number)


def testing_phone_number(test_phone_number):
    return re.match(settings.REGEX['PHONE'], test_phone_number)


def testing_number_length(test_phone_number):
    return len(test_phone_number) == 11


class TestUserDetailsValidation(TestCase):

    def setUp(self):
        super().setUp()
        self.correct_emails = ['erik.odense@gmail.com',
                               'erikodense123@gmail.com',
                               'erikodense123@gmail.com',
                               'erik.tolstrup.odense@gmail.com',
                               'erik.tolstrup.o\'dense@gmail.com']
        self.incorrect_emails = ['erik.odense',
                                 'erik.odense@',
                                 'erik.odense@gmail',
                                 'erik.odense@gmail.',
                                 'erik.o\'dense@gmail']

        self.correct_numbers = ['01398378738',
                                '07298373873',
                                '07398378738',
                                '07398378738',
                                '+447398378783',
                                '00447398378383']
        self.incorrect_numbers = ['161445627']

        self.correct_mobile = ['07783446526',
                               '07398378738',
                               '07777777777',
                               '+447398378738',
                               '00447398378738']
        self.incorrect_mobile = ['7783446526',
                                 '08783446526',
                                 '0778344652645677754',
                                 'dfasdggregas',
                                 'dsfdsf13',
                                 'dsfdsf13',
                                 '0778abcdrewr',
                                 "07783'4352",
                                 '077830056967',
                                 '0777777777777'
                                 '0783243294']

        self.incorrect_number_length = ['0778344652645677754', '0778344652644']
        self.correct_number_length = ['07397389736', '37317329736']

    def test_correct_emails(self):
        for email in self.correct_emails:
            assert (testing_email(email) is not None)

    def test_incorrect_emails(self):
        for email in self.incorrect_emails:
            assert (testing_email(email) is None)

    def test_correct_mobile(self):
        for mobile in self.correct_mobile:
            assert (testing_mobile_number(mobile) is not None)

    def test_incorrect_mobile(self):
        for mobile in self.incorrect_mobile:
            assert (testing_mobile_number(mobile) is None)

    def test_correct_number(self):
        for number in self.correct_numbers:
            assert (testing_phone_number(number) is not None)

    def test_incorrect_number(self):
        for number in self.incorrect_numbers:
            assert (testing_phone_number(number) is None)

    def test_correct_number_length(self):
        for number in self.correct_number_length:
            assert (testing_number_length(number) is True)

    def test_incorrect_number_length(self):
        for number in self.incorrect_number_length:
            assert (testing_number_length(number) is False)
