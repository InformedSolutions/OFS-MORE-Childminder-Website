from django.test import TestCase, modify_settings
from application import models, views, forms
from django.urls import reverse, resolve
from django.utils import timezone


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class TestDBSCheckValidation(TestCase):

    def test_invalid_dbs_certificate_number(self):
        test_dbs_certificate_number = 12345612345678
        assert (len(str(test_dbs_certificate_number)) > 12)

    def test_invalid_dbs_certificate_number2(self):
        test_dbs_certificate_number = 123456
        assert (len(str(test_dbs_certificate_number)) < 12)

    def test_duplicate_dbs_applicant_adult(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)

        test_adult_1_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        application = models.Application.objects.create(
            application_id=app_id,
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
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )
        models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789101'
        )
        adult = models.AdultInHome.objects.create(
            adult_id=test_adult_1_id,
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
        response = self.client.post(reverse('PITH-DBS-Check-View') + self.url_suffix,
                                   data = {'capita': ['True'],
                                     'dbs_certificate_number166f77f7-c2ee-4550-9461-45b9d2f28d34': ['123456789101'],
                                    'dbs_certificate_number_no_update166f77f7-c2ee-4550-9461-45b9d2f28d34':['']})

        self.assertEqual(200, response.status_code)
        adult.delete()

    def test_duplicate_dbs_applicant_adult2(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)

        test_adult_1_id = '166f77f7-c2ee-4550-9461-45b9d2f28d34'
        application = models.Application.objects.create(
            application_id=app_id,
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
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )
        models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789101'
        )
        adult=models.AdultInHome.objects.create(
            adult_id=test_adult_1_id,
            application_id=application,
            adult=1,
            first_name='',
            middle_names='',
            last_name='',
            birth_day=0,
            birth_month=0,
            birth_year=0,
            relationship='',
        )
        response = self.client.post(reverse('PITH-DBS-Check-View') + self.url_suffix,
                                    data = {'capita': ['True'],
                                     'dbs_certificate_number166f77f7-c2ee-4550-9461-45b9d2f28d34': [198765432101],
                                    'dbs_certificate_number_no_update166f77f7-c2ee-4550-9461-45b9d2f28d34': ['']})


        self.assertEqual(302, response.status_code)
        self.assertEqual(resolve(response.url).func.__name__, views.PITH_views.PITHChildrenCheckView.as_view().__name__)
        adult.delete()





