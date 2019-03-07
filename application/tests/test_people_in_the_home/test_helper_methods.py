import unittest

from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from django.test import tag, TestCase

from application.business_logic import DBSStatus, find_dbs_status, date_issued_within_three_months
from application import models


mock_dbs_read = Mock()


@patch('application.dbs.read', new=mock_dbs_read)
@tag('unit')
class FindDBSStatusUnitTests(TestCase):

    def setUp(self):

        self.application = models.Application.objects.create()

        self.dbs_model = models.AdultInHome.objects.create(
            application_id=self.application,
            birth_day=1, birth_month=8, birth_year=1976,
        )
        self.dob_model = self.dbs_model

        self.mock_dbs_response = Mock()
        self.mock_dbs_response.status_code = 404
        mock_dbs_read.return_value = self.mock_dbs_response
        mock_dbs_read.reset_mock()
        # due to unittest.mock bug, attribute deletion must be done _after_ reset_mock
        del self.mock_dbs_response.record

    # ---------

    def test_returns_NEED_DBS_NUMBER_if_no_dbs_number_present(self):

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_DBS_NUMBER, result)

    def test_returns_DOB_MISMATCH_if_dbs_number_specified_and_corresponds_to_record_with_different_dob(self):

        self.mock_dbs_response.status_code = 200
        self.mock_dbs_response.record = {
            'certificate_number': '123456789012',
            'date_of_issue': (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d'),
            'date_of_birth': '1975-03-05',
            'certificate_information': 'foo',
        }

        result = find_dbs_status(self.dbs_model, self.dob_model, dbs_certificate_number='123456789012')

        self.assertEqual(DBSStatus.DOB_MISMATCH, result)

    def test_records_dbs_info_if_dbs_number_specified_and_record_not_found(self):

        find_dbs_status(self.dbs_model, self.dob_model, dbs_certificate_number='123456789012')

        refetched_adult = models.AdultInHome.objects.get(pk=self.dbs_model.pk)
        self.assertEqual('123456789012', refetched_adult.dbs_certificate_number)
        self.assertEqual(False, refetched_adult.capita)

    def test_records_dbs_info_if_dbs_number_specified_and_record_found(self):

        self.mock_dbs_response.status_code = 200
        self.mock_dbs_response.record = {
            'certificate_number': '123456789012',
            'date_of_issue': (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d'),
            'date_of_birth': '1976-08-01',
            'certificate_information': 'foo',
        }

        find_dbs_status(self.dbs_model, self.dob_model, dbs_certificate_number='123456789012')

        refetched_adult = models.AdultInHome.objects.get(pk=self.dbs_model.pk)
        self.assertEqual('123456789012', refetched_adult.dbs_certificate_number)
        self.assertEqual(True, refetched_adult.capita)
        self.assertEqual(True, refetched_adult.within_three_months)

    def test_returns_OK_if_record_found_and_recent_enough(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = True
        self.dbs_model.within_three_months = True
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.OK, result)

    def test_returns_ASK_IF_ON_UPDATE_if_record_found_but_not_recent_enough_and_not_stated(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = True
        self.dbs_model.within_three_months = False
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_ASK_IF_ON_UPDATE, result)

    def test_returns_NEED_UPDATE_SERVICE_CHECK_if_record_found_but_not_recent_enough_and_stated_on_update(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = True
        self.dbs_model.within_three_months = False
        self.dbs_model.on_update = True
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_UPDATE_SERVICE_CHECK, result)

    def test_returns_NEED_UPDATE_SERVICE_SIGN_UP_if_record_found_but_not_recent_enough_and_stated_not_on_update(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = True
        self.dbs_model.within_three_months = False
        self.dbs_model.on_update = False
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP, result)

    def test_returns_NEED_ASK_IF_ENHANCED_CHECK_if_record_not_found_and_not_stated(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = False
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_ASK_IF_ENHANCED_CHECK, result)

    def test_returns_NEED_APPLY_FOR_NEW_if_record_not_found_and_stated_not_enhanced_check(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = False
        self.dbs_model.enhanced_check = False
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_APPLY_FOR_NEW, result)

    def test_returns_NEED_ASK_IF_ON_UPDATE_if_record_not_found_and_stated_enhanced_check_but_not_stated_on_update(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = False
        self.dbs_model.enhanced_check = True
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_ASK_IF_ON_UPDATE, result)

    def test_returns_NEED_UPDATE_SERVICE_CHECK_if_record_not_found_and_stated_enhanced_check_and_on_update(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = False
        self.dbs_model.enhanced_check = True
        self.dbs_model.on_update = True
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_UPDATE_SERVICE_CHECK, result)

    def test_returns_NEED_UPDATE_SERVICE_SIGN_UP_if_record_not_found_and_stated_enhanced_and_not_on_update(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.capita = False
        self.dbs_model.enhanced_check = True
        self.dbs_model.on_update = False
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model)

        self.assertEqual(DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP, result)

    def test_discards_old_dbs_info_when_dbs_certificate_number_specified(self):

        self.dbs_model.dbs_certificate_number = '123456789012'
        self.dbs_model.within_three_months = True
        self.dbs_model.capita = True
        self.dbs_model.enhanced_check = True
        self.dbs_model.on_update = True
        self.dbs_model.save()

        result = find_dbs_status(self.dbs_model, self.dob_model, dbs_certificate_number='123456789012')

        self.assertEqual(DBSStatus.NEED_ASK_IF_ENHANCED_CHECK, result)

        refetched_adult = models.AdultInHome.objects.get(application_id=self.application.pk)
        self.assertEqual(None, refetched_adult.within_three_months)
        self.assertEqual(False, refetched_adult.capita)
        self.assertEqual(None, refetched_adult.enhanced_check)
        self.assertEqual(None, refetched_adult.on_update)


# can't patch builtin attributes directly, so subclassing
class MockDatetime(datetime):

    mock_today = datetime(2019, 1, 15)

    @classmethod
    def today(cls):
        return cls.mock_today


@patch('application.business_logic.datetime', new=MockDatetime)
@tag('unit')
class DateIssuedWithinThreeMonthsUnitTests(unittest.TestCase):

    def test_returns_true_for_date_plus_one_three_months_ago(self):
        MockDatetime.mock_today = datetime(2019, 1, 15)
        result = date_issued_within_three_months(datetime(2018, 10, 16))
        self.assertTrue(result)

    def test_returns_false_for_date_minus_one_three_months_ago(self):
        MockDatetime.mock_today = datetime(2019, 1, 15)
        result = date_issued_within_three_months(datetime(2018, 10, 14))
        self.assertFalse(result)

    def test_returns_true_for_same_date_three_months_ago(self):
        MockDatetime.mock_today = datetime(2019, 1, 15)
        result = date_issued_within_three_months(datetime(2018, 10, 15))
        self.assertTrue(result)

    def test_returns_true_if_today_30th_and_date_is_last_day_of_30_day_month_three_months_ago(self):
        MockDatetime.mock_today = datetime(2018, 12, 30)
        result = date_issued_within_three_months(datetime(2018, 9, 30))
        self.assertTrue(result)

    def test_returns_true_if_today_31st_and_date_is_last_day_of_30_day_month_three_months_ago(self):
        MockDatetime.mock_today = datetime(2018, 12, 31)
        result = date_issued_within_three_months(datetime(2018, 9, 30))
        self.assertTrue(result)
