import datetime

from django.test import TestCase
from uuid import UUID

from ...models import ChildcareType, Application, UserDetails


class TestChildcareTypeLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        ChildcareType.objects.filter(application_id=test_application_id).delete()
        assert (ChildcareType.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
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
            order_code=None
        )
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            application_id=test_app,
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )

        test_childcare_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        ChildcareType.objects.create(
            childcare_id=(UUID(test_childcare_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            zero_to_five='True',
            five_to_eight='False',
            eight_plus='True'
        )
        assert (ChildcareType.objects.filter(application_id=test_application_id).count() > 0)

    def delete(self):
        ChildcareType.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
