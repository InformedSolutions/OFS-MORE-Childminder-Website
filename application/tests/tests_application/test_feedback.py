"""
Functional tests for feedback page

NOTE! If it throws you status 200, that means form submission is failing!

"""
from unittest import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from .base import ApplicationTestBase


class FeedbackTests(TestCase, ApplicationTestBase):

    def test_feedback_successfully_submitted(self):
        """
        Test to assert that feedback is successfully submitted when valid feedback is entered
        """

        with mock.patch('application.notify.send_email') as post_email_mock:
            post_email_mock.return_value.status_code = 201

            # POST valid input to feedback page
            response = self.client.post(
                reverse('Feedback'),
                {
                    'feedback': 'Test feedback',
                    'email_address': 'tester@informed.com',
                    'url': reverse('Start-Page-View')
                }
            )

            self.assertEqual(response.status_code, 302)

    def test_feedback_successfully_submitted_no_email(self):
        """
        Test to assert that feedback is successfully submitted when valid feedback is entered (without email address)
        """

        with mock.patch('application.notify.send_email') as post_email_mock:
            post_email_mock.return_value.status_code = 201

            # POST valid input to feedback page
            response = self.client.post(
                reverse('Feedback'),
                {
                    'feedback': 'Test feedback',
                    'email_address': '',
                    'url': reverse('Start-Page-View')
                }
            )

            self.assertEqual(response.status_code, 302)

    def test_invalid_feedback_submitted(self):
        """
        Test to assert that feedback is not submitted when invalid feedback is entered
        """

        with mock.patch('application.notify.send_email') as post_email_mock:
            post_email_mock.return_value.status_code = 201

            # POST valid input to feedback page
            response = self.client.post(
                reverse('Feedback'),
                {
                    'feedback': '',
                    'email_address': 'tester@informed.com',
                    'url': reverse('Start-Page-View')
                }
            )

            self.assertEqual(response.status_code, 200)

            # Assert taken to the feedback confirmation page
            self.assertEqual(response.resolver_match.view_name, 'Feedback')

            error = response.context['field_errors'].values()
            error_message = len(list(error))

            # Assert error message returned to user
            self.assertEqual(error_message, 1)
