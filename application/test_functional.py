"""
Functional tests for views
"""

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from .models import Application, UserDetails


class CreateTestNewApplicationSubmit(TestCase):

    @classmethod
    def setUp(cls):
        cls.client = Client()
        cls.application_id = None
        cls.app_id = None
        cls.order_id = None

    def TestAppInit(self):
        r = self.client.post(reverse('Account-View'))
        location = r.get('Location')

        self.application_id = location.split('=')[-1]
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
                'id': self.application_id,
                'email_address': email
            }
        )

        #print(UserDetails.get_id(app_id=self.app_id).login_id)

        self.assertEqual(r.status_code, 302)
        #self.assertTrue(
        #    UserDetails.get_id(app_id=self.app_id).email == email
        #)

    def TestAppPhone(self):
        r = self.client.post(
            reverse('Contact-Phone-View'),
            {
                'id': self.application_id,
                'mobile_number': '07783446526',
                'add_phone_number': ''
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecurityQuestion(self):
        r = self.client.post(
            reverse('Question-View'),
            {
             'id': self.application_id,
             'security_question': 'street born in',
             'security_answer': 'backer street'
            }
        )
        self.assertEqual(r.status_code, 302)

        print(Application.objects.get(pk=self.app_id).login_details_status)

        self.assertTrue(
            Application.objects.get(pk=self.app_id).login_details_status == "COMPLETED")


    def TestAppPersonalDetailsNames(self):
        r = self.client.post(
            reverse('Personal-Details-Name-View'),
            {
                'id': self.application_id,
                'first_name': "Arthur",
                'middle_names': "Conan",
                'last_name': "Doyle"
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPersonalDetailsDOB(self):
        r = self.client.post(
            reverse('Personal-Details-DOB-View'),
            {
                'id': self.application_id,
                'date_of_birth_0': '12',
                'date_of_birth_1': '03',
                'date_of_birth_2': '1987'
            }
        )
        self.assertEqual(r.status_code, 302)

    def  TestAppPersonalDetailsHomeAddress(self):
        r = self.client.post(
            reverse('Personal-Details-Home-Address-Manual-View'),
            {
                'id': self.application_id,
                'street_name_and_number': '43 Lynford Gardens',
                'street_name_and_number2': '',
                'town': 'London',
                'county': 'Essex',
                'postcode': 'IG39LY'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPersonalDetailsHomeAddressDetails(self):
        r = self.client.post(
            reverse('Personal-Details-Location-Of-Care-View'),
            {
                'id': self.application_id,
                'date_of_birth_0': '12',
                'date_of_birth_1': '03',
                'date_of_birth_2': '1987'
            }
        )
        self.assertEqual(r.status_code, 200)

    def TestAppFirstAidStart(self):
        r = self.client.post(
            reverse('First-Aid-Training-Guidance-View'),
            {
                'id': self.application_id,
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstAid(self):
        r = self.client.post(
            reverse('First-Aid-Training-Details-View'),
            {
                'id': self.application_id,
                'first_aid_training_organisation': 'The Swing Cats Ltd.',
                'title_of_training_course': 'Surviving in the woods',
                'course_date_0': '31',
                'course_date_1': '3',
                'course_date_2': '2016',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstAidCert(self):
        r = self.client.post(
            reverse('First-Aid-Training-Declaration-View'),
            {
                'id': self.application_id,
                'declaration': 'on'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppHealthBooklet(self):
        r = self.client.post(
            reverse('Health-Booklet-View'),
            {
                'id': self.application_id,
                'send_hdb_declare': 'on'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppCriminalRecordCheckDetails(self):
        r = self.client.post(
            reverse('DBS-Check-DBS-Details-View'),
            {
                'id': self.application_id,
                'dbs_certificate_number': '123456789012',
                'convictions': 'false'
            }
        )
        self.assertEqual(r.status_code, 200)

    def TestAppOtherPeopleAdults(self):
        r = self.client.post(
            reverse('Other-People-Guidance-View'),
            {
                'id': self.application_id,
                'adults_in_home':'no',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppOtherPeopleChildren(self):
        r = self.client.post(
            reverse('Other-People-Guidance-View'),
            {
                'id': self.application_id,
                'children_in_home':'no',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstReferenceName(self):
        r = self.client.post(
            reverse('References-First-Reference-View'),
            {
                'id': self.application_id,
                'first_name':'Roman',
                'last_name': 'Gorodeckij',
                'relationship':'My client',
                'time_known_0': '5',
                'time_known_1': '5',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppFirstReferenceAddress(self):
        r = self.client.post(
            reverse('References-First-Reference-Address-View'),
            {
                'id': self.application_id,
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
        r = self.client.post(
            reverse('References-First-Reference-Contact-Details-View'),
            {
                'id': self.application_id,
                'phone_number': '0123456789',
                'email_address': 'info@swingcats.lt',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecondReferenceName(self):
        r = self.client.post(
            reverse('References-Second-Reference-View'),
            {
                'id': self.application_id,
                'first_name':'Sherlock',
                'last_name': 'Holmes',
                'relationship':'My client',
                'time_known_0': '5',
                'time_known_1': '8',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppSecondReferenceAddress(self):
        r = self.client.post(
            reverse('References-Second-Reference-Address-View'),
            {
                'id': self.application_id,
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
        r = self.client.post(
            reverse('References-Second-Reference-Contact-Details-View'),
            {
                'id': self.application_id,
                'phone_number': '0123456780',
                'email_address': 'it@swingcats.lt',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppDeclaration(self):
        r = self.client.post(
            reverse('Declaration-Declaration-View'),
            {
                'id': self.application_id,
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
        r = self.client.post(
            reverse('Payment-View'),
            {
                'id': self.application_id,
                'payment_method': 'Credit'
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPaymentCreditDetails(self):
        r = self.client.post(
            reverse('Payment-Details-View'),
            {
                'id': self.application_id,
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
        r = self.client.get(
            reverse('Payment-Confirmation'),
            {
                'id': self.application_id,
                'orderCode': Application.objects.get(application_id=self.application_id).order_code
            }
        )

    def TestNewApplicationSubmit(self):
        self.TestAppInit()
        self.TestAppEmail()
        self.TestAppPhone()
        self.TestAppSecurityQuestion()
        self.TestAppPersonalDetailsNames()
        self.TestAppPersonalDetailsDOB()
        self.TestAppPersonalDetailsHomeAddress()
        self.TestAppPersonalDetailsHomeAddressDetails()
        self.TestAppFirstAid()
        self.TestAppFirstAidCert()
        self.TestAppHealthBooklet()
        self.TestAppCriminalRecordCheckDetails()
        self.TestAppOtherPeopleAdults()
        self.TestAppOtherPeopleChildren()
        self.TestAppFirstReferenceName()
        self.TestAppFirstReferenceAddress()
        self.TestAppFirstReferenceContactDetails()
        self.TestAppSecondReferenceName()
        self.TestAppSecondReferenceAddress()
        self.TestAppSecondReferenceContactDetails()
        self.TestAppDeclaration()
        self.TestAppPaymentMethod()
#        self.TestAppPaymentCreditDetails()
#        self.TestAppPaymentConfirmation()

    def test_new_application_submit(self):
        """
        Test whole application submission process
        """
        self.TestNewApplicationSubmit()
        self.assertTrue(Application.objects.filter(application_id=self.application_id).exists())
        #print(Application.objects.values_list(flat=True).filter(pk=self.application_id).values())

#        self.assertTrue(Application.objects.get(application_id=self.application_id).application_status == "SUBMITTED")

    def test_new_application_submit_log(self):
        """
        Check if logging works when whole application is submitted
        """
        pass


