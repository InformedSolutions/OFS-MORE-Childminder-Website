import json
import uuid
from unittest import mock
from unittest.mock import Mock

from django.test import modify_settings

from application.models import ChildcareType, Payment, ApplicantPersonalDetails, ApplicantName

from .view_parent import *
from datetime import datetime, timedelta


class PaymentTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/')
        self.assertEqual(found.func, payment)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/payment/details/')
        self.assertEqual(found.func, card_payment_details)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/payment/details/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/paypal-payment-completion/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/confirmation/')
        self.assertEqual(found.func, payment_confirmation)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/confirmation/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Documents'))
        self.assertEqual(found.func, documents_needed)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Documents') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Home'))
        self.assertEqual(found.func, home_ready)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Home') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    def test_url_resolves_to_page(self):
        found = resolve(reverse('Next-Steps-Interview'))
        self.assertEqual(found.func, prepare_for_interview)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(reverse('Next-Steps-Interview') + '?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)

    @modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler',
        ]
    })
    def test_payment_for_childcare_registers(self):
        """
        Assert that payment can still be submitted if applicant not applying for Early Years.
        :return:
        """
        next_year = datetime.today() + timedelta(days=366)
        short_year = next_year.strftime('%y')

        c = Client()
        app_id = uuid.uuid4()
        application = Application.objects.create(
            application_id=app_id
        )
        ChildcareType.objects.create(
            application_id=application,
            zero_to_five=False,
            five_to_eight=True,
            eight_plus=True,
            childcare_places=3,
            weekday_before_school=True,
            weekday_after_school=True,
            weekday_am=False,
            weekday_pm=False,
            weekday_all_day=False,
            weekend_all_day=False,
            overnight_care=True

        )
        UserDetails.objects.create(
            application_id=application,
            email='test@informed.com'
        )
        personal_details = ApplicantPersonalDetails.objects.create(
            application_id=application
        )
        ApplicantName.objects.create(
            application_id=application,
            personal_detail_id=personal_details,
            current_name=True,
            first_name='test'
        )

        try:
            with mock.patch('requests.get') as request_get_mock:
                test_urn_response = {
                    "URN": 123456789
                }

                request_get_mock.return_value.status_code = 201
                request_get_mock.return_value.text = json.dumps(test_urn_response)
                request_get_mock.return_value.json = Mock(
                    return_value=test_urn_response
                )

                response = c.post(reverse('Payment-Details-View') + '?id=' + str(app_id),
                    {
                        'id': app_id,
                        'card_type': 'visa',
                        'card_number': '5454545454545454',
                        'expiry_date_0': 1,
                        'expiry_date_1': short_year,
                        'cardholders_name': 'Mr Example Cardholder',
                        'card_security_code': 123,
                    })
                payment_obj = Payment.objects.get(application_id=app_id)
                self.assertTrue(payment_obj.payment_submitted)
                self.assertTrue(payment_obj.payment_authorised)

                self.assertEqual(response.status_code, 302)
        except Exception as e:
            self.fail(e)