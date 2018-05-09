from django.test import TestCase


class TestDBSCheckValidation(TestCase):

    def test_invalid_dbs_certificate_number(self):
        test_dbs_certificate_number = 12345612345678
        assert (len(str(test_dbs_certificate_number)) > 12)

    def test_invalid_dbs_certificate_number2(self):
        test_dbs_certificate_number = 123456
        assert (len(str(test_dbs_certificate_number)) < 12)