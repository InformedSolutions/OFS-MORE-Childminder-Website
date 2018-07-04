import datetime
import time

from django.test import TestCase
from uuid import UUID
from django.urls import reverse

from ...views import magic_link
from ...models import Application, UserDetails


class TestLoginLogic(TestCase):

    def test_link_expired_no_details_within_24_hours(self):
        test_application_id = 'f2c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        magic_link_str = str(magic_link.generate_random(12, "link"))
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='STARTED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='NOT_STARTED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='NOT_STARTED',
            criminal_record_check_status='NOT_STARTED',
            health_status='NOT_STARTED',
            references_status='NOT_STARTED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        user = UserDetails.objects.create(
            application_id=test_app,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=int(time.time()),
            sms_expiry_date=int(time.time()),
            magic_link_email=magic_link_str,
            magic_link_sms=''
        )

        response = self.client.get(reverse('Validate-Email') + '/?id=' + magic_link_str)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '')

    def test_link_expired_no_details_outside_24_hours(self):
        pass

    def test_link_expired_with_details_within_24_hours(self):
        pass

    def test_link_expired_with_details_outside_24_hours(self):
        pass

    def test_link_expired_already_ben_used_within_24_hours(self):
        pass

    def test_link_expired_already_been_used_outside_24_hours(self):
        pass

