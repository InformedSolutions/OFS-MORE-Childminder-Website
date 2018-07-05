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

            # POST to feedback page
            response = self.client.post(
                reverse('Feedback'),
                {
                    'feedback': 'Test feedback',
                    'email_address': 'tester@informed.com',
                    'url': reverse('Start-Page-View')
                }
            )

            print(reverse('Start-Page-View'))

            self.assertEqual(response.status_code, 201)

            # Assert taken to the feedback confirmation page
            self.assertEqual(response.resolver_match.view_name, 'Feedback-Confirmation')

            # # Assert error message returned to user
            # self.assertEqual(response.context['non_field_errors'].data[0].message,
            #                  'There has been a problem when trying to process your payment. '
            #                  'Your card has not been charged. '
            #                  'Please check your card details and try again.')
            #