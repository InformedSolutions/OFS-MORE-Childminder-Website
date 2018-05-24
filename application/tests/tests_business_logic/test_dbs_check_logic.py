import datetime

from django.test import TestCase
from uuid import UUID

from ...models import Application, CriminalRecordCheck, UserDetails


class TestDBSCheckLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        CriminalRecordCheck.objects.filter(application_id=test_application_id).delete()
        assert (CriminalRecordCheck.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        CriminalRecordCheck.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
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
        user = UserDetails.objects.create(
            application_id=test_app,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        test_criminal_record_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        CriminalRecordCheck.objects.create(
            criminal_record_id=(UUID(test_criminal_record_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            dbs_certificate_number='123456789012',
            cautions_convictions='True'
        )
        assert (CriminalRecordCheck.objects.filter(application_id=test_application_id).count() > 0)

    def delete(self):
        CriminalRecordCheck.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()

