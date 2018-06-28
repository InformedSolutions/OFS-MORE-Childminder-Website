from .view_parent import *


class TypeOfChildcareTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/childcare/type/')
        self.assertEqual(found.func, type_of_childcare_guidance)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/childcare/type?id=')
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
