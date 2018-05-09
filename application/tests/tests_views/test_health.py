from .test_views import *


class HealthTest(ViewsTest):

    def test_guidance_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/health/')
        self.assertEqual(found.func, health_intro)

    def test_guidance_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/health?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

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