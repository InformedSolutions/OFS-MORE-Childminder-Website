from unittest.mock import patch, Mock

from django.test import tag, TestCase

from application import models
from application.forms.PITH_forms import PITHDBSCheckForm, PITHDBSTypeOfCheckForm


@tag('unit')
class PITHAdultDetailsFormUnitTests(TestCase):
    pass


mock_dbs_read = Mock()


@patch('application.dbs.read', new=mock_dbs_read)
@tag('unit')
class PITHAdultDBSFormUnitTests(TestCase):

    def setUp(self):
        self.application = models.Application.objects.create()
        self.crim_rec_check = models.CriminalRecordCheck.objects.create(
            application_id=self.application,
            dbs_certificate_number='123456789012',
        )
        self.adult_in_home = models.AdultInHome.objects.create(
            application_id=self.application,
            birth_day=1, birth_month=7, birth_year=1975
        )
        self.field_name = 'dbs_certificate_number{}'.format(self.adult_in_home.pk)

        self.mock_dbs_response = Mock()
        self.mock_dbs_response.status_code = 404
        mock_dbs_read.return_value = self.mock_dbs_response
        mock_dbs_read.reset_mock()
        # due to a bug in unittest.mock, attribute deletion must be done _after_ reset
        del self.mock_dbs_response.record

    # ---------------

    def test_valid_if_dbs_number_ok(self):

        self.mock_dbs_response.status_code = 200
        self.mock_dbs_response.record = {
            'certificate_number': '123456789013',
            'date_of_issue': '2017-10-01',
            'date_of_birth': '1975-07-01',
            'certificate_information': '',
        }

        form = self.make_form('123456789013')

        valid = form.is_valid()

        self.assertTrue(valid)

    def test_invalid_if_dbs_number_contains_non_numeric(self):

        form = self.make_form('12345x789012')

        valid = form.is_valid()
        errors = form.errors

        self.assertFalse(valid)
        self.assertEqual(1, len(errors))
        self.assertEqual(1, len(errors[self.field_name]))

    def test_invalid_if_dbs_number_is_shorter_than_twelve_digits(self):

        form = self.make_form('12345678901')

        valid = form.is_valid()
        errors = form.errors

        self.assertFalse(valid)
        self.assertEqual(1, len(errors))
        self.assertEqual(1, len(errors[self.field_name]))

    def test_invalid_if_dbs_number_is_longer_than_twelve_digits(self):

        form = self.make_form('1234567890123')

        valid = form.is_valid()
        errors = form.errors

        self.assertFalse(valid)
        self.assertEqual(1, len(errors))
        self.assertEqual(1, len(errors[self.field_name]))

    def test_invalid_if_dbs_number_same_as_applicant(self):

        form = self.make_form('123456789012')

        valid = form.is_valid()
        errors = form.errors

        self.assertFalse(valid)
        self.assertEqual(1, len(errors))
        self.assertEqual(1, len(errors[self.field_name]))

    def test_invalid_if_dbs_number_corresponds_to_certificate_with_different_date_of_birth(self):

        self.mock_dbs_response.status_code = 200
        self.mock_dbs_response.record = {
            'certificate_number': '123456789013',
            'date_of_issue': '2017-10-01',
            'date_of_birth': '1976-02-02',
            'certificate_information': '',
        }

        form = self.make_form('123456789013')

        valid = form.is_valid()
        errors = form.errors

        self.assertFalse(valid)
        self.assertEqual(1, len(errors))
        self.assertEqual(1, len(errors[self.field_name]))

    # -----------

    def make_form(self, dbs_number):
        return PITHDBSCheckForm({self.field_name: dbs_number},
                                id=self.application.pk, adult=self.adult_in_home, dbs_field='dbs_certificate_number')


@tag('unit')
class PITHAdultDBSTypeOfCheckFormUnitTests(TestCase):

    def setUp(self):
        self.application = models.Application.objects.create()
        self.adult_in_home = models.AdultInHome.objects.create(
            application_id=self.application,
            birth_day=1, birth_month=7, birth_year=1975
        )
        self.enhanced_check_field_name = 'enhanced_check{}'.format(self.adult_in_home.pk)
        self.on_update_field_name = 'on_update{}'.format(self.adult_in_home.pk)

    # ---------------

    def test_valid_if_ask_enhanced_check_and_enhanced_check_answered_no(self):

        form = self.make_form(ask_if_enhanced=True, enhanced_check=False)

        valid = form.is_valid()

        self.assertTrue(valid)

    def test_valid_if_ask_enhanced_check_enhanced_check_answered_yes_and_on_update_answered(self):

        form = self.make_form(ask_if_enhanced=True, enhanced_check=True, on_update=False)

        valid = form.is_valid()

        self.assertTrue(valid)

    def test_valid_if_not_ask_enhanced_check_and_on_update_answered(self):

        form = self.make_form(ask_if_enhanced=False, on_update=True)

        valid = form.is_valid()

        self.assertTrue(valid)

    def test_invalid_if_ask_enhanced_check_and_enhanced_check_not_answered(self):

        form = self.make_form(ask_if_enhanced=True)

        valid = form.is_valid()

        self.assertFalse(valid)
        self.assertEqual(1, len(form.errors))
        self.assertEqual(1, len(form.errors[self.enhanced_check_field_name]))

    def test_invalid_if_ask_enhanced_check_enhanced_check_answered_yes_and_on_update_not_answered(self):

        form = self.make_form(ask_if_enhanced=True, enhanced_check=True)

        valid = form.is_valid()

        self.assertFalse(valid)
        self.assertEqual(1, len(form.errors))
        self.assertEqual(1, len(form.errors[self.on_update_field_name]))

    def test_invalid_if_not_ask_enhanced_check_and_on_update_not_answered(self):

        form = self.make_form(ask_if_enhanced=False)

        valid = form.is_valid()

        self.assertFalse(valid)
        self.assertEqual(1, len(form.errors))
        self.assertEqual(1, len(form.errors[self.on_update_field_name]))

    # ---------------

    def make_form(self, ask_if_enhanced, enhanced_check=None, on_update=None):
        data = {}
        if enhanced_check is not None:
            data[self.enhanced_check_field_name] = str(enhanced_check)
        if on_update is not None:
            data[self.on_update_field_name] = str(on_update)
        return PITHDBSTypeOfCheckForm(data,
                                      id=self.application.pk, adult=self.adult_in_home,
                                      ask_if_enhanced_check=ask_if_enhanced, enhanced_check_field='enhanced_check',
                                      on_update_field='on_update')


@tag('unit')
class PITHChildDetailsFormUnitTests(TestCase):
    pass


@tag('unit')
class PITHOwnChildrenDetailsFormUnitTests(TestCase):
    pass

