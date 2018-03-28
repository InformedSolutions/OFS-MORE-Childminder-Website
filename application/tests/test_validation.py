"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_validation.py --

@author: Informed Solutions
"""

import re

from datetime import date

from django.test import TestCase


class TestUserdetailsValidation(TestCase):

    def test_correct_email(self):
        test_email = 'erik.odense@gmail.com'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is not None)

    def test_correct_email2(self):
        test_email = 'erikodense123@gmail.com'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is not None)

    def test_correct_email3(self):
        test_email = 'erik.tolstrup.odense@gmail.com'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is not None)

    def test_incorrect_email(self):
        test_email = 'erik.odense'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is None)

    def test_incorrect_email2(self):
        test_email = 'erik.odense@'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is None)

    def test_incorrect_email3(self):
        test_email = 'erik.odense@gmail'
        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is None)

    # Test validation for incorrect email
    def test_incorrect_email4(self):
        test_email = 'erik.odense@gmail.'

        assert (re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", test_email) is None)

    def test_correct_mobile_number(self):
        test_mobile_number = '07783446526'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is not None)

    # Test validation for incorrect mobile number
    def test_incorrect_mobile_number(self):
        test_mobile_number = '7783446526'

        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number2(self):
        test_mobile_number = '08783446526'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number3(self):
        test_mobile_number = '0778344652645677754'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number4(self):
        test_mobile_number = 'dfasdggregas'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number5(self):
        test_mobile_number = 'dsfdsf13'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number6(self):
        test_mobile_number = '0778abcdrewr'
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_incorrect_mobile_number7(self):
        test_mobile_number = "07783'4352"
        assert (re.match("^(07\d{8,12}|447\d{7,11})$", test_mobile_number) is None)

    def test_correct_mobile_number_length(self):
        test_mobile_number = '0778344652645677754'
        assert (len(test_mobile_number) > 11)

    def test_incorrect_mobile_number_too_long(self):
        test_mobile_number = '07783446526'
        assert (len(test_mobile_number) <= 11)

    def test_correct_phone_number(self):
        test_phone_number = '0161445627'
        assert (re.match("^(0\d{8,12}|447\d{7,11})$", test_phone_number) is not None)

    def test_incorrect_phone_number(self):
        test_phone_number = '161445627'
        assert (re.match("^(0\d{8,12}|447\d{7,11})$", test_phone_number) is None)


class TestPersonalDetailsValidation(TestCase):

    def test_correct_name(self):
        test_name = 'Erik'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name2(self):
        test_name = 'Anne-Marie'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name3(self):
        test_name = 'erik'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name4(self):
        test_name = 'anne-marie'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name5(self):
        test_name = 'Eun Ji'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name6(self):
        test_name = 'Gülay'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_correct_name7(self):
        test_name = 'Anthí'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is not None)

    def test_incorrect_name(self):
        test_name = '1234'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name2(self):
        test_name = '1234a'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name3(self):
        test_name = '1234A'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name4(self):
        test_name = '1234-'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name5(self):
        test_name = '1234-a'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name6(self):
        test_name = '1234-A'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

    def test_incorrect_name7(self):
        test_name = '1234-Aa'
        assert (re.match("^[A-zÀ-ÿ- ]+$", test_name) is None)

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


class TestDBSCheckValidation(TestCase):

    def test_invalid_dbs_certificate_number(self):
        test_dbs_certificate_number = 12345612345678
        assert (len(str(test_dbs_certificate_number)) > 12)

    def test_invalid_dbs_certificate_number2(self):
        test_dbs_certificate_number = 123456
        assert (len(str(test_dbs_certificate_number)) < 12)


class TestPaymentValidation(TestCase):

    def test_valid_visa_number(self):
        test_visa_number = '4444333322221111'
        assert (re.match("^4[0-9]{12}(?:[0-9]{3})?$", test_visa_number) is not None)

    def test_invalid_visa_number(self):
        test_visa_number = '444433332222111a'
        assert (re.match("^4[0-9]{12}(?:[0-9]{3})?$", test_visa_number) is None)

    def test_invalid_visa_number2(self):
        test_visa_number = '444433'
        assert (re.match("^4[0-9]{12}(?:[0-9]{3})?$", test_visa_number) is None)

    def test_invalid_visa_number3(self):
        test_visa_number = '444433332222111?'
        assert (re.match("^4[0-9]{12}(?:[0-9]{3})?$", test_visa_number) is None)

    def test_invalid_visa_number4(self):
        test_visa_number = '4444333322221111111'
        assert (re.match("^4[0-9]{12}(?:[0-9]{3})?$", test_visa_number) is None)

    def test_valid_mastercard_number(self):
        test_mastercard_number = '5105105105105100'
        assert (re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                         test_mastercard_number) is not None)

    def test_invalid_mastercard_number(self):
        test_mastercard_number = '5105105'
        assert (re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                         test_mastercard_number) is None)

    def test_invalid_mastercard_number2(self):
        test_mastercard_number = '510510510510510a'
        assert (re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                         test_mastercard_number) is None)

    def test_invalid_mastercard_number3(self):
        test_mastercard_number = '510510510510510?'
        assert (re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                         test_mastercard_number) is None)

    def test_invalid_mastercard_number4(self):
        test_mastercard_number = '51051051051051000'
        assert (re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                         test_mastercard_number) is None)

    def test_valid_american_express_number(self):
        test_american_express_number = '378282246310005'
        assert (re.match("^3[47][0-9]{13}$", test_american_express_number) is not None)

    def test_invalid_american_express_number(self):
        test_american_express_number = '3782822'
        assert (re.match("^3[47][0-9]{13}$", test_american_express_number) is None)

    def test_invalid_american_express_number2(self):
        test_american_express_number = '37828224631000a'
        assert (re.match("^3[47][0-9]{13}$", test_american_express_number) is None)

    def test_invalid_american_express_number3(self):
        test_american_express_number = '37828224631000?'
        assert (re.match("^3[47][0-9]{13}$", test_american_express_number) is None)

    def test_invalid_american_express_number4(self):
        test_american_express_number = '378282246310005097533568'
        assert (re.match("^3[47][0-9]{13}$", test_american_express_number) is None)

    def test_valid_maestro_number(self):
        test_maestro_number = '6759649826438453'
        assert (re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", test_maestro_number) is not None)

    def test_invalid_maestro_number(self):
        test_maestro_number = '675964982643845a'
        assert (re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", test_maestro_number) is None)

    def test_invalid_maestro_number2(self):
        test_maestro_number = '675964982643845?'
        assert (re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", test_maestro_number) is None)

    def test_invalid_maestro_number3(self):
        test_maestro_number = '6759649826438453212455452132345445'
        assert (re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", test_maestro_number) is None)

    def test_invalid_maestro_number4(self):
        test_maestro_number = '675964'
        assert (re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", test_maestro_number) is None)

    def test_valid_security_code(self):
        test_security_code = '123'
        assert (re.match("^[0-9]{3,4}$", test_security_code) is not None)

    def test_invalid_security_code(self):
        test_security_code = '123445435346'
        assert (re.match("^[0-9]{3,4}$", test_security_code) is None)

    def test_invalid_security_code2(self):
        test_security_code = '12a'
        assert (re.match("^[0-9]{3,4}$", test_security_code) is None)

    def test_invalid_security_code3(self):
        test_security_code = '12?'
        assert (re.match("^[0-9]{3,4}$", test_security_code) is None)

    def test_invalid_security_code4(self):
        test_security_code = '1'
        assert (re.match("^[0-9]{3,4}$", test_security_code) is None)
