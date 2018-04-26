"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_views.py --

@author: Informed Solutions
"""

import datetime
from uuid import UUID

from django.conf import settings
from django.test import Client
from django.test import TestCase
from django.urls import resolve, reverse

from application import models
from application.views import (application_saved,
                               card_payment_details,
                               contact_phone,
                               contact_summary,
                               dbs_check_dbs_details,
                               dbs_check_guidance,
                               dbs_check_summary,
                               dbs_check_upload_dbs,
                               declaration_declaration,
                               declaration_summary,
                               documents_needed,
                               first_aid_training_declaration,
                               first_aid_training_details,
                               first_aid_training_guidance,
                               first_aid_training_renew,
                               first_aid_training_summary,
                               first_aid_training_training,
                               health_intro,
                               health_booklet,
                               health_check_answers,
                               home_ready,
                               other_people_guidance,
                               other_people_adult_question,
                               other_people_adult_details,
                               other_people_adult_dbs,
                               other_people_adult_permission,
                               other_people_children_question,
                               other_people_children_details,
                               other_people_approaching_16,
                               other_people_summary,
                               payment,
                               payment_confirmation,
                               paypal_payment_completion,
                               personal_details_childcare_address,
                               personal_details_childcare_address_manual,
                               personal_details_childcare_address_select,
                               personal_details_dob,
                               personal_details_guidance,
                               personal_details_home_address,
                               personal_details_home_address_manual,
                               personal_details_home_address_select,
                               personal_details_location_of_care,
                               personal_details_name,
                               personal_details_summary,
                               prepare_for_interview,
                               references_intro,
                               references_first_reference,
                               references_first_reference_address,
                               references_first_reference_address_select,
                               references_first_reference_address_manual,
                               references_first_reference_contact_details,
                               references_second_reference,
                               references_second_reference_address,
                               references_second_reference_address_select,
                               references_second_reference_address_manual,
                               references_second_reference_contact_details,
                               references_summary,
                               start_page,
                               task_list,
                               type_of_childcare_age_groups,
                               type_of_childcare_guidance,
                               type_of_childcare_register, )
from application.views.login import new_email, account_selection, existing_email
from ..models import Application, UserDetails


class StartPageTest(TestCase):

    def test_root_url_resolves_to_start_page_view(self):
        found = resolve(settings.URL_PREFIX + '/')
        self.assertEqual(found.func, start_page)


class TaskListTest(TestCase):

    def test_url_resolves_to_task_list(self):
        found = resolve(settings.URL_PREFIX + '/task-list/')
        self.assertEqual(found.func, task_list)

    def test_task_list_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/task-list/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)


class TypeOfChildcareTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/childcare/guidance/')
        self.assertEqual(found.func, type_of_childcare_guidance)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/childcare/guidance?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/childcare/age-groups/')
        self.assertEqual(found.func, type_of_childcare_age_groups)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/childcare/age-groups?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/childcare/register/')
        self.assertEqual(found.func, type_of_childcare_register)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/childcare/register?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        test_app = Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='NOT_STARTED',
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
        assert (models.Application.objects.get(pk=test_application_id).childcare_type_status != 'COMPLETED')

    def delete(self):
        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class LoginAndContactDetailsTest(TestCase):

    def test_url_resolves_to_email_page(self):
        found = resolve(settings.URL_PREFIX + '/new-application/')
        self.assertEqual(found.func, new_email)

    def test_email_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/account/email/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_phone_page(self):
        found = resolve(settings.URL_PREFIX + '/account/phone/')
        self.assertEqual(found.func, contact_phone)

    def test_phone_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/account/phone/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_summary_page(self):
        found = resolve(settings.URL_PREFIX + '/account/summary/')
        self.assertEqual(found.func, contact_summary)

    def test_summary_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/account/summary/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='COMPLETED',
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
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )

        assert (models.Application.objects.get(pk=test_application_id).login_details_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class PersonalDetailsTest(TestCase):

    def test_guidance_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/')
        self.assertEqual(found.func, personal_details_guidance)

    def test_guidance_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_name_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/your-name/')
        self.assertEqual(found.func, personal_details_name)

    def test_name_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/your-name/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_dob_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/your-date-of-birth/')
        self.assertEqual(found.func, personal_details_dob)

    def test_dob_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/your-date-of-birth/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_home_address_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/your-home-address/')
        self.assertEqual(found.func, personal_details_home_address)

    def test_home_address_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/your-home-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_home_address_manual_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/enter-home-address/')
        self.assertEqual(found.func, personal_details_home_address_manual)

    def test_home_address_manual_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/enter-home-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_home_address_select_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/select-home-address/')
        self.assertEqual(found.func, personal_details_home_address_select)

    def test_home_address_select_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/select-home-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_location_of_care_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/home-address-details/')
        self.assertEqual(found.func, personal_details_location_of_care)

    def test_location_of_care_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/home-address-details/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_childcare_address_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/childcare-address/')
        self.assertEqual(found.func, personal_details_childcare_address)

    def test_childcare_address_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/childcare-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_childcare_address_manual_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/enter-childcare-address/')
        self.assertEqual(found.func, personal_details_childcare_address_manual)

    def test_childcare_address_manual_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/enter-childcare-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_childcare_address_select_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/select-childcare-address/')
        self.assertEqual(found.func, personal_details_childcare_address_select)

    def test_childcare_address_select_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/select-childcare-address/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_summary_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/personal-details/check-answers/')
        self.assertEqual(found.func, personal_details_summary)

    def test_summary_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/personal-details/check-answers/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
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
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id = application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        assert (models.Application.objects.get(pk=test_application_id).personal_details_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class FirstAidTrainingTest(TestCase):

    def test_guidance_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/')
        self.assertEqual(found.func, first_aid_training_guidance)

    def test_guidance_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)  #

    def test_details_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/details/')
        self.assertEqual(found.func, first_aid_training_details)

    def test_details_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid/details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_declaration_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/certificate/')
        self.assertEqual(found.func, first_aid_training_declaration)

    def test_declaration_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid/certificate?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_renew_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/renew/')
        self.assertEqual(found.func, first_aid_training_renew)

    def test_renew_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid/renew?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_training_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/update/')
        self.assertEqual(found.func, first_aid_training_training)

    def test_training_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid/update?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_summary_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/first-aid/check-answers/')
        self.assertEqual(found.func, first_aid_training_summary)

    def test_summary_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/first-aid/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
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
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        assert (models.Application.objects.get(pk=test_application_id).first_aid_training_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class HealthTest(TestCase):

    def test_guidance_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/health/')
        self.assertEqual(found.func, health_intro)

    def test_guidance_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/health?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)  #

    def test_booklet_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/health/booklet/')
        self.assertEqual(found.func, health_booklet)

    def test_health_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/health/booklet?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_summary_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/health/check-answers/')
        self.assertEqual(found.func, health_check_answers)

    def test_summary_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/health/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='NOT_STARTED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
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
        assert (models.Application.objects.get(pk=test_application_id).health_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class EYFSTest(TestCase):

    # def test_url_resolves_to_page(self):
    #    found = resolve(settings.URL_PREFIX + '/eyfs/guidance/')
    #    self.assertEqual(found.func, eyfs_guidance)

    # def test_page_not_displayed_without_id(self):
    #    c = Client()
    #    try:
    #        c.get(settings.URL_PREFIX + '/eyfs/guidance?id=')
    #        self.assertEqual(1, 0)
    #    except:
    #        self.assertEqual(0, 0)

    # def test_url_resolves_to_page(self):
    #    found = resolve(settings.URL_PREFIX + '/eyfs/knowledge/')
    #    self.assertEqual(found.func, eyfs_knowledge)

    # def test_page_not_displayed_without_id(self):
    #    c = Client()
    #    try:
    #        c.get(settings.URL_PREFIX + '/eyfs/knowledge?id=')
    #        self.assertEqual(1, 0)
    #    except:
    #        self.assertEqual(0, 0)

    # def test_url_resolves_to_page(self):
    #    found = resolve(settings.URL_PREFIX + '/eyfs/training/')
    #    self.assertEqual(found.func, eyfs_training)

    # def test_page_not_displayed_without_id(self):
    #    c = Client()
    #    try:
    #        c.get(settings.URL_PREFIX + '/eyfs/training?id=')
    #        self.assertEqual(1, 0)
    #    except:
    #        self.assertEqual(0, 0)

    # def test_url_resolves_to_page(self):
    #    found = resolve(settings.URL_PREFIX + '/eyfs/questions/')
    #    self.assertEqual(found.func, eyfs_questions)

    # def test_page_not_displayed_without_id(self):
    #    c = Client()
    #    try:
    #        c.get(settings.URL_PREFIX + '/eyfs/questions?id=')
    #        self.assertEqual(1, 0)
    #    except:
    #        self.assertEqual(0, 0)

    # def test_url_resolves_to_page(self):
    #    found = resolve(settings.URL_PREFIX + '/eyfs/summary/')
    #    self.assertEqual(found.func, eyfs_summary)

    # def test_page_not_displayed_without_id(self):
    #    c = Client()
    #    try:
    #        c.get(settings.URL_PREFIX + '/eyfs/summary?id=')
    #        self.assertEqual(1, 0)
    #    except:
    #        self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='NOT_STARTED',
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
        user = models.UserDetails.objects.create(
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
        assert (models.Application.objects.get(pk=test_application_id).eyfs_training_status != 'COMPLETED')

    def delete(self):
        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class DBSCheckTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/criminal-record/')
        self.assertEqual(found.func, dbs_check_guidance)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/criminal-record/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/criminal-record/your-details/')
        self.assertEqual(found.func, dbs_check_dbs_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/criminal-record/your-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):

        found = resolve(settings.URL_PREFIX + '/criminal-record/post-certificate/')
        self.assertEqual(found.func, dbs_check_upload_dbs)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/criminal-record/post-certificate?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/criminal-record/check-answers/')
        self.assertEqual(found.func, dbs_check_summary)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/criminal-record/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),

            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        assert (models.Application.objects.get(pk=test_application_id).criminal_record_check_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class ReferencesTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/')
        self.assertEqual(found.func, references_intro)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/first-reference/')
        self.assertEqual(found.func, references_first_reference)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/first-reference?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/first-reference-address/')
        self.assertEqual(found.func, references_first_reference_address)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/first-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/select-first-reference-address/')
        self.assertEqual(found.func, references_first_reference_address_select)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/select-first-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/enter-first-reference-address/')
        self.assertEqual(found.func, references_first_reference_address_manual)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/enter-first-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/first-reference-contact-details/')
        self.assertEqual(found.func, references_first_reference_contact_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/first-reference-contact-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/second-reference/')
        self.assertEqual(found.func, references_second_reference)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/second-reference?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/second-reference-address/')
        self.assertEqual(found.func, references_second_reference_address)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/second-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/select-second-reference-address/')
        self.assertEqual(found.func, references_second_reference_address_select)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/select-second-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/enter-second-reference-address/')
        self.assertEqual(found.func, references_second_reference_address_manual)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/enter-second-reference-address?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/second-reference-contact-details/')
        self.assertEqual(found.func, references_second_reference_contact_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/second-reference-contact-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/references/check-answers/')
        self.assertEqual(found.func, references_summary)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/references/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='NOT_STARTED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        assert (models.Application.objects.get(pk=test_application_id).references_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class OtherPeopleTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/guidance/')
        self.assertEqual(found.func, other_people_guidance)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/guidance?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/adult-question/')
        self.assertEqual(found.func, other_people_adult_question)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/adult-question?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/adult-details/')
        self.assertEqual(found.func, other_people_adult_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/adult-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/adult-dbs/')
        self.assertEqual(found.func, other_people_adult_dbs)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/adult-dbs?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/adult-permission/')
        self.assertEqual(found.func, other_people_adult_permission)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/adult-permission?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/children-question/')
        self.assertEqual(found.func, other_people_children_question)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/children-question?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/children-details/')
        self.assertEqual(found.func, other_people_children_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/children-details?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/approaching-16/')
        self.assertEqual(found.func, other_people_approaching_16)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/approaching-16?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/other-people/summary/')
        self.assertEqual(found.func, other_people_summary)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/other-people/summary?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        assert (models.Application.objects.get(pk=test_application_id).people_in_home_status != 'COMPLETED')

    def delete(self):
        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class DeclarationTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/check-answers/')
        self.assertEqual(found.func, declaration_summary)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/declaration/')
        self.assertEqual(found.func, declaration_declaration)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/declaration?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/your-declaration/')
        self.assertEqual(found.func, declaration_declaration)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/your-declaration?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_status_does_not_change_to_in_progress_when_returning_to_task_list(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='COMPLETED',
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
        user = models.UserDetails.objects.create(
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
        assert (models.Application.objects.get(pk=test_application_id).declarations_status != 'COMPLETED')

    def delete(self):
        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()


class AccountSelectionTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/sign-in/new-application/')
        self.assertEqual(found.func, account_selection)


class PaymentTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/')
        self.assertEqual(found.func, payment)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/details/')
        self.assertEqual(found.func, card_payment_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/details/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/paypal-payment-completion/')
        self.assertEqual(found.func, paypal_payment_completion)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/paypal-payment-completion/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/confirmation/')
        self.assertEqual(found.func, payment_confirmation)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/confirmation/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Documents'))
        self.assertEqual(found.func, documents_needed)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Documents') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Home'))
        self.assertEqual(found.func, home_ready)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Home') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Interview'))
        self.assertEqual(found.func, prepare_for_interview)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Interview') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)


class ApplicationSavedTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/application-saved/')
        self.assertEqual(found.func, application_saved)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/application-saved/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)


class ExistingApplicationTest(TestCase):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/sign-in/')
        self.assertEqual(found.func, existing_email)


class ValidateMagicLinkEmailTest(TestCase):

    def test_page_not_displayed_without_magic_link_code(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/validate/')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)


# class ValidateMagicLinkSMSTest(TestCase):
#
#     def test_url_resolves_to_page(self):
#         found = resolve(settings.URL_PREFIX + '/verify-phone/')
#         self.assertEqual(found.func, sms_verification)


class ValidateMagicLinkSecurityQuestionTest(TestCase):

    def test_page_not_displayed_without_magic_link_code(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/security-question/')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)


class TaskStatusTest(TestCase):

    def test_status_update_with_tasks_not_started(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'
        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id = application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )

        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': False,
            'confirm_details': False
        })
        temp_context = application_status_context
        del temp_context['declaration_status']
        assert (('NOT_STARTED' in temp_context.values()) == True)

    def test_status_update_with_tasks_in_progress(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='IN_PROGRESS',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': False,
            'confirm_details': False
        })
        temp_context = application_status_context
        del temp_context['declaration_status']
        assert (('IN_PROGRESS' in temp_context.values()) == True)

    def test_status_update_with_tasks_completed_except_declarations(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
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
        user = models.UserDetails.objects.create(
            application_id = application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': False,
            'confirm_details': False
        })
        temp_context = application_status_context
        del temp_context['declaration_status']
        assert (('IN_PROGRESS' in temp_context.values()) == False)
        assert (('NOT_STARTED' in temp_context.values()) == False)

    def test_status_update_with_tasks_completed_with_declarations_to_do(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
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
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': True,
            'confirm_details': False
        })
        assert (application_status_context['declaration_status'] == 'NOT_STARTED')

    def test_status_update_with_tasks_completed_with_declarations_in_progress(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='IN_PROGRESS',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': True,
            'confirm_details': False
        })
        assert (application_status_context['declaration_status'] == 'IN_PROGRESS')

    def test_status_update_with_tasks_completed_with_declarations_complete(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'
        test_login_id = '004551ca-21fa-4dbe-9095-0384e73b3cbe'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='COMPLETED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            order_code=None
        )
        user = models.UserDetails.objects.create(
            application_id=application,
            login_id=(UUID(test_login_id)),
            email='',
            mobile_number='',
            add_phone_number='',
            email_expiry_date=None,
            sms_expiry_date=None,
            magic_link_email='',
            magic_link_sms=''
        )
        application_status_context = dict({
            'application_id': test_application_id,
            'login_details_status': application.login_details_status,
            'personal_details_status': application.personal_details_status,
            'childcare_type_status': application.childcare_type_status,
            'first_aid_training_status': application.first_aid_training_status,
            'eyfs_training_status': application.eyfs_training_status,
            'criminal_record_check_status': application.criminal_record_check_status,
            'health_status': application.health_status,
            'reference_status': application.references_status,
            'people_in_home_status': application.people_in_home_status,
            'declaration_status': application.declarations_status,
            'all_complete': True,
            'confirm_details': True
        })
        assert (application_status_context['declaration_status'] == 'COMPLETED')

    def delete(self):
        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
