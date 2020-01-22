import datetime

from django.test import TestCase
from uuid import UUID

from ...models import (ApplicantHomeAddress,
                       ApplicantName,
                       ApplicantPersonalDetails,
                       Application,
                       UserDetails)


class TestPersonalLogic(TestCase):

    def test_logic_to_create_new_dob_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_dob_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
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
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
        )
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() > 0)

    def test_logic_to_create_new_name_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantName.objects.filter(personal_detail_id=test_personal_detail_id).delete()
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() == 0)
        assert (ApplicantName.objects.filter(personal_detail_id=test_personal_detail_id).count() == 0)

    def test_logic_to_update_name_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantName.objects.filter(personal_detail_id=test_personal_detail_id).delete()
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
            childcare_training_status='COMPLETED',
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
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=test_personal_detail_id,
            application_id=Application.objects.get(pk=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_name_id = '6e09fe41-2b07-4177-a5e4-347b2515ea8e'
        ApplicantName.objects.create(
            name_id=test_name_id,
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            current_name='True',
            first_name='Erik',
            middle_names='Tolstrup',
            last_name='Odense'
        )
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() > 0)
        assert (ApplicantName.objects.filter(personal_detail_id=test_personal_detail_id).count() > 0)

    def test_logic_to_create_new_home_address_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_home_address_id = '11a3aef5-9e23-4216-b646-e6adccda4270'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(home_address_id=test_home_address_id, current_address=True).delete()
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() == 0)
        assert (ApplicantHomeAddress.objects.filter(home_address_id=test_home_address_id,
                                                    current_address=True).count() == 0)

    def test_logic_to_update_home_address_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id).delete()
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
            childcare_training_status='COMPLETED',
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
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_home_address_id = '11a3aef5-9e23-4216-b646-e6adccda4270'
        ApplicantHomeAddress.objects.create(
            home_address_id=(UUID(test_home_address_id)),
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            childcare_address=None,
            current_address=True,
        )
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() > 0)
        assert (ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id,
                                                    current_address=True).count() > 0)

    def test_logic_to_create_new_childcare_address_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id).delete()
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
            childcare_training_status='COMPLETED',
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
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_home_address_id = '11a3aef5-9e23-4216-b646-e6adccda4270'
        ApplicantHomeAddress.objects.create(
            home_address_id=(UUID(test_home_address_id)),
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            childcare_address=False,
            current_address=True,
        )
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(home_address_id=test_home_address_id, childcare_address=True).delete()
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() == 0)
        assert (ApplicantHomeAddress.objects.filter(home_address_id=test_home_address_id,
                                                    childcare_address=True).count() == 0)

    def test_logic_to_update_childcare_address_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id).delete()
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
            childcare_training_status='COMPLETED',
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
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_home_address_id = '11a3aef5-9e23-4216-b646-e6adccda4270'
        ApplicantHomeAddress.objects.create(
            home_address_id=(UUID(test_home_address_id)),
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            childcare_address=True,
            current_address=False,
        )
        assert (ApplicantPersonalDetails.objects.filter(application_id=test_application_id).count() > 0)
        assert (ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id,
                                                    childcare_address=True).count() > 0)

    def test_multiple_childcare_address_logic(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_personal_detail_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ApplicantPersonalDetails.objects.filter(application_id=test_application_id).delete()
        ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id).delete()
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
            childcare_training_status='COMPLETED',
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
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_home_address_id = '11a3aef5-9e23-4216-b646-e6adccda4270'
        ApplicantHomeAddress.objects.create(
            home_address_id=(UUID(test_home_address_id)),
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            childcare_address=True,
            current_address=False,
        )
        test_home_address_id2 = 'd51b854d-30b0-4889-88d4-804b2c6215e4'
        ApplicantHomeAddress.objects.create(
            home_address_id=(UUID(test_home_address_id2)),
            personal_detail_id=ApplicantPersonalDetails.objects.get(personal_detail_id=test_personal_detail_id),
            application_id=Application.objects.get(pk=test_application_id),
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            childcare_address=True,
            current_address=True,
        )
        assert (ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id,
                                                    childcare_address=True).count() > 1)
        assert (ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id, childcare_address=True,
                                                    current_address=True).count() > 0)
        assert (ApplicantHomeAddress.objects.filter(personal_detail_id=test_personal_detail_id, childcare_address=True,
                                                    current_address=False).count() > 0)

    def delete(self):
        ApplicantHomeAddress.objects.filter(name_id='11a3aef5-9e23-4216-b646-e6adccda4270').delete()
        ApplicantPersonalDetails.objects.filter(personal_detail_id='166f77f7-c2ee-4550-9461-45b9d2f28d34').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
