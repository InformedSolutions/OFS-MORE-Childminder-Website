"""
Tests targetting the payment process
"""

from unittest import mock

from django.test import TestCase, tag
from django.urls import reverse, resolve

from .base import ApplicationTestBase
from ...payment_service import *
from ...models import Payment, Application


class YourChildrenTests(TestCase, ApplicationTestBase):

    def setUp(self):
        with mock.patch('application.notify.send_email') as notify_mock, \
            mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:

            notify_connection_test_mock.return_value.status_code = 201
            notify_mock.return_value.status_code = 201

            # Initial steps required here as client object needs to be authenticated to
            # access payment pages
            self.TestAppInit()

            self.TestAppEmail()
            self.TestValidateEmail()
            self.TestAppPhone()
            self.TestContactSummaryView()
            self.TestTypeOfChildcareAgeGroups()
            self.TestTypeOfChildcareOvernightCare()
            self.TestSecurityQuestion()
            self.AppTestTypeOfChildcareRegister()

            self.TestAppPersonalDetailsNames()

    @tag('http')
    def test_can_access_own_children_guidance_page(self):
        response = self.client.get(
            reverse('Your-Children-Guidance-View'),
            {
                'id': self.app_id,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Guidance-View')

        self.assertTrue('<title>Your children</title>' in str(response.content))

    @tag('http')
    def test_can_progress_past_guidance_page(self):
        response = self.client.post(
            reverse('Your-Children-Guidance-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')

        self.assertTrue('<title>Details of your children</title>' in str(response.content))

    @tag('http')
    def test_can_submit_with_single_child(self):
        response = self.client.post(
            reverse('Your-Children-Details-View'),
            {
                'id': self.app_id,
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, 'Your-Children-Details-View')

        self.assertTrue('<title>Details of your children</title>' in str(response.content))
