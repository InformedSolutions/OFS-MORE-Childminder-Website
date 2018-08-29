import datetime

from datetime import date
from django.test import TestCase
from uuid import UUID

from ...models import Application, FirstAidTraining, UserDetails


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
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
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
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
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
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='NOT_STARTED',
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

