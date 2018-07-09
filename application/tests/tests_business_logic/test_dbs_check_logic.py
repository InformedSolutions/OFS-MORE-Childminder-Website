import datetime

from django.test import TestCase, Client, modify_settings
from uuid import UUID

from django.urls import reverse

from ...models import Application, CriminalRecordCheck, UserDetails, AdultInHome
from ...business_logic import new_dbs_numbers_is_valid


class TestDBSCheckLogic(TestCase):

    test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
    test_childcare_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
    test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
    test_criminal_record_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
    test_adult_id = 'b81e5479-217f-4cec-8442-7ee3e88ab392'
    test_adult_2_id = 'b58e3405-71a8-4619-a802-61ebf6aba3b8'
    test_application = None
    test_criminal_record = None
    test_login = None
    test_childminder_dbs_number = '123456789011'
    test_household_member_1_dbs_number = '123456789012'
    test_household_member_2_dbs_number = '123456789013'

    # Clients for HTTP level tests
    client = Client()

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        CriminalRecordCheck.objects.filter(application_id=test_application_id).delete()
        assert (CriminalRecordCheck.objects.filter(application_id=test_application_id).count() == 0)

    def setUp(self):
        CriminalRecordCheck.objects.filter(application_id=self.test_application_id).delete()
        Application.objects.filter(application_id=self.test_application_id).delete()
        UserDetails.objects.filter(login_id=self.test_login_id).delete()

        self.test_application = Application.objects.create(
            application_id=(UUID(self.test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )

        self.test_login = UserDetails.objects.create(
            application_id=self.test_application,
            login_id=(UUID(self.test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )

        self.test_criminal_record = CriminalRecordCheck.objects.create(
            criminal_record_id=(UUID(self.test_criminal_record_id)),
            application_id=Application.objects.get(application_id=self.test_application_id),
            dbs_certificate_number='',
            cautions_convictions='True'
        )

        assert (CriminalRecordCheck.objects.filter(application_id=self.test_application_id).count() > 0)

    def delete(self):
        CriminalRecordCheck.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()

    def test_dbs_numbers_deemed_unique_when_only_childminder_present(self):
        dbs_uniqueness_check_result = new_dbs_numbers_is_valid(self.test_application, self.test_childminder_dbs_number)
        self.assertTrue(dbs_uniqueness_check_result.dbs_numbers_unique)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_childminder_dbs)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_household_member_dbs)

    def test_dbs_numbers_deemed_unique_when_childminder_and_single_household_member_present(self):

        # Attach one test adult to the application with a differing DBS number
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        dbs_uniqueness_check_result = new_dbs_numbers_is_valid(self.test_application, self.test_childminder_dbs_number)
        self.assertTrue(dbs_uniqueness_check_result.dbs_numbers_unique)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_childminder_dbs)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_household_member_dbs)

    def test_dbs_numbers_deemed_unique_when_childminder_and_multiple_household_member_present(self):

        # Attach multiple test adults to the application with differing DBS numbers
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=2,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_2_dbs_number
        )

        dbs_uniqueness_check_result = new_dbs_numbers_is_valid(self.test_application, self.test_childminder_dbs_number)
        self.assertTrue(dbs_uniqueness_check_result.dbs_numbers_unique)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_childminder_dbs)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_household_member_dbs)

    def test_dbs_numbers_not_deemed_unique_when_childminder_dbs_duplicated(self):
        self.test_criminal_record.dbs_certificate_number = self.test_childminder_dbs_number
        self.test_criminal_record.save()

        dbs_uniqueness_check_result = new_dbs_numbers_is_valid(self.test_application,
                                                               self.test_childminder_dbs_number)
        self.assertFalse(dbs_uniqueness_check_result.dbs_numbers_unique)
        self.assertTrue(dbs_uniqueness_check_result.duplicates_childminder_dbs)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_household_member_dbs)

    def test_dbs_numbers_not_deemed_unique_when_household_member_dbs_duplicated(self):

        # Attach multiple test adults to the application with differing matching numbers
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        dbs_uniqueness_check_result = new_dbs_numbers_is_valid(self.test_application,
                                                               self.test_household_member_1_dbs_number)
        self.assertFalse(dbs_uniqueness_check_result.dbs_numbers_unique)
        self.assertFalse(dbs_uniqueness_check_result.duplicates_childminder_dbs)
        self.assertTrue(dbs_uniqueness_check_result.duplicates_household_member_dbs)

        # Test is to assert first adult in home is identified as the duplicate record
        self.assertEqual(dbs_uniqueness_check_result.duplicate_entry_index, 1)

    # HTTP web tier tests for DBS task completion

    @modify_settings(MIDDLEWARE={
        'remove': [
             'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_dbs_numbers_deemed_unique_when_only_childminder_present(self):
        response = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        expected_redirect_url = reverse('DBS-Check-Summary-View') + '?id=' + self.test_application_id

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_dbs_numbers_deemed_unique_when_childminder_and_single_household_member_present(self):

        # Attach one test adult to the application with a differing DBS number before POSTing page
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        response = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        expected_redirect_url = reverse('DBS-Check-Summary-View') + '?id=' + self.test_application_id

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_dbs_numbers_deemed_unique_when_childminder_and_multiple_household_member_present(self):
        # Attach multiple test adults to the application with differing DBS numbers
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=2,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_2_dbs_number
        )

        response = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        expected_redirect_url = reverse('DBS-Check-Summary-View') + '?id=' + self.test_application_id

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_childminder_can_update_dbs_to_same_number(self):

        self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_household_member_1_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        response = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_household_member_1_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        expected_redirect_url = reverse('DBS-Check-Summary-View') + '?id=' + self.test_application_id

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_error_raised_when_childminder_dbs_duplicates_household_member(self):
        # Attach multiple test adults to the application with differing DBS numbers
        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_1_dbs_number
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=2,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_2_dbs_number
        )

        response = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_household_member_1_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors']['dbs_certificate_number'][0],
                         'Please enter a different DBS number. You entered this number for someone in your childcare location')

    # HTTP web tier tests for Household members task vompletion

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_error_raised_when_household_member_duplicates_childminder(self):
        self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=self.test_household_member_2_dbs_number
        )

        response = self.client.post(
            reverse('Other-People-Adult-DBS-View'),
            {
                'id': self.test_application_id,
                'adults': 1,
                '1-dbs_certificate_number': self.test_childminder_dbs_number
            },
            follow=True
        )

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors']['dbs_certificate_number'][0],
                         'Please enter a DBS number that is different from your own')

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_no_error_raised_when_household_members_dbs_numbers_added_which_differ_to_childminder(self):
        self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=''
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=2,
            birth_day=22,
            birth_month=2,
            birth_year=1991,
            dbs_certificate_number=''
        )

        response = self.client.post(
            reverse('Other-People-Adult-DBS-View'),
            {
                'id': self.test_application_id,
                'adults': 2,
                '1-dbs_certificate_number': self.test_household_member_1_dbs_number,
                '2-dbs_certificate_number': self.test_household_member_2_dbs_number
            },
            follow=True
        )

        expected_redirect_url = reverse('Other-People-Children-Question-View') \
                                + '?id=' + self.test_application_id + '&adults=2'

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_redirect_url)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_http_error_raised_when_household_member_duplicates_other_household_member(self):
        self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.test_application_id,
                'dbs_certificate_number': self.test_childminder_dbs_number,
                'cautions_convictions': False
            },
            follow=True
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_id)),
            application_id=self.test_application,
            adult=1,
            birth_day=22,
            birth_month=1,
            birth_year=1991,
            dbs_certificate_number=''
        )

        AdultInHome.objects.create(
            adult_id=(UUID(self.test_adult_2_id)),
            application_id=self.test_application,
            adult=2,
            birth_day=22,
            birth_month=2,
            birth_year=1991,
            dbs_certificate_number=''
        )

        response = self.client.post(
            reverse('Other-People-Adult-DBS-View'),
            {
                'id': self.test_application_id,
                'adults': 2,
                '1-dbs_certificate_number': self.test_household_member_1_dbs_number,
                '2-dbs_certificate_number': self.test_household_member_1_dbs_number
            },
            follow=True
        )

        # Assert user is redirected on to check answers page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors']['dbs_certificate_number'][0],
                         'Please enter a different DBS number for each person')

