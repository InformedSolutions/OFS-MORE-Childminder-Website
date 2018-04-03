"""
Functional tests for views

NOTE! If it throws you status 200, that means form submission is failing!

"""

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from timeline_logger.models import TimelineLog

from application.models import Application, UserDetails, ApplicantName, ApplicantPersonalDetails, ApplicantHomeAddress, ChildcareType


class CreateTestNewApplicationSubmit(TestCase):
    """
    Functional test for submitting whole application.
    """

    @classmethod
    def setUp(cls):
        cls.client = Client()
        cls.app_id = None
        cls.order_id = None

    def TestAppInit(self):
        """Start application"""
        r = self.client.post(reverse('Account-View'))
        location = r.get('Location')

        self.app_id = location.split('=')[-1]

        self.assertEqual(r.status_code, 302)

        self.assertTrue(
            Application.objects.get(
                pk=self.app_id
            ).application_status == "DRAFTING"
        )

    def TestAppEmail(self):
        """Submit email"""

        email = 'omelette.du.fromage@gmail.com'

        r = self.client.post(
            reverse('Contact-Email-View'),
            {
                'id': self.app_id,
                'email_address': email
            }
        )

        self.assertEqual(r.status_code, 302)
        self.assertEqual(
            UserDetails.objects.get(application=self.app_id).email, email
        )

    def TestAppPhone(self):
        """Submit phone"""

        data = {
            'id': self.app_id,
            'mobile_number': '07783446526',
            'add_phone_number': ''
        }

        r = self.client.post(reverse('Contact-Phone-View'), data)

        self.assertEqual(r.status_code, 302)
        self.assertEqual(
            UserDetails.objects.get(application=self.app_id).mobile_number, data['mobile_number']
        )

    def TestContactSummaryView(self):
        r = self.client.post(reverse('Contact-Summary-View'), {'id':self.app_id})

        self.assertEqual(
           Application.objects.get(pk=self.app_id).login_details_status, "COMPLETED")

    def TestAppSecurityQuestion(self):
        """Submit security question"""

        data = {
            'id': self.app_id,
            'security_question': 'street born in',
            'security_answer': 'backer street'
        }

        r = self.client.post(reverse('Question-View'), data)

        self.assertEqual(r.status_code, 302)
        self.assertEqual(UserDetails.objects.get(application=self.app_id).security_question, data['security_question'])
        self.assertEqual(UserDetails.objects.get(application=self.app_id).security_answer, data['security_answer'])

    def TestTypeOfChildcareAgeGroups(self):
        """Type of childcare age groups"""

        data = {
            'id': self.app_id,
            'type_of_childcare': ['0-5', '5-8', '8over']
        }

        r = self.client.post(reverse('Type-Of-Childcare-Age-Groups-View'), data)
        self.assertEqual(r.status_code, 302)

        self.assertEqual(ChildcareType.objects.get(application_id=self.app_id).zero_to_five, True)
        self.assertEqual(ChildcareType.objects.get(application_id=self.app_id).five_to_eight, True)
        self.assertEqual(ChildcareType.objects.get(application_id=self.app_id).eight_plus, True)

    def TestTypeOfChildcareOvernightCare(self):
        """Type of childcare overnight care"""

        data = {
            'id': self.app_id,
            'overnight_care': ['True']
        }

        r = self.client.post(reverse('Type-Of-Childcare-Overnight-Care-View'), data)
        self.assertEqual(r.status_code, 302)

        self.assertEqual(ChildcareType.objects.get(application_id=self.app_id).overnight_care, True)

    def TestTypeOfChildcareSummaryView(self):
        r = self.client.post(reverse('Type-Of-Childcare-Summary-View'), {'id':self.app_id})

        self.assertEqual(
           Application.objects.get(pk=self.app_id).childcare_type_status, "COMPLETED")

    def AppTestTypeOfChildcareRegister(self):
        """Type of childcare register"""
        r = self.client.post(reverse('Type-Of-Childcare-Register-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Application.objects.get(pk=self.app_id).childcare_type_status, "COMPLETED")

    def TestAppPersonalDetailsNames(self):
        """Submit your name in Personal details task"""

        data = {
            'id': self.app_id,
            'first_name': "Arthur",
            'middle_names': "Conan",
            'last_name': "Doyle"
        }

        r = self.client.post(reverse('Personal-Details-Name-View'), data)
        self.assertEqual(r.status_code, 302)

        p_id = ApplicantPersonalDetails.objects.get(application_id=Application.objects.get(pk=self.app_id))
        self.assertEqual(ApplicantName.objects.get(personal_detail_id=p_id).first_name, data['first_name'])
        self.assertEqual(ApplicantName.objects.get(personal_detail_id=p_id).middle_names, data['middle_names'])
        self.assertEqual(ApplicantName.objects.get(personal_detail_id=p_id).last_name, data['last_name'])

    def TestAppPersonalDetailsDOB(self):
        """Submit DOB"""
        data = {
            'id': self.app_id,
            'date_of_birth_0': 12,
            'date_of_birth_1': 3,
            'date_of_birth_2': 1987
        }

        r = self.client.post(reverse('Personal-Details-DOB-View'), data)
        self.assertEqual(r.status_code, 302)

        p_id = ApplicantPersonalDetails.objects.get(application_id=Application.objects.get(pk=self.app_id)).personal_detail_id
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_day, data['date_of_birth_0'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_month, data['date_of_birth_1'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_year, data['date_of_birth_2'])

    def TestAppPersonalDetailsHomeAddress(self):
        """Submit Personal Home address"""

        data = {
            'id': self.app_id,
            'street_name_and_number': '43 Lynford Gardens',
            'street_name_and_number2': '',
            'town': 'London',
            'county': 'Essex',
            'postcode': 'IG39LY'
        }

        r = self.client.post(reverse('Personal-Details-Home-Address-Manual-View'), data)
        self.assertEqual(r.status_code, 302)

        p_id = ApplicantPersonalDetails.objects.get(application_id=Application.objects.get(pk=self.app_id)).personal_detail_id
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).street_line1, data['street_name_and_number'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).street_line2, data['street_name_and_number2'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).town, data['town'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).county, data['county'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).postcode, data['postcode'])

    def TestAppPersonalDetailsHomeAddressDetails(self):
        """Submit Personal Home address"""

        data =  {
            'id': self.app_id,
            'location_of_care': True,
        }

        r = self.client.post(
            reverse('Personal-Details-Location-Of-Care-View'), data
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPersonalDetailsSummaryView(self):
        """Personal details summary"""
        self.client.get(reverse('Personal-Details-Summary-View'), {'id': self.app_id})
        self.assertEqual(
            Application.objects.get(pk=self.app_id).personal_details_status, "COMPLETED")

    def TestAppFirstAidStart(self):
        """Start First Aid"""
        r = self.client.post(
            reverse('First-Aid-Training-Guidance-View'),
            {
                'id': self.app_id,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstAid(self):
        """Submit First Aid"""
        r = self.client.post(
            reverse('First-Aid-Training-Details-View'),
            {
                'id': self.app_id,
                'first_aid_training_organisation': 'The Swing Cats Ltd.',
                'title_of_training_course': 'Surviving in the woods',
                'course_date_0': '31',
                'course_date_1': '3',
                'course_date_2': '2016',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstAidCert(self):
        """Submit First Aid certificate"""
        r = self.client.post(
            reverse('First-Aid-Training-Declaration-View'),
            {
                'id': self.app_id,
                'declaration': 'on'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppHealthBooklet(self):
        """Submit Health booklet"""
        r = self.client.post(
            reverse('Health-Booklet-View'),
            {
                'id': self.app_id,
                'send_hdb_declare': 'on'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppCriminalRecordCheckDetails(self):
        """Submit CRC details"""
        r = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.app_id,
                'dbs_certificate_number': '123456789012',
                'convictions': False
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppOtherPeopleAdults(self):
        """Submit other people"""
        r = self.client.post(
            reverse('Other-People-Adult-Question-View'),
            {
                'id': self.app_id,
                'adults_in_home': False,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppOtherPeopleChildren(self):
        """Submit other children"""
        r = self.client.post(
            reverse('Other-People-Children-Question-View'),
            {
                'id': self.app_id,
                'children_in_home': False,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppOtherPeopleSummary(self):
        """Submit Other People Summary"""
        r = self.client.get(reverse('Other-People-Summary-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 200)

        self.assertEqual(Application.objects.get(pk=self.app_id).people_in_home_status, "COMPLETED")

    def TestAppFirstReferenceName(self):
        """Submit first reference name"""
        r = self.client.post(
            reverse('References-First-Reference-View'),
            {
                'id': self.app_id,
                'first_name':'Roman',
                'last_name': 'Gorodeckij',
                'relationship':'My client',
                'time_known_0': 5,
                'time_known_1': 5,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstReferenceAddress(self):
        """Submit First reference address"""
        r = self.client.post(
            reverse('References-First-Reference-Address-View'),
            {
                'id': self.app_id,
                'street_name_and_number': '29 Baker street',
                'street_name_and_number2': '',
                'town': 'London',
                'county': 'Essex',
                'postcode': 'WA157XH',
                'country': 'United Kingdom',
                'manual': True,
                'lookup': False,
                'finish': True,
                'submit': True
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstReferenceContactDetails(self):
        """Submit First reference contact details"""
        r = self.client.post(
            reverse('References-First-Reference-Contact-Details-View'),
            {
                'id': self.app_id,
                'phone_number': '0123456789',
                'email_address': 'info@swingcats.lt',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecondReferenceName(self):
        """Submit Second Reference Name"""

        r = self.client.post(
            reverse('References-Second-Reference-View'),
            {
                'id': self.app_id,
                'first_name':'Sherlock',
                'last_name': 'Holmes',
                'relationship':'My client',
                'time_known_0': 5,
                'time_known_1': 8,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecondReferenceAddress(self):
        """Submit Second Reference Address"""
        r = self.client.post(
            reverse('References-Second-Reference-Address-View'),
            {
                'id': self.app_id,
                'street_name_and_number': '59 Chet street',
                'street_name_and_number2': '',
                'town': 'London',
                'county': 'Essex',
                'postcode': 'WA167GH',
                'country': 'United Kingdom',
                'manual': True,
                'lookup': False,
                'finish': True,
                'submit': True

            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecondReferenceContactDetails(self):
        """Submit Second Reference Contact Details"""
        r = self.client.post(
            reverse('References-Second-Reference-Contact-Details-View'),
            {
                'id': self.app_id,
                'phone_number': '0123456780',
                'email_address': 'it@swingcats.lt',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestReferencesSummary(self):
        """Submit Second Reference Contact Details"""
        r = self.client.get(reverse('References-Summary-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Application.objects.get(pk=self.app_id).references_status, "COMPLETED")

    def TestAppDeclaration(self):
        """Send Declaration"""

        r = self.client.post(
            reverse('Declaration-Declaration-View'),
            {
                'id': self.app_id,
                'background_check_declare': 'on',
                'inspect_home_declare': 'on',
                'interview_declare': 'on',
                'change_declare': 'on',
                'share_info_declare': 'on',
                'information_correct_declare': 'on',
            }
        )
        self.assertEqual(r.status_code, 302)


    def TestAppPaymentMethod(self):
        """Choose payment method"""

        r = self.client.post(
            reverse('Payment-View'),
            {
                'id': self.app_id,
                'payment_method': 'Credit'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPaymentCreditDetails(self):
        """Submit Credit Card details"""

        r = self.client.post(
            reverse('Payment-Details-View'),
            {
                'id': self.app_id,
                'card_type': 'visa',
                'card_number': '5454545454545454',
                'expiry_date_0': 1,
                'expiry_date_1': 2019,
                'cardholders_name': 'Mr Example Cardholder',
                'card_security_code': 123,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPaymentConfirmation(self):
        """Send Payment Confirmation"""

        r = self.client.get(
            reverse('Payment-Confirmation'),
            {
                'id': self.app_id,
                'orderCode': Application.objects.get(application_id=self.app_id).order_code
            }
        )
        self.assertEqual(r.status_code, 200)

    def TestNewApplicationSubmit(self):
        """Submit whole application"""

        self.TestAppInit()

        self.TestAppEmail()
        self.TestAppPhone()
        self.TestContactSummaryView()
        self.TestAppSecurityQuestion()
        self.TestTypeOfChildcareAgeGroups()
        self.TestTypeOfChildcareOvernightCare()
        self.AppTestTypeOfChildcareRegister()

        self.TestAppPersonalDetailsNames()
        self.TestAppPersonalDetailsDOB()
        self.TestAppPersonalDetailsHomeAddress()
        self.TestAppPersonalDetailsHomeAddressDetails()
        self.TestAppPersonalDetailsSummaryView()

        self.TestAppFirstAid()
        self.TestAppFirstAidCert()
        self.TestAppHealthBooklet()

        self.TestAppCriminalRecordCheckDetails()

        self.TestAppOtherPeopleAdults()
        self.TestAppOtherPeopleChildren()
        self.TestAppOtherPeopleSummary()

        self.TestAppFirstReferenceName()
        self.TestAppFirstReferenceAddress()
        self.TestAppFirstReferenceContactDetails()
        self.TestAppSecondReferenceName()
        self.TestAppSecondReferenceAddress()
        self.TestAppSecondReferenceContactDetails()
        self.TestReferencesSummary()

        self.TestAppDeclaration()
        self.TestAppPaymentMethod()
        self.TestAppPaymentCreditDetails()
        self.TestAppPaymentConfirmation()

    def test_new_application_submit(self):
        """
        Test if application been submitted
        """
        self.TestNewApplicationSubmit()

        self.assertTrue(Application.objects.filter(application_id=self.app_id).exists())
        self.assertEqual(Application.objects.get(application_id=self.app_id).application_status, "SUBMITTED")

    def test_new_application_submit_log(self):
        """
        Check if logging works when whole application is submitted
        """
        pass


