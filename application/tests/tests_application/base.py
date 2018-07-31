"""
A base class for reusable test steps across applicaiton unit tests
"""
import json
from datetime import datetime
from unittest import mock
from unittest.mock import Mock

from django.core.urlresolvers import reverse
from django.test import Client

from ...models import (ApplicantHomeAddress,
                       ApplicantName,
                       ApplicantPersonalDetails,
                       Application,
                       ChildcareType,
                       UserDetails)


class ApplicationTestBase(object):

    client = Client()
    app_id = None

    def TestAppInit(self):
        """Start application"""
        r = self.client.post(reverse('Account-Selection'), {'acc_selection': 'new'})
        self.assertEqual(r.status_code, 302)

    def TestAppEmail(self):
        """Submit email"""

        self.email = 'test-address@informed.com'

        r = self.client.post(
            reverse('New-Email'),
            {
                'email_address': self.email
            }
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.email, UserDetails.objects.get(email=self.email).email)

    def TestReturnToApp(self):
        """Tests returning to application for both a new and existing email."""

        self.email = 'omelette.du.fromage@gmail.com'
        new_email = 'cheese.omelette@gmail.com'

        r = self.client.post(
            reverse('Existing-Email'),
            {
                'email_address': self.email
            }
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.email, UserDetails.objects.get(email=self.email).email)

        self.assertEqual(False, UserDetails.objects.filter(email=new_email).exists())
        r = self.client.post(
            reverse('Existing-Email'),
            {
                'email_address': new_email
            }
        )
        self.assertEqual(r.status_code, 302)  # Create account for new email and send link.
        self.assertEqual(new_email, UserDetails.objects.get(email=new_email).email)

    def TestValidateEmail(self):
        """Validate Email"""

        acc = UserDetails.objects.get(email=self.email)
        self.app_id = acc.application_id.pk
        r = self.client.get(
            '/childminder/validate/' + str(acc.magic_link_email), follow=True
        )

        self.assertEqual(r.status_code, 200)
        self.assertTrue(
            Application.objects.get(
                pk=self.app_id
            ).application_status == "DRAFTING"
        )

    def TestAppPhone(self):
        """Submit phone"""

        data = {
            'id': self.app_id,
            'mobile_number': '07783446526',
            'add_phone_number': ''
        }

        r = self.client.post(reverse('Contact-Phone-View'), data)

        acc = UserDetails.objects.get(email=self.email)
        acc.mobile_number = '07783446526'
        acc.save()
        app = Application.objects.get(pk=self.app_id)
        app.login_details_status = "COMPLETED"
        app.save()
        self.assertEqual(r.status_code, 302)
        self.assertEqual(
            UserDetails.objects.get(email=self.email).mobile_number, data['mobile_number']
        )

    def TestContactSummaryView(self):
        self.client.post(reverse('Contact-Summary-View'), {'id': self.app_id})

        self.assertEqual(
            Application.objects.get(pk=self.app_id).login_details_status, "COMPLETED")

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
        r = self.client.post(reverse('Type-Of-Childcare-Summary-View'), {'id': self.app_id})

        self.assertEqual(
            Application.objects.get(pk=self.app_id).childcare_type_status, "COMPLETED")

    def AppTestTypeOfChildcareRegister(self):
        """Type of childcare register"""
        r = self.client.post(reverse('Type-Of-Childcare-Register-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 302)

    def AppTestOvernightCare(self):
        """Overnight care provision"""
        r = self.client.post(reverse('Type-Of-Childcare-Overnight-Care-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Application.objects.get(pk=self.app_id).childcare_type_status, "COMPLETED")

    def TestUpdateEmail(self):
        """Update email address field"""
        r = self.client.post(reverse('Contact-Email-View'), {'id': self.app_id, 'email_address': 'y@y.com'})

        self.assertEqual(r.status_code, 302)
        self.assertIsNot('y@y.com', UserDetails.objects.get(application_id=self.app_id).email)

    def TestUpdateEmailApostrophe(self):
        """Update email address field with apostrophe """
        r = self.client.post(reverse('Contact-Email-View'), {'id': self.app_id, 'email_address': 'yapostrophe\'@y.com'})

        self.assertEqual(r.status_code, 302)
        self.assertIsNot('yapostrophe\'@y.com', UserDetails.objects.get(application_id=self.app_id).email)

    def TestVerifyPhone(self):
        """Test update email address process- update, validate and redirect"""
        self.TestUpdateEmail()
        self.TestValidateEmail()
        r = self.client.post(reverse('Security-Code') + '?id=' + str(self.app_id), {'id': self.app_id,
                                                                                    'magic_link_sms': UserDetails.objects.get(
                                                                                        application_id=self.app_id).magic_link_sms})
        self.assertEqual(r.status_code, 302)

    def TestVerifyPhoneEmailApostrophe(self):
        """Test update email address process with apostrophe in email- update, validate and redirect"""
        self.TestUpdateEmailApostrophe()
        self.TestValidateEmail()
        r = self.client.post(reverse('Security-Code') + '?id=' + str(self.app_id), {'id': self.app_id,
                                                                                    'magic_link_sms': UserDetails.objects.get(
                                                                                        application_id=self.app_id).magic_link_sms})
        self.assertEqual(r.status_code, 302)

    def TestSecurityQuestion(self):
        """Test """
        self.TestAppEmail()
        self.TestValidateEmail()
        r = self.client.post(reverse('Security-Question'), {'id': self.app_id,
                                                            'security_answer': UserDetails.objects.get(
                                                                application_id=self.app_id).mobile_number})

        self.assertEqual(r.status_code, 302)

    def TestAppPersonalDetailsNames(self, data=None):
        """Submit your name in Personal details task"""

        if not data:
            data = {
                'id': self.app_id,
                'first_name': "John-D'Arthur",
                'middle_names': "Conan-Da'vey",
                'last_name': "O'Doyle"
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

        p_id = ApplicantPersonalDetails.objects.get(
            application_id=Application.objects.get(pk=self.app_id)).personal_detail_id
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_day,
                         data['date_of_birth_0'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_month,
                         data['date_of_birth_1'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_year,
                         data['date_of_birth_2'])

    def TestAppPersonalDetailsHomeAddress(self):
        """Submit Personal Home address"""

        data = {
            'id': self.app_id,
            'street_line1': '43 Lynford Gardens',
            'street_line2': '',
            'town': 'London',
            'county': 'Essex',
            'postcode': 'IG39LY'
        }

        r = self.client.post(reverse('Personal-Details-Home-Address-Manual-View'), data)
        self.assertEqual(r.status_code, 302)

        p_id = ApplicantPersonalDetails.objects.get(
            application_id=Application.objects.get(pk=self.app_id)).personal_detail_id
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).street_line1,
                         data['street_line1'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).street_line2,
                         data['street_line2'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).town, data['town'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).county, data['county'])
        self.assertEqual(ApplicantHomeAddress.objects.get(personal_detail_id=p_id).postcode, data['postcode'])

    def TestAppPersonalDetailsHomeAddressDetails(self):
        """Submit Personal Home address"""

        data = {
            'id': self.app_id,
            'childcare_location': True,
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
                'cautions_convictions': False
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

    def TestAppOtherPeopleAdultsDetails(self):
        """Submit other people"""
        data = {
            'id': self.app_id,
            'adults': '1',
            '1-first_name': 'Joseph-Christ\'Opher',
            '1-middle_names': 'Pet\'r-Ivor',
            '1-last_name': 'Chris-J\'oe',
            '1-relationship': 'Son',
            '1-email_address': 'test@email.com',
            '1-date_of_birth_0': '16',
            '1-date_of_birth_1': '6',
            '1-date_of_birth_2': '1984',
            'submit': 1

        }

        r = self.client.post(reverse('Other-People-Adult-Details-View'), data)

        self.assertEqual(r.status_code, 302)

        self.assertEqual(r.wsgi_request.POST['1-first_name'],
                         data['1-first_name'])

        self.assertEqual(r.wsgi_request.POST['1-middle_names'],
                         data['1-middle_names'])

        self.assertEqual(r.wsgi_request.POST['1-last_name'],
                         data['1-last_name'])

        self.assertEqual(r.wsgi_request.POST['1-relationship'],
                         data['1-relationship'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_0'],
                         data['1-date_of_birth_0'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_1'],
                         data['1-date_of_birth_1'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_2'],
                         data['1-date_of_birth_2'])

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

        p_id = ApplicantPersonalDetails.objects.get(
            application_id=Application.objects.get(pk=self.app_id)).personal_detail_id
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_day,
                         data['date_of_birth_0'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_month,
                         data['date_of_birth_1'])
        self.assertEqual(ApplicantPersonalDetails.objects.get(personal_detail_id=p_id).birth_year,
                         data['date_of_birth_2'])

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

    def TestAppOtherPeopleChildrenDetails(self):
        """Submit other people"""
        # get a birth date year that is actually valid for a child (within the last 10 years from now will do)
        birth_year = str(datetime.now().year - 10)

        data = {
            'id': self.app_id,
            'children': '1',
            '1-first_name': 'Joseph-Christ\'Opher',
            '1-middle_names': 'Pet\'r-Ivor',
            '1-last_name': 'Chris-J\'oe',
            '1-relationship': 'Son',
            '1-date_of_birth_0': '16',
            '1-date_of_birth_1': '6',
            '1-date_of_birth_2': birth_year,
            'submit': 1

        }

        r = self.client.post(reverse('Other-People-Children-Details-View'), data)

        self.assertEqual(r.status_code, 302)

        self.assertEqual(r.wsgi_request.POST['1-first_name'],
                         data['1-first_name'])

        self.assertEqual(r.wsgi_request.POST['1-middle_names'],
                         data['1-middle_names'])

        self.assertEqual(r.wsgi_request.POST['1-last_name'],
                         data['1-last_name'])

        self.assertEqual(r.wsgi_request.POST['1-relationship'],
                         data['1-relationship'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_0'],
                         data['1-date_of_birth_0'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_1'],
                         data['1-date_of_birth_1'])

        self.assertEqual(r.wsgi_request.POST['1-date_of_birth_2'],
                         data['1-date_of_birth_2'])

    def TestAppOtherPeopleSummary(self):
        """Submit Other People Summary"""
        r = self.client.get(reverse('Other-People-Summary-View'), {'id': self.app_id})
        self.assertEqual(r.status_code, 200)

    def TestAppFirstReferenceName(self):
        """Submit first reference name"""
        r = self.client.post(
            reverse('References-First-Reference-View'),
            {
                'id': self.app_id,
                'first_name': 'Roman',
                'last_name': 'Gorodeckij',
                'relationship': 'My client',
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
                'street_line1': '29 Baker street',
                'street_line2': '',
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
                'first_name': 'Sherlock',
                'last_name': 'Holmes',
                'relationship': 'My client',
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
                'street_line1': '59 Chet street',
                'street_line2': '',
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

    def TestAppSecondReferenceContactDetails(self, data=None):
        """Submit Second Reference Contact Details"""

        if not data:
            data = {
                'id': self.app_id,
                'phone_number': '0123456780',
                'email_address': 'it@swingcats.lt',
            }

        r = self.client.post(
            reverse('References-Second-Reference-Contact-Details-View'), data)
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
                'suitable_declare': 'on',
            }
        )
        self.assertEqual(r.status_code, 302)

    def TestAppPaymentCreditDetails(self):
        """Submit Credit Card details"""

        with mock.patch('application.services.payment_service.make_payment') as post_payment_mock, \
                mock.patch('application.services.noo_integration_service.create_application_reference') as application_reference_mock:
            test_payment_response = {
                "customerOrderCode": "TEST",
                "lastEvent": "AUTHORISED"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            application_reference_mock.return_value = 'TESTURN'

            r = self.client.post(
                reverse('Payment-Details-View'),
                {
                    'id': self.app_id,
                    'card_type': 'visa',
                    'card_number': '5454545454545454',
                    'expiry_date_0': 1,
                    'expiry_date_1': 19,
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
                'orderCode': Application.objects.get(application_id=self.app_id).application_reference
            }
        )

        self.assertEqual(r.status_code, 200)

    def TestAppArcFlaggedStatuses(self):
        """Test that field_arc_flagged is false once successful declaration has been made."""
        app = Application.objects.get(application_id=self.app_id)

        flagged_fields_to_check = (
            "childcare_type_arc_flagged",
            "criminal_record_check_arc_flagged",
            "eyfs_training_arc_flagged",
            "first_aid_training_arc_flagged",
            "health_arc_flagged",
            "login_details_arc_flagged",
            "people_in_home_arc_flagged",
            "personal_details_arc_flagged",
            "references_arc_flagged"
        )

        for field in flagged_fields_to_check:
            setattr(app, field, True)  # Set flagged_fields to true.

        app.save()

        r = self.client.post(
            reverse('Declaration-Declaration-View'),
            {
                'id': self.app_id,
                'share_info_declare': True,
                'suitable_declare': True,
                'information_correct_declare': True,
                'change_declare': True,
                'display_contact_details_on_web': True
            }
        )

        app = Application.objects.get(application_id=self.app_id)

        for field in flagged_fields_to_check:
            self.assertFalse(getattr(app, field))  # Assert flagged_fields are false.
