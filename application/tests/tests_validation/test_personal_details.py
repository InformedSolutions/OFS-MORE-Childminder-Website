import re

from datetime import date
from django.test import TestCase


class TestPersonalDetailsValidation(TestCase):

    def test_correct_name(self):
        test_name = 'Erik'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name2(self):
        test_name = 'Anne-Marie'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name3(self):
        test_name = 'erik'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name4(self):
        test_name = 'anne-marie'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name5(self):
        test_name = 'Eun Ji'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name6(self):
        test_name = 'Gülay'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name7(self):
        test_name = 'Anthí'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_correct_name8(self):
        test_name = 'O\'Brien'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is not None)

    def test_incorrect_name(self):
        test_name = '1234'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name2(self):
        test_name = '1234a'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name3(self):
        test_name = '1234A'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name4(self):
        test_name = '1234-'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name5(self):
        test_name = '1234-a'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name6(self):
        test_name = '1234-A'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_incorrect_name7(self):
        test_name = '1234-Aa'
        assert (re.match("^[A-zÀ-ÿ- ']+$", test_name) is None)

    def test_legal_age_to_childmind(self):
        test_applicant_dob = date(1995, 4, 20)
        test_date = date(2018, 1, 5)
        age = test_date.year - test_applicant_dob.year - (
                (test_date.month, test_date.day) < (test_applicant_dob.month, test_applicant_dob.day))
        assert (age > 18)

    def test_illegal_age_to_childmind(self):
        test_applicant_dob = date(2014, 2, 1)
        test_date = date(2018, 1, 5)
        age = test_date.year - test_applicant_dob.year - (
                (test_date.month, test_date.day) < (test_applicant_dob.month, test_applicant_dob.day))
        assert (age < 18)

    def test_address_string_that_is_too_long(self):
        test_string = 'LlanfairpwllgwyngyllgogerychwyrndrbwllllantisiliogogogochLlanfairpwllgwyngyllgogerychwyrndrbwllllantisiliogogogoch'
        assert (len(test_string) > 100)

    def test_address_string_that_is_not_too_long(self):
        test_string = 'Llanfairpwllgwyngyllgogerychwyrndrbwllllantisiliogogogoch'
        assert (len(test_string) <= 100)

    def test_valid_postcode(self):
        test_postcode = 'WA14 4PA'
        test_postcode_no_space = test_postcode.replace(" ", "")
        postcode_uppercase = test_postcode_no_space.upper()
        assert (re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is not None)

    def test_valid_postcode_without_space(self):
        test_postcode = 'WA144PA'
        test_postcode_no_space = test_postcode.replace(" ", "")
        postcode_uppercase = test_postcode_no_space.upper()
        assert (re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is not None)

    def test_invalid_postcode(self):
        test_postcode = '!%WA14'
        test_postcode_no_space = test_postcode.replace(" ", "")
        postcode_uppercase = test_postcode_no_space.upper()
        assert (re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None)

    def test_invalid_postcode_too_long(self):
        test_postcode = 'WA14 4PAAAAAA'
        test_postcode_no_space = test_postcode.replace(" ", "")
        postcode_uppercase = test_postcode_no_space.upper()
        assert (re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None)

    def test_invalid_postcode_too_long2(self):
        test_postcode = 'WA144PAAAAAA'
        test_postcode_no_space = test_postcode.replace(" ", "")
        postcode_uppercase = test_postcode_no_space.upper()
        assert (re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None)