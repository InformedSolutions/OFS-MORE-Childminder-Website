import os
import random
import string
import time

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from application.middleware import CustomAuthenticationHandler
from application.models import UserDetails


def redirect_by_status(application):
    """
    Helper method to calculate a redirect that a user should be issued after logging in
    based on an application's current status
    :param application: the application to be logged into
    :return: an HttpResponseRedirect to a landing page based on an application's current status
    """
    # If application is still being drafted, return user to task list
    if application.application_status == 'DRAFTING':
        if application.childcare_type_status == 'COMPLETED':
            response = HttpResponseRedirect(
                reverse('Task-List-View') + '?id=' + str(application.application_id)
            )
        else:
            response = HttpResponseRedirect(
                reverse('Type-Of-Childcare-Guidance-View') + '?id=' + str(application.application_id))

    # If application is submitted but awaiting ARC review, or in the process of being reviewed,
    # redirect the user to an information page informing them that no action is required of them
    if application.application_status == 'ARC_REVIEW' or application.application_status == 'SUBMITTED':
        response = HttpResponseRedirect(
            reverse('Awaiting-Review-View') + '?id=' + str(application.application_id)
        )

    # If application status indicates user must supply further information or correct a submission,
    # redirect them to the task list
    if application.application_status == 'FURTHER_INFORMATION':
        response = HttpResponseRedirect(
            reverse('Task-List-View') + '?id=' + str(application.application_id)
        )

    # If accepted move to SUBMITTED send to confirmation view saying Ofsted are performing background
    # checks
    if application.application_status == 'ACCEPTED':
        response = HttpResponseRedirect(
            reverse('Accepted-View') + '?id=' + str(application.application_id)
        )

    return response


def generate_random(digits, type):
    """
    Method to generate a random code or random string of varying size for the SMS code or Magic Link URL
    :param digits: integer indicating the desired length
    :param type: flag to indicate the SMS code or Magic Link URL
    :return:
    """
    if type == 'code':
        r = ''.join([random.choice(string.digits[1:]) for n in range(digits)])
        if settings.EXECUTING_AS_TEST == 'True':
            os.environ['SMS_VALIDATION_CODE'] = r
            print(r)
    elif type == 'link':
        r = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(digits)])
    r = r.upper()

    return r


class MagicLinkUsedException(PermissionDenied):
    pass


class MagicLinkExpiredException(PermissionDenied):
    pass


class MagicLinkInvalidException(PermissionDenied):
    pass


class SMSCodeUsedException(PermissionDenied):
    pass


class SMSCodeExpiredException(PermissionDenied):
    pass


class SMSCodeInvalidException(PermissionDenied):
    pass


def magic_link_validation(link_code):
    """Returns the UserDetails model associated with this magic link code, if valid"""

    if not link_code:
        raise MagicLinkInvalidException()

    try:
        user_details = UserDetails.objects.get(magic_link_email=link_code)
    except UserDetails.DoesNotExist as e:
        raise MagicLinkInvalidException() from e

    if user_details.email_expiry_date == 0:
        raise MagicLinkUsedException()

    if _has_expired(user_details.email_expiry_date):
        raise MagicLinkExpiredException()

    return user_details


def sms_code_validation(user_details, sms_code):
    """Compares the given sms code with that stored in the given UserDetails model"""

    if not user_details.magic_link_sms or sms_code != user_details.magic_link_sms:
        raise SMSCodeInvalidException()

    if user_details.sms_expiry_date == 0:
        raise SMSCodeUsedException()

    if _has_expired(user_details.sms_expiry_date):
        raise SMSCodeExpiredException()

    return user_details


def refresh_and_check_sms_resends(user_details):
    """User can re-send sms code a limited number of times in a certain period of time.
    Reset the counter if sufficient time has elapsed, or return False if they are out
    of re-sends"""
    if _has_expired(user_details.sms_resend_attempts_expiry_date, 24 * 60 * 60):
        user_details.sms_resend_attempts_expiry_date = int(time.time())
        user_details.sms_resend_attempts = 0
        user_details.save()
    # 4, because initial send is included plus 3 re-sends
    return user_details.sms_resend_attempts < 4


def invalid_email_link_redirect(exception):
    if isinstance(exception, MagicLinkExpiredException):
        path = '/link-expired/'
    else:
        path = '/link-used/'
    return HttpResponseRedirect(settings.URL_PREFIX + path)


def invalid_sms_code_redirect(magic_link_email):
    """Note, the parameter is the EMAIL validation code rather than the SMS one, to be passed
    through to the target page"""
    return HttpResponseRedirect(reverse('Security-Question') + '?validation=' + magic_link_email)


def create_and_send_sms_code(user_details):
    from application.views.magic_link import magic_link_text
    sms_code = generate_random(5, 'code')
    user_details.sms_resend_attempts += 1
    user_details.magic_link_sms = sms_code
    user_details.sms_expiry_date = int(time.time())
    user_details.save()
    magic_link_text(user_details.mobile_number, sms_code)


def log_user_in(user_details, response):
    # expire codes
    user_details.email_expiry_date = 0
    user_details.sms_expiry_date = 0
    user_details.sms_resend_attempts = 0
    user_details.save()
    # log user in
    CustomAuthenticationHandler.create_session(response, user_details.email)
    # Update last accessed time and reset expiry email flag
    application = user_details.application_id
    application.date_last_accessed = timezone.now()
    application.application_expiry_email_sent = False
    application.save()


def _has_expired(creation_time, exp_period_seconds=None):
    """
    Method to check whether a Magic Link URL or SMS code has expired
    :param creation_time: Time to check for expiry
    :param exp_period_seconds: Number of seconds after which the creation_time will have expired
    :return: True if expired, otherwise False
    """
    if exp_period_seconds is None:
        # Expiry period is set in hours in settings.py
        exp_period_seconds = settings.EMAIL_EXPIRY * 60 * 60
    diff = int(time.time() - creation_time)
    return diff > exp_period_seconds
