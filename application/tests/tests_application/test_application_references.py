"""
Tests for assuring the application reference number generation process
"""
import re

from django.conf import settings
from django.test import TestCase

from ...models import ApplicationReference
from ...application_reference_generator import create_application_reference


class ApplicationReferenceTests(TestCase):

    test_discriminator = settings.APPLICATION_PREFIX

    def test_application_discriminator_applied(self):
        test_reference_number = create_application_reference()
        reference_number_discriminator = test_reference_number[:2]
        self.assertEqual(reference_number_discriminator, self.test_discriminator)

    def test_application_reference_seeding_number_set(self):
        # Test to assert seed reference is set at 1000000
        test_reference_number = create_application_reference()
        reference_number_without_prefix = test_reference_number[2:]
        self.assertEqual(reference_number_without_prefix, '1000001')

    def test_can_create_application_reference_number_with_delimiter_prefixed(self):
        test_reference_number = create_application_reference()
        self.assertIsNotNone(test_reference_number)
        self.assertTrue(re.match(r'(' + settings.APPLICATION_PREFIX + ')([0-9]{7})', test_reference_number))

    def test_application_reference_number_rolls(self):
        create_application_reference()
        current_reference = ApplicationReference.objects.all().first()
        self.assertEqual(current_reference.reference, 1000001)

        create_application_reference()
        current_reference = ApplicationReference.objects.all().first()
        self.assertEqual(current_reference.reference, 1000002)
