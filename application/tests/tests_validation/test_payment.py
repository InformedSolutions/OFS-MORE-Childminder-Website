import re

from django.conf import settings
from django.test import TestCase


class TestPaymentValidation(TestCase):

    def setUp(self):
        self.valid_visa = ['4444333322221111']
        self.invalid_visa = ['444433332222111a',
                             '444433',
                             '444433332222111?',
                             '4444333322221111111']

        self.valid_mastercard = ['5105105105105100']
        self.invalid_mastercard = ['5105105',
                                   '510510510510510a',
                                   '510510510510510?',
                                   '51051051051051000',
                                   ]

        self.valid_maestro = ['6759649826438453']
        self.invalid_maestro = ['675964',
                                '675964982643845a',
                                '6759649826438453212455452132345445',
                                '675964982643845?']

        self.valid_american_express = ['378282246310005']
        self.invalid_american_express = ['3782822',
                                         '37828224631000?',
                                         '378282246310005097533568',
                                         '37828224631000a']

        self.valid_security_number = ['123']
        self.invalid_security_number = ['1', '123445435346', '12a', '12?']

        super().setUp()

    @staticmethod
    def check_visa_number(number):
        return re.match(settings.REGEX['VISA'], number)

    @staticmethod
    def check_american_express_number(number):
        return re.match(settings.REGEX['AMERICAN_EXPRESS'], number)

    @staticmethod
    def check_maestro_number(number):
        return re.match(settings.REGEX['MAESTRO'], number)

    @staticmethod
    def check_mastercard_number(number):
        return re.match(settings.REGEX['MASTERCARD'], number)

    @staticmethod
    def check_card_security_number(number):
        return re.match(settings.REGEX['CARD_SECURITY_NUMBER'], number)

    def test_visa(self):
        for val in self.valid_visa:
            assert(self.check_visa_number(val) is not None)

        for inval in self.invalid_visa:
            assert(self.check_visa_number(inval) is None)

    def test_mastercard(self):
        for val in self.valid_mastercard:
            assert (self.check_mastercard_number(val) is not None)

        for inval in self.invalid_mastercard:
            assert (self.check_mastercard_number(inval) is None)

    def test_american_express(self):
        for val in self.valid_american_express:
            assert (self.check_american_express_number(val) is not None)

        for inval in self.invalid_american_express:
            assert (self.check_american_express_number(inval) is None)

    def test_maestro(self):
        for val in self.valid_maestro:
            assert (self.check_maestro_number(val) is not None)

        for inval in self.invalid_maestro:
            assert (self.check_maestro_number(inval) is None)

    def test_security_number(self):
        for val in self.valid_security_number:
            assert (self.check_card_security_number(val) is not None)

        for inval in self.invalid_security_number:
            assert (self.check_card_security_number(inval) is None)
