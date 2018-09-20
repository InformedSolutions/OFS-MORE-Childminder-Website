"""
Functional tests for views

NOTE! If it throws you status 200, that means form submission is failing!

"""
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
        self.TestUpdateEmail()
        self.TestValidateEmail()

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

            self.TestAppInit()

            self.TestAppEmail()
            self.TestValidateEmail()
            self.TestAppPhone()
            self.TestReturnToApp()

            self.TestEmailValidationDoesNotCountAsResend()
            self.TestResendCodeIncrementsCount()
            self.TestResendCodeRedirectsToSMSPage()
            self.TestFourthSMSResendRedirectsToSecurityQuestion()
            self.TestSMSLoginResetsSMSResendNumber()
            self.TestSecurityQuestionLoginResetsSMSResendNumber()

            self.TestContactSummaryView()
            self.TestTypeOfChildcareAgeGroups()
            self.TestTypeOfChildcareOvernightCare()
            self.TestSecurityQuestion()
            self.AppTestTypeOfChildcareRegister()

            self.TestAppPersonalDetailsNames()
            self.TestAppPersonalDetailsDOB()
            self.TestAppPersonalDetailsHomeAddress()
            self.TestAppPersonalDetailsHomeAddressDetails()
            # self.TestAppPersonalDetailsSummaryView()

            self.TestVerifyPhone()
            self.TestVerifyPhoneEmailApostrophe()

            self.TestAppFirstAid()
            self.TestAppFirstAidCert()
            self.TestAppHealthBooklet()

            self.TestAppCriminalRecordCheckDetails()

            self.TestAppOtherPeopleAdults()
            self.TestAppOtherPeopleChildren()
            self.TestAppOtherPeopleSummary()

            self.TestAppOtherPeopleAdultsDetails()
            self.TestAppOtherPeopleChildrenDetails()

            self.TestAppFirstReferenceName()
            self.TestAppFirstReferenceAddress()
            self.TestAppFirstReferenceContactDetails()
            self.TestAppSecondReferenceName()
            self.TestAppSecondReferenceAddress()
            self.TestAppSecondReferenceContactDetails()
            self.TestReferencesSummary()

            self.TestAppDeclaration()
            self.TestAppArcFlaggedStatuses()
            self.TestAppPaymentCreditDetails()
            self.TestAppPaymentConfirmation()
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

        self.TestAppInit()
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

        self.TestAppPersonalDetailsNames(data)

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
