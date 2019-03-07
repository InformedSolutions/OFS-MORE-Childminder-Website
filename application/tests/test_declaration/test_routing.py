from django.test import TestCase, tag
from django.urls import reverse

from application import models, views
from application.tests import utils


@tag('http')
class DeclarationSummaryPageFunctionalTests(utils.NoMiddlewareTestCase):

    def setUp(self):
        self.application = models.Application.objects.create(
        )
        self.user_details = models.UserDetails.objects.create(
            application_id=self.application,
        )
        self.applicant_personal_details = models.ApplicantPersonalDetails.objects.create(
            application_id=self.application
        )
        self.applicant_name = models.ApplicantName.objects.create(
            application_id=self.application,
            personal_detail_id=self.applicant_personal_details,
            current_name=True,
        )
        self.applicant_home_address = models.ApplicantHomeAddress.objects.create(
            application_id=self.application,
            personal_detail_id=self.applicant_personal_details,
            move_in_month=1, move_in_year=2001,
            current_address=True,
            childcare_address=True,
        )
        self.childcare_type = models.ChildcareType.objects.create(
            application_id=self.application,
            zero_to_five=True, five_to_eight=True, eight_plus=True,
        )
        self.adult_in_home = models.AdultInHome.objects.create(
            application_id=self.application,
            birth_day=1, birth_month=2, birth_year=1983,
            adult=1,
        )
        self.first_aid_training = models.FirstAidTraining.objects.create(
            application_id=self.application,
            course_day=1, course_month=2, course_year=2015,
        )
        self.crim_rec_check = models.CriminalRecordCheck.objects.create(
            application_id=self.application,
            certificate_information='',
        )
        self.childcare_training = models.ChildcareTraining.objects.create(
            application_id=self.application,
        )
        self.reference1 = models.Reference.objects.create(
            application_id=self.application,
            reference=1,
            years_known=1, months_known=11,
        )
        self.reference2 = models.Reference.objects.create(
            application_id=self.application,
            reference=2,
            years_known=2, months_known=10,
        )

    # ------------

    def test_can_render_page(self):

        response = self.client.get(reverse('Declaration-Summary-View'), data={'id': self.application.pk})

        self.assertEqual(200, response.status_code)
        utils.assertView(response, views.declaration_summary)

    def test_doesnt_display_adults_in_home_if_not_working_in_their_own_home(self):

        self.application.working_in_other_childminder_home = True
        self.application.save()

        response = self.client.get(reverse('Declaration-Summary-View'), data={'id': self.application.pk})

        utils.assertNotXPath(response, '//*[normalize-space(text())="Adults in the home"]')

    def test_displays_adults_in_home_info_that_is_always_shown(self):

        self.application.working_in_other_childminder_home = False
        self.application.adults_in_home = True
        self.application.save()

        self.adult_in_home.first_name = 'Joe'
        self.adult_in_home.middle_names = 'Josef'
        self.adult_in_home.last_name = 'Johannsen'
        self.adult_in_home.birth_day = 20
        self.adult_in_home.birth_month = 12
        self.adult_in_home.birth_year = 1975
        self.adult_in_home.relationship = 'Uncle'
        self.adult_in_home.email = 'foo@example.com'
        self.adult_in_home.lived_abroad = False
        self.adult_in_home.dbs_certificate_number = '123456789012'
        self.adult_in_home.save()

        response = self.client.get(reverse('Declaration-Summary-View'), data={'id': self.application.pk})

        utils.assertSummaryField(response, 'Name', 'Joe Josef Johannsen', heading='Joe Josef Johannsen')
        utils.assertSummaryField(response, 'Date of birth', '20 Dec 1975', heading='Joe Josef Johannsen')
        utils.assertSummaryField(response, 'Relationship', 'Uncle', heading='Joe Josef Johannsen')
        utils.assertSummaryField(response, 'Email', 'foo@example.com', heading='Joe Josef Johannsen')
        utils.assertSummaryField(response, 'Have they lived outside of the UK in the last 5 years?', 'No',
                                 heading='Joe Josef Johannsen')
        utils.assertSummaryField(response, 'DBS certificate number', '123456789012', heading='Joe Josef Johannsen')

    def test_doesnt_display_private_information_for_adults_in_the_home(self):

        self.application.working_in_other_childminder_home = False
        self.application.adults_in_home = True
        self.application.save()

        self.adult_in_home.first_name = 'Joe'
        self.adult_in_home.middle_names = 'Josef'
        self.adult_in_home.last_name = 'Johannsen'
        self.adult_in_home.save()

        response = self.client.get(reverse('Declaration-Summary-View'), data={'id': self.application.pk})

        utils.assertNotSummaryField(response, 'Known to council social services in regards to their own children?',
                                    heading='Joe Josef Johannsen')

