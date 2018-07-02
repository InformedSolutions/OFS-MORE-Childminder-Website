import pytz

from datetime import datetime, timedelta
from django.test import TestCase
from uuid import UUID
from unittest import mock

from ...models import AdultInHome, Application, ChildInHome, UserDetails
from ...business_logic import health_check_email_resend_logic


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
        application = Application.objects.create(
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
            login_id=(UUID(test_login_id)),
            application_id=application,
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
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
        )
        assert (AdultInHome.objects.filter(application_id=test_application_id, adult=1).count() > 0)

    def test_rearrange_adults(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        AdultInHome.objects.filter(application_id=test_application_id, adult=1).delete()
        AdultInHome.objects.filter(application_id=test_application_id, adult=2).delete()
        AdultInHome.objects.filter(application_id=test_application_id, adult=3).delete()
        UserDetails.objects.filter(login_id=test_login_id).delete()
        application = Application.objects.create(
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
            login_id=(UUID(test_login_id)),
            application_id=application,
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
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
        application = Application.objects.create(
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
            login_id=(UUID(test_login_id)),
            application_id=application,
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
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
        application = Application.objects.create(
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
            login_id=(UUID(test_login_id)),
            application_id=application,
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
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

    def test_health_check_email_resend_logic_less_than_three_last_24_hours(self):
        """
        Test to check that if the health check email is sent less than three times in the last 24 hours,
        the resend limit is not reached
        """
        mock_adult_in_home_record = mock.Mock(spec=AdultInHome)
        mock_adult_in_home_record.email_resent_timestamp = datetime.now(pytz.utc)
        mock_adult_in_home_record.email_resent = 1
        resend_limit_reached = health_check_email_resend_logic(mock_adult_in_home_record)
        assert (resend_limit_reached is False)

    def test_health_check_email_resend_logic_more_than_three_last_24_hours(self):
        """
        Test to check that if the health check email is sent more than three times in the last 24 hours,
        the resend limit is reached
        """
        mock_adult_in_home_record = mock.Mock(spec=AdultInHome)
        mock_adult_in_home_record.email_resent_timestamp = datetime.now(pytz.utc)
        mock_adult_in_home_record.email_resent = 4
        resend_limit_reached = health_check_email_resend_logic(mock_adult_in_home_record)
        assert (resend_limit_reached is True)

    def test_health_check_email_resend_logic_over_24_hours(self):
        """
        Test to check that if the last health check email is sent over 24 hours ago, the resend limit is not reached
        """
        mock_adult_in_home_record = mock.Mock(spec=AdultInHome)
        mock_adult_in_home_record.email_resent_timestamp = datetime.now(pytz.utc) - timedelta(1)
        mock_adult_in_home_record.email_resent = 4
        resend_limit_reached = health_check_email_resend_logic(mock_adult_in_home_record)
        assert (resend_limit_reached is False)

    def delete(self):
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=1).delete()
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=2).delete()
        AdultInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=3).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=1).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=2).delete()
        ChildInHome.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c', adult=3).delete()
        Application.objects.filter(application_id='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
