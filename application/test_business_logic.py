"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_business_logic.py --

@author: Informed Solutions
"""

import datetime

from datetime import date
from django.test import TestCase
from uuid import UUID

from application.models import (AdultInHome,
                                ApplicantHomeAddress,
                                ApplicantName,
                                ApplicantPersonalDetails,
                                Application,
                                ChildcareType,
                                ChildInHome,
                                CriminalRecordCheck,
                                EYFS,
                                FirstAidTraining,
                                HealthDeclarationBooklet,
                                Reference,
                                UserDetails)


class TestChildcareTypeLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        ChildcareType.objects.filter(application_id=test_application_id).delete()
        assert (ChildcareType.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        ApplicantPersonalDetails.objects.create(
            personal_detail_id=(UUID(test_personal_detail_id)),
            application_id=Application.objects.get(pk=test_application_id),
            birth_day='00',
            birth_month='00',
            birth_year='0000'
        )
        test_name_id = '6e09fe41-2b07-4177-a5e4-347b2515ea8e'
        ApplicantName.objects.create(
            name_id=(UUID(test_name_id)),
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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
            move_in_month=0,
            move_in_year=0
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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
            move_in_month=0,
            move_in_year=0
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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
            move_in_month=0,
            move_in_year=0
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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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
            move_in_month=0,
            move_in_year=0
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
            move_in_month=0,
            move_in_year=0
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


class TestFirstAidTrainingLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        FirstAidTraining.objects.filter(application_id=test_application_id).delete()
        assert (FirstAidTraining.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        FirstAidTraining.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_first_aid_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        FirstAidTraining.objects.create(
            first_aid_id=(UUID(test_first_aid_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            training_organisation='Red Cross',
            course_title='Infant First Aid',
            course_day='01',
            course_month='02',
            course_year='2003'
        )
        assert (FirstAidTraining.objects.filter(application_id=test_application_id).count() > 0)

    def test_logic_to_go_to_declaration(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        FirstAidTraining.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        test_first_aid_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_first_aid = FirstAidTraining.objects.create(
            first_aid_id=(UUID(test_first_aid_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            training_organisation='Red Cross',
            course_title='Infant First Aid',
            course_day=1,
            course_month=2,
            course_year=2017
        )
        test_date = date(2018, 1, 5)
        certificate_day = test_first_aid.course_day
        certificate_month = test_first_aid.course_month
        certificate_year = test_first_aid.course_year
        certificate_date = date(certificate_year, certificate_month, certificate_day)
        certificate_age = test_date.year - certificate_date.year - (
                (test_date.month, test_date.day) < (certificate_date.month, certificate_date.day))
        assert (certificate_age < 2.5)

    def test_logic_to_go_to_renew(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        FirstAidTraining.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        test_first_aid_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_first_aid = FirstAidTraining.objects.create(
            first_aid_id=(UUID(test_first_aid_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            training_organisation='Red Cross',
            course_title='Infant First Aid',
            course_day=1,
            course_month=2,
            course_year=2014
        )
        test_date = date(2018, 1, 5)
        certificate_day = test_first_aid.course_day
        certificate_month = test_first_aid.course_month
        certificate_year = test_first_aid.course_year
        certificate_date = date(certificate_year, certificate_month, certificate_day)
        certificate_age = test_date.year - certificate_date.year - (
                (test_date.month, test_date.day) < (certificate_date.month, certificate_date.day))
        assert (2.5 <= certificate_age <= 3)

    def test_logic_to_go_to_training(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        FirstAidTraining.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        test_first_aid_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        test_first_aid = FirstAidTraining.objects.create(
            first_aid_id=(UUID(test_first_aid_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            training_organisation='Red Cross',
            course_title='Infant First Aid',
            course_day=1,
            course_month=2,
            course_year=1995
        )
        test_date = date(2018, 1, 5)
        certificate_day = test_first_aid.course_day
        certificate_month = test_first_aid.course_month
        certificate_year = test_first_aid.course_year
        certificate_date = date(certificate_year, certificate_month, certificate_day)
        certificate_age = test_date.year - certificate_date.year - (
                (test_date.month, test_date.day) < (certificate_date.month, certificate_date.day))
        assert (certificate_age > 3)

    def delete(self):
        FirstAidTraining.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class TestEYFSLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        EYFS.objects.filter(application_id=test_application_id).delete()
        assert (EYFS.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        EYFS.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_eyfs_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        EYFS.objects.create(
            eyfs_id=(UUID(test_eyfs_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            eyfs_understand='True',
            eyfs_training_declare='True',
            share_info_declare='True'
        )
        assert (EYFS.objects.filter(application_id=test_application_id).count() > 0)

    def delete(self):
        EYFS.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


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
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
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


class TestHealthLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        HealthDeclarationBooklet.objects.filter(application_id=test_application_id).delete()
        assert (HealthDeclarationBooklet.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        HealthDeclarationBooklet.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_hdb_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        HealthDeclarationBooklet.objects.create(
            hdb_id=(UUID(test_hdb_id)),
            application_id=Application.objects.get(application_id=test_application_id),
            send_hdb_declare='True'
        )
        assert (HealthDeclarationBooklet.objects.filter(application_id=test_application_id).count() > 0)

    def delete(self):
        HealthDeclarationBooklet.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class TestReferencesLogic(TestCase):

    def test_logic_to_create_new_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        Reference.objects.filter(application_id=test_application_id, reference=1).delete()
        assert (Reference.objects.filter(application_id=test_application_id, reference=1).count() == 0)

    def test_logic_to_update_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        Reference.objects.filter(application_id=test_application_id).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application = Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_reference_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        Reference.objects.create(
            application_id=application,
            reference_id=(UUID(test_reference_id)),
            reference=1,
            first_name='',
            last_name='',
            relationship='',
            years_known=0,
            months_known=0,
            street_line1='',
            street_line2='',
            town='',
            county='',
            country='',
            postcode='',
            phone_number='',
            email=''
        )
        assert (Reference.objects.filter(application_id=test_application_id, reference=1).count() > 0)

    def delete(self):
        Reference.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', reference=1).delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class TestPeopleInYourHomeLogic(TestCase):

    def test_logic_to_create_new_adult_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        AdultInHome.objects.filter(application_id=test_application_id, adult=1).delete()
        assert (AdultInHome.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_adult_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        AdultInHome.objects.filter(application_id=test_application_id, adult=1).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application = Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_adult_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        AdultInHome.objects.create(
            adult_id=(UUID(test_adult_id)),
            application_id=application,
            adult=1,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship='',
            dbs_certificate_number=0,
            permission_declare=True
        )
        assert (AdultInHome.objects.filter(application_id=test_application_id, adult=1).count() > 0)

    def test_rearrange_adults(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        AdultInHome.objects.filter(application_id=test_application_id, adult=1).delete()
        AdultInHome.objects.filter(application_id=test_application_id, adult=2).delete()
        AdultInHome.objects.filter(application_id=test_application_id, adult=3).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application = Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_adult_1_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        AdultInHome.objects.create(
            adult_id=(UUID(test_adult_1_id)),
            application_id=application,
            adult=1,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship='',
            dbs_certificate_number=0,
            permission_declare=True
        )
        test_adult_2_id = '72fa718c-e31e-4fd6-b1c6-5bd25725a545'
        adult_delete = AdultInHome.objects.create(
            adult_id=(UUID(test_adult_2_id)),
            application_id=application,
            adult=2,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship='',
            dbs_certificate_number=0,
            permission_declare=True
        )
        test_adult_3_id = 'becf38ef-45df-4ea1-888d-0d75e3223972'
        AdultInHome.objects.create(
            adult_id=(UUID(test_adult_3_id)),
            application_id=application,
            adult=3,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship='',
            dbs_certificate_number=0,
            permission_declare=True
        )
        number_of_adults = AdultInHome.objects.filter(application_id=test_application_id).count()
        adult_delete.delete()
        for i in range(1, number_of_adults + 1):
            if AdultInHome.objects.filter(application_id=test_application_id, adult=i).count() == 0:
                next_adult = i + 1
                if AdultInHome.objects.filter(application_id=test_application_id, adult=next_adult).count() != 0:
                    next_adult_record = AdultInHome.objects.get(application_id=test_application_id, adult=next_adult)
                    next_adult_record.adult = i
                    next_adult_record.save()
        assert (AdultInHome.objects.filter(application_id=test_application_id, adult=3).count() == 0)
        assert (AdultInHome.objects.filter(application_id=test_application_id, adult=1).count() == 1)
        assert (AdultInHome.objects.filter(application_id=test_application_id, adult=2).count() == 1)

    def test_logic_to_create_new_child_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        ChildInHome.objects.filter(application_id=test_application_id, child=1).delete()
        assert (ChildInHome.objects.filter(application_id=test_application_id).count() == 0)

    def test_logic_to_update_child_record(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ChildInHome.objects.filter(application_id=test_application_id, child=1).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application = Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_child_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        ChildInHome.objects.create(
            child_id=(UUID(test_child_id)),
            application_id=application,
            child=1,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship=''
        )
        assert (ChildInHome.objects.filter(application_id=test_application_id, child=1).count() > 0)

    def test_rearrange_children(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        ChildInHome.objects.filter(application_id=test_application_id, child=1).delete()
        ChildInHome.objects.filter(application_id=test_application_id, child=2).delete()
        ChildInHome.objects.filter(application_id=test_application_id, child=3).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        user = UserDetails.objects.create(
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application = Application.objects.create(
            application_id=(UUID(test_application_id)),
            login_id=user,
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
            order_code=None
        )
        test_child_1_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        ChildInHome.objects.create(
            child_id=(UUID(test_child_1_id)),
            application_id=application,
            child=1,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship=''
        )
        test_child_2_id = '72fa718c-e31e-4fd6-b1c6-5bd25725a545'
        child_delete = ChildInHome.objects.create(
            child_id=(UUID(test_child_2_id)),
            application_id=application,
            child=2,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship=''
        )
        test_child_3_id = 'becf38ef-45df-4ea1-888d-0d75e3223972'
        ChildInHome.objects.create(
            child_id=(UUID(test_child_3_id)),
            application_id=application,
            child=3,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship=''
        )
        number_of_children = ChildInHome.objects.filter(application_id=test_application_id).count()
        child_delete.delete()
        for i in range(1, number_of_children + 1):
            if ChildInHome.objects.filter(application_id=test_application_id, child=i).count() == 0:
                next_child = i + 1
                if ChildInHome.objects.filter(application_id=test_application_id, child=next_child).count() != 0:
                    next_child_record = ChildInHome.objects.get(application_id=test_application_id, child=next_child)
                    next_child_record.child = i
                    next_child_record.save()
        assert (ChildInHome.objects.filter(application_id=test_application_id, child=3).count() == 0)
        assert (ChildInHome.objects.filter(application_id=test_application_id, child=1).count() == 1)
        assert (ChildInHome.objects.filter(application_id=test_application_id, child=2).count() == 1)

    def delete(self):
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=1).delete()
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=2).delete()
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=3).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=1).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=2).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=3).delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
