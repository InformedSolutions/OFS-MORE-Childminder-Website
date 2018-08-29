import datetime
import time

from django.test import TestCase
from uuid import UUID
from django.urls import reverse

from ...utils import build_url
from ...views import magic_link
from ...models import Application, UserDetails
import uuid


class TestLoginLogic(TestCase):
    magic_link_str = None
    app_details = {
        'application_id': None,
        'login_details_status': 'STARTED',
        'personal_details_status': 'NOT_STARTED',
        'childcare_type_status': 'NOT_STARTED',
        'first_aid_training_status': 'NOT_STARTED',
        'childcare_training_status': 'NOT_STARTED',
        'criminal_record_check_status': 'NOT_STARTED',
        'health_status': 'NOT_STARTED',
        'references_status': 'NOT_STARTED',
        'people_in_home_status': 'NOT_STARTED',
        'declarations_status': 'NOT_STARTED',
    }

    user_details = {
        'application_id': None,
        'login_id': str(uuid.uuid4()),
        'email': '',
        'mobile_number': '',
        'add_phone_number': '',
        'email_expiry_date': None,
        'sms_expiry_date': int(time.time()),
        'magic_link_email': None,
        'magic_link_sms': ''
    }

    def setUp(self):
        app_id = str(uuid.uuid4())
        self.app_details['application_id'] = app_id

        self.magic_link_str = str(magic_link.generate_random(12, "link"))
        self.user_details['magic_link_email'] = self.magic_link_str

    def test_validation_no_details_within_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        self.user_details['email_expiry_date'] = int(time.time())
        self.user_details['mobile_number'] = ''
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + self.magic_link_str + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/account/phone/' in response.url)

    def test_link_expired_no_details_outside_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        # set expiry date to yesterday (90000 seconds is 25 hours)
        self.user_details['email_expiry_date'] = int(time.time()) - 90000
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + self.magic_link_str + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/link-expired/' in response.url)

    def test_link_expired_with_details_within_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        self.user_details['email_expiry_date'] = int(time.time())
        self.user_details['mobile_number'] = '07123456789'
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + self.magic_link_str + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/security-code/' in response.url)

    def test_link_expired_with_details_outside_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        # set expiry date to yesterday (90000 seconds is 25 hours)
        self.user_details['email_expiry_date'] = int(time.time()) - 90000
        self.user_details['mobile_number'] = '07123456789'
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + self.magic_link_str + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/link-expired/' in response.url)

    def test_link_expired_already_been_used_within_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        self.user_details['email_expiry_date'] = int(time.time())
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + str(magic_link.generate_random(12, "link")) + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/link-used/' in response.url)

    def test_link_expired_already_been_used_outside_24_hours(self):
        application = Application.objects.create(**self.app_details)
        self.user_details['application_id'] = application
        # set expiry date to yesterday (90000 seconds is 25 hours)
        self.user_details['email_expiry_date'] = int(time.time()) - 90000
        UserDetails.objects.create(**self.user_details)

        response = self.client.get('/childminder/validate/' + str(magic_link.generate_random(12, "link")) + "/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue('/link-used/' in response.url)
