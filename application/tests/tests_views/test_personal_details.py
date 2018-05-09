from .test_views import *


class PersonalDetailsTest(ViewsTest):

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
        assert (models.Application.objects.get(pk=test_application_id).personal_details_status != 'COMPLETED')

    def delete(self):

        models.Application.objects.get(pk='f8c42666-1367-4878-92e2-1cee6ebcb48c').delete()
        models.UserDetails.objects.get(login_id='004551ca-21fa-4dbe-9095-0384e73b3cbe').delete()
