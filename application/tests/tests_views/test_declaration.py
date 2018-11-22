import random

from django.test import modify_settings

from application.views import declaration_intro, publishing_your_details
from .view_parent import *
import uuid


class DeclarationTest(ViewsTest):

    def test_url_resolves_to_page_check_answers(self):
        found = resolve(settings.URL_PREFIX + '/check-answers/')
        self.assertEqual(found.func, declaration_summary)

    def test_page_not_displayed_without_id_check_answers(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/check-answers?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page_declaration(self):
        found = resolve(settings.URL_PREFIX + '/declaration/')
        self.assertEqual(found.func, declaration_intro)

    def test_page_not_displayed_without_id_declaration(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/declaration?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page_your_declaration(self):
        found = resolve(settings.URL_PREFIX + '/your-declaration/')
        self.assertEqual(found.func, declaration_declaration)

    def test_page_not_displayed_without_id_your_declaration(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/your-declaration?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page_publish_details(self):
        found = resolve(settings.URL_PREFIX + '/publishing-your-details/')
        self.assertEqual(found.func, publishing_your_details)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_can_submit_consent_to_publish_details(self):
        """
        Assert that whatever is posted to the publish details page gets inverted in the database.
        """
        app_id = uuid.uuid4()
        models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='COMPLETED',
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
        c = Client()
        publish_details = bool(random.getrandbits(1))
        try:
            response = c.post(settings.URL_PREFIX + '/publishing-your-details/?id=' + str(app_id),
                              {'publish_details': publish_details,
                               'id': str(app_id)})
            application = models.Application.objects.get(application_id=app_id)
            self.assertEqual(application.publish_details, not publish_details)
            self.assertEqual(response.status_code, 302)

        except Exception as e:
            self.fail(e)

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
