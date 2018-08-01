"""
Tests for assuring the application reference number generation process
"""
import json
from unittest import mock
from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase

from ...services.noo_integration_service import create_application_reference


class ApplicationReferenceTests(TestCase):

    test_discriminator = settings.APPLICATION_PREFIX

    def test_can_produce_application_reference(self):
        with mock.patch('requests.get') as request_get_mock:
            test_urn_response = {
              "URN": 123456789
            }

            request_get_mock.return_value.status_code = 201
            request_get_mock.return_value.text = json.dumps(test_urn_response)
            request_get_mock.return_value.json = Mock(
                return_value=test_urn_response
            )

            test_reference_number = create_application_reference()
            self.assertIsNotNone(test_reference_number)
