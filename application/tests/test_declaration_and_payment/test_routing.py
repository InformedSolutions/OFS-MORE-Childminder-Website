import json
from unittest import mock

from django.test import tag
from django.urls import reverse, resolve

from application import models, views
from application.tests import utils


@tag('http')
class DeclarationSummaryPageFunctionalTests(utils.NoMiddlewareTestCase):

    def setUp(self):
        self.application = utils.make_test_application()
        self.adult_in_home = models.AdultInHome.objects.get(application_id=self.application.pk)

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
        self.adult_in_home.PITH_same_address=True
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


@tag('http')
class PaymentPageFunctionalTests(utils.NoMiddlewareTestCase):

    def setUp(self):
        self.application = utils.make_test_application()
        self.app_id = self.application.application_id

    @mock.patch('application.messaging.SQSHandler.send_message')
    @mock.patch('application.services.noo_integration_service.create_application_reference')
    @mock.patch('application.services.payment_service.make_payment')
    def test_submit_returns_to_payment_page_with_error_if_status_500_received(
            self, post_payment_mock, application_reference_mock, send_message_mock):
        """
        Test that if a failure is encountered when attempting to first lodge a payment with Worldpay,
        an error gets returned to the user
        """
        application_reference_mock.return_value = 'TESTURN'

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

    @mock.patch('application.messaging.SQSHandler.send_message')
    @mock.patch('application.services.noo_integration_service.create_application_reference')
    @mock.patch('application.services.payment_service.check_payment')
    @mock.patch('application.services.payment_service.make_payment')
    def test_submit_returns_to_payment_page_with_error_if_status_404_received(
            self, post_payment_mock, check_payment_mock, application_reference_mock, send_message_mock):
        """
        Tests that if a payment cannot be reconciled once lodged, an error is raised to the user.
        """
        application_reference_mock.return_value = 'TESTURN'

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

    @mock.patch('application.messaging.SQSHandler.send_message')
    @mock.patch('application.services.noo_integration_service.create_application_reference')
    @mock.patch('application.services.payment_service.make_payment')
    def test_submit_returns_to_payment_page_with_error_if_REFUSED_received(
            self, post_payment_mock, application_reference_mock, send_message_mock):
        """
        Tests that if a payment has been refused by Worldpay an error is shown.
        """
        application_reference_mock.return_value = 'TESTURN'

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
        self.assertFalse(models.Payment.objects.filter(application_id=self.app_id).exists())

        # Assert taken back to the payment page
        self.assertEqual(response.resolver_match.view_name, 'Payment-Details-View')

        # Assert error message returned to user
        self.assertEqual(response.context['non_field_errors'].data[0].message,
                         'There has been a problem when trying to process your payment. '
                         'Your card has not been charged. '
                         'Please check your card details and try again.')

    @mock.patch('application.messaging.SQSHandler.send_message')
    @mock.patch('application.services.noo_integration_service.create_application_reference')
    @mock.patch('application.services.payment_service.make_payment')
    def test_resubmit_doesnt_place_second_worldpay_order_and_original_payment_ref_is_retained(
            self, post_payment_mock, application_reference_mock, send_message_mock):
        """
        Test to assert that if a payment is submitted for a second time
        it is not placed as a second Worldpay order and the original payment reference
        is retained
        """
        application_reference_mock.return_value = 'TESTURN'

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
        payment_record = models.Payment.objects.get(application_id=self.app_id)
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

    @mock.patch('application.messaging.SQSHandler.send_message')
    @mock.patch('application.services.noo_integration_service.create_application_reference')
    @mock.patch('application.services.payment_service.make_payment')
    def test_submit_lodges_payment_and_assigns_ref_and_redirects_to_confirmation_page_if_valid(
            self, post_payment_mock, application_reference_mock, send_message_mock):
        """
        Full test to ensure that when a payment is taken the following outcomes are met:
           1. Payment confirmation page is shown
           2. Application Reference number assigned
           3. Payment record is lodged
        """
        application_reference_mock.return_value = 'TESTURN'

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
        application = models.Application.objects.get(pk=self.app_id)
        self.assertIsNotNone(application.application_reference)
        self.assertIsNotNone(application.date_submitted)

        # 3.Assert payment record created and marked appropriately
        payment_record = models.Payment.objects.get(application_id=self.app_id)
        self.assertIsNotNone(payment_record.payment_reference)
        self.assertTrue(payment_record.payment_submitted)
        self.assertTrue(payment_record.payment_authorised)

