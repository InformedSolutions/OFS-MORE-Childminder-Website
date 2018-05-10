import re

from django.test import TestCase


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