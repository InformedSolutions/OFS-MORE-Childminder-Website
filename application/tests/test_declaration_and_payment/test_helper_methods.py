"""
Tests for assuring the application reference number generation process
"""
import re
import time

from django.conf import settings
from django.test import TestCase, tag

from application import models
from application.application_reference_generator import create_application_reference
from application.payment_service import created_formatted_payment_reference
from application.views import payment as payment_views, NO_ADDITIONAL_CERTIFICATE_INFORMATION
from application.tests import utils


@tag('unit')
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
        current_reference = models.ApplicationReference.objects.all().first()
        self.assertEqual(current_reference.reference, 1000001)

        create_application_reference()
        current_reference = models.ApplicationReference.objects.all().first()
        self.assertEqual(current_reference.reference, 1000002)


@tag('unit')
class PaymentReferenceTests(TestCase):

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


def bool_to_info(boolean):
    return NO_ADDITIONAL_CERTIFICATE_INFORMATION[0] if not boolean else 'Some Information'


@tag('unit')
class PaymentEmailGetTemplateTests(TestCase):

    def setUp(self):

        # create test application
        self.app_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        self.application = models.Application.objects.create(
            application_id=self.app_id,
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            application_reference='REF123',
        )

        models.UserDetails.objects.create(
            application_id=self.application,
            email="test@informed.com"
        )

        self.pd = models.ApplicantPersonalDetails.objects.create(
            application_id=self.application,
        )

        models.ApplicantName.objects.create(
            application_id=self.application,
            personal_detail_id=self.pd,
            current_name=True,
            first_name="Test",
            last_name="Test"
        )

        self.crc = models.CriminalRecordCheck.objects.create(
            application_id=self.application,
            dbs_certificate_number='001630091191',
            lived_abroad=False,
            capita=True,
            certificate_information=bool_to_info(True),
        )

        # patch send_email for each test
        self.send_email_mock = utils.patch_object_for_setUp(self, payment_views, 'send_email')

    def test_email_template_HDB_DBS_only(self):

        self.crc.lived_abroad = False
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(True)
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 35

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '35', 'ref': 'REF123'},
                                                '02c01f75-1f9d-428f-a862-4effac03ebd3')

    def test_email_template_HDB_DBS_and_lived_abroad(self):

        self.crc.lived_abroad = True
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(True)
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 35

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '35', 'ref': 'REF123'},
                                                'c82b8ffd-f67c-4019-a724-d57ab559f08e')

    def test_email_template_HDB_update_service_DBS_only(self):

        self.crc.lived_abroad = False
        self.crc.capita = False
        self.crc.enhanced_check = True
        self.crc.on_update = True
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 35

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '35', 'ref': 'REF123'},
                                                '02c01f75-1f9d-428f-a862-4effac03ebd3')

    def test_email_template_HDB_update_service_DBS_and_lived_abroad(self):

        self.crc.lived_abroad = True
        self.crc.capita = False
        self.crc.enhanced_check = True
        self.crc.on_update = True
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 35

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '35', 'ref': 'REF123'},
                                                'c82b8ffd-f67c-4019-a724-d57ab559f08e')

    def test_email_template_DBS_only(self):

        self.crc.lived_abroad = False
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(True)
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 103

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '103', 'ref': 'REF123'},
                                                '294f2710-c507-4d30-ae64-b5451c59a45c')

    def test_email_template_DBS_and_lived_abroad(self):

        self.crc.lived_abroad = True
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(True)
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 103

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '103', 'ref': 'REF123'},
                                                '94190a2d-d1c7-46c6-8144-da38141aa027')

    def test_email_template_update_service_DBS_only(self):

        self.crc.lived_abroad = False
        self.crc.capita = False
        self.crc.enhanced_check = True
        self.crc.on_update = True
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 103

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '103', 'ref': 'REF123'},
                                                '294f2710-c507-4d30-ae64-b5451c59a45c')

    def test_email_template_update_service_DBS_and_lived_abroad(self):

        self.crc.lived_abroad = True
        self.crc.capita = False
        self.crc.enhanced_check = True
        self.crc.on_update = True
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 103

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '103', 'ref': 'REF123'},
                                                '94190a2d-d1c7-46c6-8144-da38141aa027')

    def test_email_template_HDB_only(self):

        self.crc.lived_abroad = False
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(False)
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 99

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '99', 'ref': 'REF123'},
                                                '8ca4eb7c-f4c9-417a-85e6-f4c10672f41a')

    def test_email_template_No_Docs(self):

        self.crc.lived_abroad = False
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(False)
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 42

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '42', 'ref': 'REF123'},
                                                '75325ea2-c9b4-408c-9d89-c16ebbd7bd32')

    def test_email_template_HDB_lived_abroad_only(self):

        self.crc.lived_abroad = True
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(False)
        self.crc.save()
        childcare_reg = 'EYR-CR-both'
        cost = 1337

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '1337', 'ref': 'REF123'},
                                                '36720ba3-165e-40cd-a6d2-320daa9d6e4a')

    def test_email_template_lived_abroad_only(self):

        self.crc.lived_abroad = True
        self.crc.capita = True
        self.crc.certificate_information = bool_to_info(False)
        self.crc.save()
        childcare_reg = 'CR-both'
        cost = 102

        payment_views.get_template(self.crc, self.app_id, self.application, cost, childcare_reg)

        self.send_email_mock.assert_called_with('test@informed.com',
                                                {'firstName': 'Test', 'cost': '102', 'ref': 'REF123'},
                                                'f5a2998c-7322-4e32-8a85-72741bfec4a5')

