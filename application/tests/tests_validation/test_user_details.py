"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_validation.py --
@author: Informed Solutions
"""

import re

from django.conf import settings
from django.test import TestCase

from ...business_logic import convert_mobile_to_notify_standard, \
    childminder_references_and_user_email_duplication_check

def testing_email(test_email):
    return re.match(settings.REGEX['EMAIL'], test_email)


def testing_mobile_number(test_mobile_number):
    return re.match(settings.REGEX['MOBILE'], test_mobile_number)


def testing_phone_number(test_phone_number):
    return re.match(settings.REGEX['PHONE'], test_phone_number)


def testing_number_length(test_phone_number):
    return len(test_phone_number) == 11

def testing_convert_mobile(test_mobile_numbers):
    return convert_mobile_to_notify_standard(test_mobile_numbers["original"]) == test_mobile_numbers["result"]


def testing_duplicate_email(test_email_1,test_email_2):
    return childminder_references_and_user_email_duplication_check(test_email_1, test_email_2)


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

        self.correct_duplicate_emails = [
            {
                "1": "test@gmail.com",
                "2": "different@lineone.biz",
            },
            {
                "1": "",
                "2": "hardtothinkofemails@jurassicpark.gov.uk",
            },
            {
                "1": "alrightshows@over.com",
                "2": "",
            },
            {
                "1": "itwasfunwhileit@lasted.com",
                "2": "ohwaitihavetowrite@incorrecttoo.com",
            },
            {
                "1": None,
                "2": "ihadtoduplicateemails@sigh.gov.uk",
            },
            {
                "1": "alrightshows@over.com",
                "2": None,
            },
        ]

        self.incorrect_duplicate_emails = [
            {
                "1": "hiagain@gmail.com",
                "2": "hiagain@gmail.com",
            },
            {
                "1": "different@bing.co.uk",
                "2": "different@bing.co.uk",
            },
            {
                "1": "",
                "2": "",
            },
            {
                "1": None,
                "2": None,
            },
        ]

        self.convert_mobiles = [
            {
                "original": "+447398378738",
                "result": "07398378738"
            },
            {
                "original": "00447398378233",
                "result": "07398378233"
            },
            {
                "original": "07398378233",
                "result": "07398378233"
            },
            {
                "original": "",
                "result": ""
            }
        ]

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

    def test_correct_duplicate_emails(self):
        for emails in self.correct_duplicate_emails:
            assert (testing_duplicate_email(emails['1'], emails['2']) is True)

    def test_incorrect_duplicate_emails(self):
        for emails in self.incorrect_duplicate_emails:
            assert (testing_duplicate_email(emails['1'], emails['2']) is False)

    def test_convert_mobile(self):
        for mobile in self.convert_mobiles:
            assert(testing_convert_mobile(mobile) is True)
