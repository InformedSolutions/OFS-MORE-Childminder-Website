"""
Tests targetting the payment process
"""

from unittest import mock

from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone

from .base import ApplicationTestBase
from ...payment_service import *
from ...models import Payment, Application
from application import dbs
from application import models
from application.views.payment import get_template
from application.views import payment as payment_views
from application.business_logic import get_childcare_register_type



class PaymentTests(TestCase, ApplicationTestBase):

    def setUp(self):
        with mock.patch('application.notify.send_email') as notify_mock, \
            mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:

            notify_connection_test_mock.return_value.status_code = 201
            notify_mock.return_value.status_code = 201

            # Initial steps required here as client object needs to be authenticated to
            # access payment pages
            self.TestAppInit()

            self.test_app_email()
            self.TestValidateEmail()
            self.TestAppPhone()
            self.TestContactSummaryView()
            self.TestTypeOfChildcareAgeGroups()
            self.TestTypeOfChildcareOvernightCare()
            self.TestSecurityQuestion()
            self.AppTestTypeOfChildcareRegister()

            self.TestAppPersonalDetailsNames()

    def test_payment_reference_formatted(self):
        test_cm_reference = 'CM1000000'
        formatted_reference = created_formatted_payment_reference(test_cm_reference)
        more_prefix_in_payment_reference = formatted_reference[:4]
        reference_in_payment_reference = formatted_reference[5:14]
        timestamp_date = formatted_reference[15:23]

        # Reference should include MORE prefix, full reference number, two colons and a yyyymmddhhmmss timestamp
        self.assertEqual(len(formatted_reference), 29)
        self.assertEqual('MORE', more_prefix_in_payment_reference)
        self.assertEqual(test_cm_reference, reference_in_payment_reference)
        self.assertEqual(timestamp_date, time.strftime("%Y%m%d"))

    def test_payment_creation_failure_raises_exception(self):
        """
        Test that if a failure is encountered when attempting to first lodge a payment with Worldpay,
        an error gets returned to the user
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock:
            test_payment_response = {
              'message': 'Internal Server error',
              'error': 'Test error',
            }

            post_payment_mock.return_value.status_code = 500
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            response = self.client.post(
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

            self.assertEqual(response.status_code, 200)

            # Assert taken back to the payment page
            self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

            # Assert error message returned to user
            self.assertEqual(response.context['non_field_errors'].data[0].message,
                             'There has been a problem when trying to process your payment. '
                             'Your card has not been charged. '
                             'Please check your card details and try again.')

    def test_payment_not_found_raises_exception(self):
        """
        Tests that if a payment cannot be reconciled once lodged, an error is raised to the user.
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock, \
                mock.patch('application.payment_service.check_payment') as check_payment_mock:
            test_payment_response = {
                "amount": 50000,
                "cardHolderName": "Mr Example Cardholder",
                "cardNumber": 5454545454545454,
                "cvc": 352,
                "expiryMonth": 6,
                "expiryYear": 2018,
                "currencyCode": "GBP",
                "customerOrderCode": "TEST_ORDER_CODE",
                "orderDescription": "Childminder Registration Fee"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            check_payment_mock.return_value.status_code = 404

            response = self.client.post(
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

            self.assertEqual(response.status_code, 200)

            # Assert taken back to the payment page
            self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

            # Assert error message returned to user
            self.assertEqual(response.context['non_field_errors'].data[0].message,
                             'There has been a problem when trying to process your payment. '
                             'Your card has not been charged. '
                             'Please check your card details and try again.')

    def test_refused_payment_shows_error(self):
        """
        Tests that if a payment has been refused by Worldpay an error is shown.
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock:
            test_payment_response = {
                "customerOrderCode": "TEST",
                "lastEvent": "REFUSED"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            response = self.client.post(
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

            self.assertEqual(response.status_code, 200)

            # Check that initial payment attempt was rolled back
            self.assertFalse(Payment.objects.filter(application_id=self.app_id).exists())

            # Assert taken back to the payment page
            self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

            # Assert error message returned to user
            self.assertEqual(response.context['non_field_errors'].data[0].message,
                             'There has been a problem when trying to process your payment. '
                             'Your card has not been charged. '
                             'Please check your card details and try again.')

    def test_payment_duplicate_payment_not_lodged(self):
        """
        Test to assert that if a payment is submitted for a second time
        it is not placed as a second Worldpay order and the original payment reference
        is retained
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock:
            test_payment_response = {
                "customerOrderCode": "TEST",
                "lastEvent": "AUTHORISED"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            # POST to submission page twice
            self.client.post(
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

            # Assert payment has been marked as submitted following first submission to Worldpay
            payment_record = Payment.objects.get(application_id=self.app_id)
            initial_payment_reference = payment_record.payment_reference

            self.assertIsNotNone(initial_payment_reference)
            self.assertTrue(payment_record.payment_submitted)

            response = self.client.post(
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

            # Ensure only 1 request to lodge payment was made during the above two consecutive calls
            self.assertEqual(post_payment_mock.call_count, 1)

            # Test original payment reference retained
            payment_record.refresh_from_db()
            self.assertEqual(payment_record.payment_reference, initial_payment_reference)

            self.assertEqual(response.status_code, 200)

            # Assert taken back to the payment page
            self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

            # Assert error message returned to user
            self.assertEqual(response.context['non_field_errors'].data[0].message,
                             'There has been a problem when trying to process your payment. '
                             'Your card has not been charged. '
                             'Please check your card details and try again.')

    def test_payment_duplicate_payment_not_lodged(self):
        """
        Test to assert that if a payment is submitted for a second time
        it is not placed as a second Worldpay order and the original payment reference
        is retained
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock:
            test_payment_response = {
                "customerOrderCode": "TEST",
                "lastEvent": "AUTHORISED"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            # POST to submission page twice
            self.client.post(
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

            # Assert payment has been marked as submitted following first submission to Worldpay
            payment_record = Payment.objects.get(application_id=self.app_id)
            initial_payment_reference = payment_record.payment_reference

            self.assertIsNotNone(initial_payment_reference)
            self.assertTrue(payment_record.payment_submitted)

            response = self.client.post(
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

            # Ensure only 1 request to lodge payment was made during the above two consecutive calls
            self.assertEqual(post_payment_mock.call_count, 1)

            # Test original payment reference retained
            payment_record.refresh_from_db()
            self.assertEqual(payment_record.payment_reference, initial_payment_reference)

            self.assertEqual(response.status_code, 200)

            # Assert taken back to the payment page
            self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

            # Assert error message returned to user
            self.assertEqual(response.context['non_field_errors'].data[0].message,
                             'There has been a problem when trying to process your payment. '
                             'Your card has not been charged. '
                             'Please check your card details and try again.')

    def test_can_lodge_valid_payment(self):
        """
        Full test to ensure that when a payment is taken the following outcomes are met:
           1. Payment confirmation page is shown
           2. Application Reference number assigned
           3. Payment record is lodged
        """

        with mock.patch('application.payment_service.make_payment') as post_payment_mock:
            test_payment_response = {
                "customerOrderCode": "TEST",
                "lastEvent": "AUTHORISED"
            }

            post_payment_mock.return_value.status_code = 201
            post_payment_mock.return_value.text = json.dumps(test_payment_response)

            response = self.client.post(
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

            # 1. Assert confirmation page shown
            self.assertEqual(response.status_code, 302)
            redirect_target = resolve(response.url)
            self.assertEqual(redirect_target.view_name, 'Payment-Confirmation')

            # 2. Assert application reference assigned and marked as submitted
            application = Application.objects.get(pk=self.app_id)
            self.assertIsNotNone(application.application_reference)
            self.assertIsNotNone(application.date_submitted)

            # 3.Assert payment record created and marked appropriately
            payment_record = Payment.objects.get(application_id=self.app_id)
            self.assertIsNotNone(payment_record.payment_reference)
            self.assertTrue(payment_record.payment_submitted)
            self.assertTrue(payment_record.payment_authorised)

    def test_email_template_HDB_DBS_only(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)

        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=True,
            five_to_eight=False,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='001630091191',
            lived_abroad=False,
            capita=True,
            certificate_information=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '35', 'ref': None},
                                               '02c01f75-1f9d-428f-a862-4effac03ebd3')
            crc.delete()

    def test_email_template_HDB_DBS_and_lived_abroad(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)

        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=True,
            five_to_eight=False,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='001630091191',
            lived_abroad=True,
            capita=True,
            certificate_information=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '35', 'ref': None},
                                               'c82b8ffd-f67c-4019-a724-d57ab559f08e')
            crc.delete()

    def test_email_template_HDB_update_service_DBS_only(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)


        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=True,
            five_to_eight=False,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789012',
            lived_abroad=False,
            capita=False,
            on_update=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '35', 'ref': None},
                                               '02c01f75-1f9d-428f-a862-4effac03ebd3')
            crc.delete()

    def test_email_template_HDB_update_service_DBS_and_lived_abroad(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)


        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=True,
            five_to_eight=False,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789012',
            lived_abroad=True,
            capita=False,
            on_update=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '35', 'ref': None},
                                               'c82b8ffd-f67c-4019-a724-d57ab559f08e')
            crc.delete()

    def test_email_template_DBS_only(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)

        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='001630091191',
            lived_abroad=False,
            capita=True,
            certificate_information=True
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '103', 'ref': None},
                                               '294f2710-c507-4d30-ae64-b5451c59a45c')
            crc.delete()

    def test_email_template_DBS_and_lived_abroad(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)


        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='001630091191',
            lived_abroad=True,
            capita=True,
            certificate_information=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '103', 'ref': None},
                                               '94190a2d-d1c7-46c6-8144-da38141aa027')
            crc.delete()

    def test_email_template_update_service_DBS_only(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)


        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789012',
            lived_abroad=False,
            capita=False,
            on_update=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '103', 'ref': None},
                                               '294f2710-c507-4d30-ae64-b5451c59a45c')
            crc.delete()

    def test_email_template_update_service_DBS_and_lived_abroad(self):
        app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.url_suffix = '?id=' + str(app_id)


        application = models.Application.objects.create(
            application_id=app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
        )

        models.UserDetails.objects.create(
            application_id=application,
            email="test@informed.com"
        )

        pd_id = models.ApplicantPersonalDetails.objects.create(
            application_id=application,
        )

        models.ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=pd_id,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        models.ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=False,
            overnight_care=False,
        )

        crc = models.CriminalRecordCheck.objects.create(
            application_id=application,
            dbs_certificate_number='123456789012',
            lived_abroad=False,
            capita=False,
            on_update=True,
        )

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        with mock.patch.object(payment_views, 'send_email') as send_email_mock:
            get_template(crc, app_id, application, childcare_register_cost, childcare_register_type)

            send_email_mock.assert_called_with('test@informed.com', {'firstName': 'Test', 'cost': '103', 'ref': None},
                                               '94190a2d-d1c7-46c6-8144-da38141aa027')
            crc.delete()