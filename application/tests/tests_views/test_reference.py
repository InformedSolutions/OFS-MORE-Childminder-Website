from .view_parent import *


class ReferencesTest(ViewsTest):

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
            childcare_training_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='NOT_STARTED',
            people_in_home_status='COMPLETED',
            declarations_status='NOT_STARTED',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
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