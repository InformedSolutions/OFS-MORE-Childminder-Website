"""
Functional tests for views

NOTE! If it throws you status 200, that means form submission is failing!

"""
import datetime
import uuid

from uuid import uuid4

from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.urls import resolve

from timeline_logger.models import TimelineLog
from .base import ApplicationTestBase

from ...models import (AdultInHome,
                       ApplicantHomeAddress,
                       ApplicantName,
                       ApplicantPersonalDetails,
                       Application,
                       ChildcareType,
                       ChildInHome,
                       CriminalRecordCheck,
                       ChildcareTraining,
                       Reference,
                       UserDetails)

from ...views import magic_link, security_question


class CreateTestNewApplicationSubmit(TestCase, ApplicationTestBase):
    """
    Functional test for submitting whole application.
    """

    def setUp(self):
        self.TestNewApplicationSubmit()
        super().setUp()

    def TestEmailValidationDoesNotCountAsResend(self):
        self.test_update_email()
        self.test_validate_email()

        self.assertEqual(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts)
        self.assertEqual(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts_expiry_date)

    def TestResendCodeIncrementsCount(self):
        r = self.client.post(reverse('Resend-Code') + '?id=' + str(self.app_id))

        self.assertEqual(1, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts)
        self.assertNotEqual(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts_expiry_date)

    def TestResendCodeRedirectsToSMSPage(self):
        r = self.client.post(reverse('Resend-Code') + '?id=' + str(self.app_id))
        found = resolve(r.url)

        self.assertEqual(r.status_code, 302)
        self.assertEqual(found.func.view_class, magic_link.SMSValidationView.as_view().view_class)

    def TestFourthSMSResendRedirectsToSecurityQuestion(self):
        UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts = 0

        for n in range(3):
            r = self.client.post(reverse('Resend-Code') + '?id=' + str(self.app_id))

        r = self.client.get(reverse('Resend-Code') + '?id=' + str(self.app_id))
        found = resolve(r.url.split('?')[0])

        self.assertEqual(r.status_code, 302)
        self.assertEqual(found.func, security_question.question)

    def TestSMSLoginResetsSMSResendNumber(self):
        acc = UserDetails.objects.get(application_id=self.app_id)
        acc.sms_resend_attempts = 10  # Some non-zero value.
        correct_sms_code = acc.magic_link_sms
        acc.save()

        r = self.client.post(reverse('Security-Code') + '?id=' + str(self.app_id),
                             {'id': self.app_id, 'magic_link_sms': correct_sms_code})

        self.assertIs(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts)

    def TestSecurityQuestionLoginResetsSMSResendNumber(self):
        acc = UserDetails.objects.get(application_id=self.app_id)
        acc.sms_resend_attempts = 10  # Some non-zero value.
        acc.save()
        # security_answer = CriminalRecordCheck.objects.get(application_id=self.app_id).dbs_certificate_number
        security_answer = acc.mobile_number
        r = self.client.post(reverse('Security-Question') + '?id=' + str(self.app_id),
                             {'id': self.app_id, 'security_answer': security_answer})

        self.assertIs(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts)

    def TestSecurityQuestionLoginResetsSMSResendNumber(self):
        acc = UserDetails.objects.get(application_id=self.app_id)
        acc.sms_resend_attempts = 10  # Some non-zero value.
        acc.save()
        # security_answer = CriminalRecordCheck.objects.get(application_id=self.app_id).dbs_certificate_number
        security_answer = acc.mobile_number
        r = self.client.post(reverse('Security-Question') + '?id=' + str(self.app_id),
                             {'id': self.app_id, 'security_answer': security_answer})

        self.assertIs(0, UserDetails.objects.get(application_id=self.app_id).sms_resend_attempts)

    def TestAppPaymentConfirmationWithNoHealthBookletNoConviction(self):
        # """Send Payment Confirmation"""
        # application = Application.objects.get(application_id=self.app_id)
        # application.health_status = 'NOT_STARTED'
        # application.save()
        #
        # criminal_record_check = CriminalRecordCheck.objects.get(application_id=self.app_id)
        # criminal_record_check.cautions_convictions = False
        # criminal_record_check.save()
        #
        # r = self.client.get(
        #     reverse('Payment-Confirmation'),
        #     {
        #         'id': self.app_id,
        #         'orderCode': Application.objects.get(application_id=self.app_id).application_reference,
        #     }
        # )
        # self.assertEqual(r.status_code, 200)
        # self.assertNotContains(r, '<p>We need your health declaration booklet.</p>')
        # self.assertNotContains(r, '<li>DBS certificate</li>')
        pass

    def TestAppPaymentConfirmationWithHealthBookletNoConviction(self):
        # """Send Payment Confirmation"""
        # application = Application.objects.get(application_id=self.app_id)
        # application.health_status = 'COMPLETED'
        # application.save()
        #
        # criminal_record_check = CriminalRecordCheck.objects.get(application_id=self.app_id)
        # criminal_record_check.cautions_convictions = False
        # criminal_record_check.save()
        #
        # r = self.client.get(
        #     reverse('Payment-Confirmation'),
        #     {
        #         'id': self.app_id,
        #         'orderCode': Application.objects.get(application_id=self.app_id).application_reference,
        #     }
        # )
        # self.assertEqual(r.status_code, 200)
        # self.assertContains(r, '<p>We need your health declaration booklet.</p>')
        # self.assertNotContains(r, '<li>DBS certificate</li>')
        pass

    def TestAppPaymentConfirmationWithHealthBookletAndConviction(self):
        # """Send Payment Confirmation"""
        # application = Application.objects.get(application_id=self.app_id)
        # application.health_status = 'COMPLETED'
        # application.save()
        #
        # criminal_record_check = CriminalRecordCheck.objects.get(application_id=self.app_id)
        # criminal_record_check.cautions_convictions = True
        # criminal_record_check.save()
        #
        # r = self.client.get(
        #     reverse('Payment-Confirmation'),
        #     {
        #         'id': self.app_id,
        #         'orderCode': Application.objects.get(application_id=self.app_id).application_reference,
        #     }
        # )
        # self.assertEqual(r.status_code, 200)
        # self.assertContains(r, '<li>health declaration booklet</li>')
        # self.assertContains(r, '<li>DBS certificate.</li>')
        pass

    def TestNewApplicationSubmit(self):
        """Submit whole application"""

        with mock.patch('application.notify.send_email') as notify_mock, \
                mock.patch('application.utils.test_notify_connection') as notify_connection_test_mock:
            notify_connection_test_mock.return_value.status_code = 201
            notify_mock.return_value.status_code = 201

            self.test_app_init()

            self.test_app_email()
            self.test_validate_email()
            self.test_app_phone()
            self.test_return_to_application()

            self.TestEmailValidationDoesNotCountAsResend()
            self.TestResendCodeIncrementsCount()
            self.TestResendCodeRedirectsToSMSPage()
            self.TestFourthSMSResendRedirectsToSecurityQuestion()
            self.TestSMSLoginResetsSMSResendNumber()
            self.TestSecurityQuestionLoginResetsSMSResendNumber()

            self.test_contact_summary_view()
            self.test_type_of_childcare_age_groups()
            self.test_type_of_childcare_overnight_care()
            self.test_security_question()
            self.test_type_of_childcare_register()

            self.test_personal_details_names()
            self.test_personal_details_dob()
            self.test_personal_details_home_address()
            self.test_personal_details_home_address_details()
            # self.TestAppPersonalDetailsSummaryView()

            self.test_verify_phone()
            self.test_verify_phone_email_apostrophe()

            self.test_first_aid_details()
            self.test_first_aid_certificate()
            self.test_health_declaration_booklet()

            self.test_criminal_record_check_details()

            self.test_other_people_adults()
            self.test_other_people_children()
            self.test_other_people_summary()

            self.test_other_people_adult_details()
            self.test_other_people_children_details()

            self.test_first_reference_name()
            self.test_first_reference_address()
            self.test_first_reference_contact_details()
            self.test_second_reference_name()
            self.test_second_reference_address()
            self.test_second_reference_contact_details()
            self.test_references_summary()

            self.test_declaration()
            self.test_arc_flagged_statuses()
            self.test_payment_credit_credentials()
            self.test_payment_confirmation()
            self.TestAppPaymentConfirmationWithHealthBookletNoConviction()
            self.TestAppPaymentConfirmationWithHealthBookletAndConviction()
            self.TestAppPaymentConfirmationWithNoHealthBookletNoConviction()

    def test_application_submit(self):
        """
        Test if application been submitted
        """
        self.assertTrue(Application.objects.filter(application_id=self.app_id).exists())
        self.assertEqual(Application.objects.get(application_id=self.app_id).application_status, "SUBMITTED")

    def test_new_application_submit_log(self):
        """
        Check logging trigger right after application was drafted/started
        """

        self.test_app_init()
        self.assertEqual(
            TimelineLog.objects.filter(object_id=self.app_id)[0].extra_data['action'], "created by"
        )

    def test_submitted_application_log(self):
        """
        Check if logging triggered right after application got submitted status
        """
        self.assertTrue(
            TimelineLog.objects.filter(object_id=self.app_id, extra_data__contains={"action": "submitted by"})
        )

    def test_updated_field_log(self):
        """
        After application been returned, we start to log all field changes with the
        help of signals.
        """

        # Set application_status to FURTHER_INFORMATION programatically,
        # as functionally this can be only done from ARC.
        self._set_application_status("FURTHER_INFORMATION")

        # Update the field

        data = {
            'id': self.app_id,
            'first_name': "Sherlock",
            'middle_names': "Scott",
            'last_name': "Holmes"
        }

        self.test_personal_details_names(data)

        # Check if logs appareade
        self.assertTrue(
            TimelineLog.objects.filter(
                object_id=self.app_id,
                extra_data__contains={
                    "application_status": "FURTHER_INFORMATION"
                })
        )

    def _set_application_status(self, status):
        """Helper to set status in Application model

        Arguments:
            status {string} -- Desired application status
        """

        app = Application.objects.get(pk=self.app_id)
        app.application_status = status
        app.save()

    def test_cancel_application(self):
        r = self.client.get(reverse('Cancel-Application'),
                            {
                                'id': self.app_id
                            })
        self.assertTrue(Application.objects.filter(pk=self.app_id).exists())

        r = self.client.get(reverse('Cancel-Application-Confirmation'))
        self.assertEqual(r.status_code, 200)

    def test_delete_application(self):
        data = {
            'id': self.app_id,
        }
        self.assertTrue(Application.objects.filter(pk=self.app_id).exists())
        r = self.client.post(reverse('Cancel-Application'), data)
        self.assertFalse(Application.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(UserDetails.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ApplicantHomeAddress.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ApplicantName.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ApplicantPersonalDetails.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ChildcareType.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(Reference.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(AdultInHome.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ChildInHome.objects.filter(application_id=self.app_id).exists())
        # self.assertFalse(CriminalRecordCheck.objects.filter(application_id=self.app_id).exists())
        self.assertFalse(ChildcareTraining.objects.filter(application_id=self.app_id).exists())
