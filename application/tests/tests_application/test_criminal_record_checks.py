import datetime
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase, Client, modify_settings, tag
from django.urls import reverse

from ...business_logic import dbs_date_of_birth_no_match, date_issued_within_three_months
from ...models import Application, CriminalRecordCheck, ApplicantPersonalDetails


@modify_settings(MIDDLEWARE={
    'remove': [
        'application.middleware.CustomAuthenticationHandler'
    ]
})
class NoMiddlewareTestCase(TestCase):
    pass


class DBSTemplateViewTestCase(NoMiddlewareTestCase):

    def setUp(self):
        self.client = Client()
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        # Set the following variables when inheriting
        self.view_url_name = None
        self.correct_url = None

        Application.objects.create(application_id=self.application_id)

    @tag('http')
    def test_view_rendered_on_get(self):
        if self.view_url_name is not None:
            response = self.client.get(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_redirect_on_post(self):
        if self.view_url_name is not None:
            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 302)
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_redirect_to_correct_url(self):
        if self.view_url_name is not None and self.correct_url is not None:
            correct_url = reverse(self.correct_url) + '?id=' + self.application_id
            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
            self.assertTrue(response.url == correct_url)
        else:
            raise self.skipTest('view_url_name or correct_url not set')


class DBSGoodConductViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Good-Conduct-View'
        self.correct_url = 'DBS-Email-Certificates-View'


class DBSSendCertificateViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Email-Certificates-View'
        self.correct_url = 'DBS-Military-View'


class DBSMinistryOfDefenceViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Ministry-Of-Defence-View'
        self.correct_url = 'DBS-Guidance-Second-View'


class DBSGuidanceViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Guidance-View'
        self.correct_url = 'DBS-Lived-Abroad-View'


class DBSGuidanceSecondViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Guidance-Second-View'
        self.correct_url = 'DBS-Check-Capita-View'

    @tag('http')
    def test_post_request_to_guidance_page_redirects_to_criminal_details_page(self):
        # Build env
        self.view_url_name = 'DBS-Guidance-Second-View'
        criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
        application = Application.objects.get(application_id=self.application_id)
        crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                        criminal_record_id=criminal_record_check_id)
        response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)
        print('Returned a {0} response'.format(response.status_code))
        self.assertEqual(response.status_code, 302)
        correct_url = reverse(self.correct_url) + '?id=' + self.application_id
        print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
        self.assertEqual(response.url, correct_url)

        # Tear down env
        crc_record.delete()


class DBSGetViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Get-View'
        self.correct_url = 'Task-List-View'


class DBSPostViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Post-View'
        self.correct_url = 'DBS-Summary-View'


class DBSUpdateCheckView(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Update-Check-View'
        self.correct_url = 'DBS-Post-View'


class DBSRadioViewTests(NoMiddlewareTestCase):
    def setUp(self):
        self.dbs_views_path = 'application.views.dbs'
        self.client = Client()
        self.application_id = '4437429e-c9f5-492f-9ee7-ea8bfddc0567'

        Application.objects.create(application_id=self.application_id)

        self.view = None
        self.form = None
        self.view_url_name = None
        self.correct_url = None

    @tag('http')
    def test_view_rendered_on_get(self):
        if self.view_url_name is not None:
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)

            response = self.client.get(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name not set')

    @tag('http')
    def test_form_invalid_callable(self):
        if all(var is not None for var in [self.view, self.view_url_name]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            view_class_name = self.view.__name__
            mock_response = HttpResponse()
            mock_response.status_code = 200

            with patch('{0}.{1}.form_invalid'.format(self.dbs_views_path, view_class_name)) as mock_form_invalid:
                mock_form_invalid.return_value = mock_response

                response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)

                self.assertTrue(mock_form_invalid.called)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view or view_url_name not set')

    @tag('http')
    def test_no_redirect_on_form_invalid(self):
        if self.view_url_name is not None:
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name not set')

    @tag('http')
    def test_radio_error_message(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id)
            self.assertRaises(ValidationError)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_form_valid_callable(self):
        if all(var is not None for var in [self.view, self.view_url_name]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            view_class_name = self.view.__name__
            mock_response = HttpResponse()
            mock_response.status_code = 200
            form_data = {self.form.choice_field_name: True}

            with patch('{0}.{1}.form_valid'.format(self.dbs_views_path, view_class_name)) as mock_form_valid:
                mock_form_valid.return_value = mock_response

                response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

                self.assertTrue(mock_form_valid.called)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view or view_url_name not set')

    @tag('http')
    def test_redirect_on_form_valid(self):
        if all(var is not None for var in [self.view_url_name]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            form_data = {self.form.choice_field_name: True}

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

            self.assertTrue(response.status_code == 302)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name not set')

    @tag('http')
    def test_radio_yes_redirect(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            form_data = {self.form.choice_field_name: True}

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 302)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_radio_yes_redirect_to_correct_url(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            form_data = {self.form.choice_field_name: True}

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

            yes_redirect, no_redirect = self.correct_url

            correct_url = reverse(yes_redirect) + '?id=' + self.application_id
            print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
            self.assertTrue(response.url == correct_url)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view or view_url_name or correct_url not set')

    @tag('http')
    def test_radio_no_redirect(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            form_data = {self.form.choice_field_name: False}

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

            yes_redirect, no_redirect = self.correct_url

            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 302)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_radio_no_redirect_to_correct_url(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            form_data = {self.form.choice_field_name: False}

            response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id, form_data)

            yes_redirect, no_redirect = self.correct_url

            correct_url = reverse(no_redirect) + '?id=' + self.application_id
            print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
            self.assertTrue(response.url == correct_url)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')


class DBSLivedAbroadViewTests(DBSRadioViewTests):
    def setUp(self):
        super().setUp()

        from application.views import DBSLivedAbroadView as view
        from application.forms import DBSLivedAbroadForm as form

        self.view = view
        self.form = form
        self.view_url_name = 'DBS-Lived-Abroad-View'
        self.correct_url = ('DBS-Good-Conduct-View', 'DBS-Military-View')

    def test_view_rendered_on_get(self):
        if self.view_url_name is not None:
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)
            # Set to stop error being raised
            previous_criminal_record_check_status = application.criminal_record_check_status
            application.criminal_record_check_status = 'IN_PROGRESS'
            application.save()

            response = self.client.get(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

            # Tear down env
            application.criminal_record_check_status = previous_criminal_record_check_status
            application.save()
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name not set')


class DBSMilitaryViewTests(DBSRadioViewTests):
    def setUp(self):
        super().setUp()

        from application.views import DBSMilitaryView as view
        from application.forms import DBSMilitaryForm as form

        self.view = view
        self.form = form
        self.view_url_name = 'DBS-Military-View'
        self.correct_url = ('DBS-Ministry-Of-Defence-View', 'DBS-Guidance-Second-View')


class DBSTypeViewTests(DBSRadioViewTests):
    def setUp(self):
        super().setUp()

        from application.views import DBSTypeView as view
        from application.forms import DBSTypeForm as form

        self.view = view
        self.form = form
        self.view_url_name = 'DBS-Type-View'
        self.correct_url = ('DBS-Check-Capita-View', 'DBS-Update-View')


class DBSUpdateViewTests(DBSRadioViewTests):
    def setUp(self):
        super().setUp()

        from application.views import DBSUpdateView as view
        from application.forms import DBSUpdateForm as form

        self.view = view
        self.form = form
        self.view_url_name = 'DBS-Update-View'
        self.correct_url = ('DBS-Check-No-Capita-View', 'DBS-Get-View')


class DBSCheckCapitaView(DBSRadioViewTests):
    def setUp(self):
        super().setUp()

        from application.views import DBSCheckCapitaView as view
        from application.forms import DBSCheckCapitaForm as form

        self.view = view
        self.form = form
        self.view_url_name = 'DBS-Check-Capita-View'
        self.correct_url = ('DBS-Post-View', 'DBS-Summary-View')

    @tag('http')
    def test_form_valid_callable(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_radio_no_redirect(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_radio_no_redirect_to_correct_url(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_radio_yes_redirect(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_radio_yes_redirect_to_correct_url(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_redirect_on_form_valid(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_form_cautions_convictions_validation(self):
        raise self.skipTest('Not Yet Implemented')

    def test_no_capita_redirect(self):
        # Build env
        self.correct_url = 'DBS-Check-Type'
        criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
        application = Application.objects.get(application_id=self.application_id)
        crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                        criminal_record_id=criminal_record_check_id)
        pd = ApplicantPersonalDetails.objects.create(application_id=application, birth_day=1, birth_month=2,
                                                     birth_year=1994)

        response = self.client.post(reverse(self.view_url_name) + '?id=' + self.application_id,
                                    data={'dbs_certificate_number': '111111111111'})
        print('Returned a {0} response'.format(response.status_code))
        self.assertEqual(response.status_code, 302)
        correct_url = reverse(self.correct_url) + '?id=' + self.application_id
        print('Returned url is {0} but should have been {1} response'.format(response.url, correct_url))
        self.assertEqual(response.url, correct_url)

        # Tear down env
        crc_record.delete()
        pd.delete()

    def test_capita_correct_date_of_birth(self):
        application = Application.objects.get(application_id=self.application_id)
        pd = ApplicantPersonalDetails.objects.create(application_id=application, birth_day=1, birth_month=2,
                                                     birth_year=1994)
        dbs_response = {'certificate_number': 123456789101, 'date_of_issue': '2019-01-01',
                        'date_of_birth': '1994-02-01', 'certificate_information': 'info'}
        result = dbs_date_of_birth_no_match(application, dbs_response)
        self.assertEqual(result, False)

        pd.delete()

    def test_capita_incorrect_date_of_birth(self):
        application = Application.objects.get(application_id=self.application_id)
        pd = ApplicantPersonalDetails.objects.create(application_id=application, birth_day=1, birth_month=2,
                                                     birth_year=1994)
        dbs_response = {'certificate_number': 123456789101, 'date_of_issue': '2019-01-01',
                        'date_of_birth': '1930-07-01', 'certificate_information': 'info'}
        result = dbs_date_of_birth_no_match(application, dbs_response)
        self.assertEqual(result, True)

    def test_date_not_issued_within_three_months(self):
        date_issued = datetime.datetime(2000, 1, 1)
        result = date_issued_within_three_months(date_issued)
        self.assertEqual(result, False)


class DBSCheckNoCapitaView(DBSTemplateViewTestCase):
    def setUp(self):

        super().setUp()
        self.view_url_name = 'DBS-Check-No-Capita-View'
        self.correct_url = 'DBS-Post-View'

    @tag('http')
    def test_view_rendered_on_get(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)

            response = self.client.get(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')

    @tag('http')
    def test_redirect_on_post(self):
        raise self.skipTest('Not Yet Implemented')

    @tag('http')
    def test_redirect_to_correct_url(self):
        raise self.skipTest('Not Yet Implemented')


class DBSSummaryViewTests(DBSTemplateViewTestCase):
    def setUp(self):
        super().setUp()
        self.view_url_name = 'DBS-Summary-View'
        self.correct_url = 'Task-List-View'

    @tag('http')
    def test_view_rendered_on_get(self):
        if all(var is not None for var in [self.view_url_name, self.correct_url]):
            # Build env
            criminal_record_check_id = '35afa482-c607-4ad9-bf44-a8d69bb8c428'
            application = Application.objects.get(application_id=self.application_id)
            crc_record = CriminalRecordCheck.objects.create(application_id=application,
                                                            criminal_record_id=criminal_record_check_id)

            response = self.client.get(reverse(self.view_url_name) + '?id=' + self.application_id)
            print('Returned a {0} response'.format(response.status_code))
            self.assertTrue(response.status_code == 200)

            # Tear down env
            crc_record.delete()
        else:
            raise self.skipTest('view_url_name or correct_url not set')
