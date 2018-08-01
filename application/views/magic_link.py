"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- magic_link.py --

@author: Informed Solutions
"""

import os
import random
import string
import time
import logging
import traceback

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from application import login_redirect_helper
from application.middleware import CustomAuthenticationHandler
from application.forms import VerifyPhoneForm
from application.models import Application, UserDetails
from application.notify import send_email, send_text


log = logging.getLogger('django.server')


def magic_link_confirmation_email(email, link_id):
    """
    Method to send a magic link email, using notify.py, to allow applicant to log in
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """
    # If executing login function in test mode set env variable for later retrieval by test code
    if settings.EXECUTING_AS_TEST == 'True':
        os.environ['EMAIL_VALIDATION_URL'] = link_id
    else:
        print(link_id)

    personalisation = {"link": link_id}
    template_id = 'ecd2a788-257b-4bb9-8784-5aed82bcbb92'

    return send_email(email, personalisation, template_id)


def magic_link_resubmission_confirmation_email(email, application_reference, first_name, updated_tasks):
    """
    Method to send a magic link email, using notify.py, to allow applicant to log in
    """
    personalisation = {
        'ref': application_reference,
        'firstName': first_name,
    }

    all_tasks = [
        'Your sign in details',
        'Type of childcare',
        'Your personal details',
        'First aid training',
        'Criminal record (DBS) check',
        'Early years training',
        'Health declaration booklet',
        'People in your home',
        'References'
    ]

    for task in all_tasks:
        personalisation[task] = task in updated_tasks

    # Remove parentheses from 'Criminal record (DBS) check' - Notify cannot format such variables.
    personalisation['Criminal record DBS check'] = personalisation.pop('Criminal record (DBS) check')

    template_id = '6431f727-c49e-4f17-964e-b5595a83e958'

    send_email(email, personalisation, template_id)


def magic_link_update_email(email, first_name, link_id):
    """
    Method to send a magic link email, using notify.py, to update an applicant's email
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """
    # If executing login function in test mode set env variable for later retrieval by test code
    if settings.EXECUTING_AS_TEST == 'True':
        os.environ['EMAIL_VALIDATION_URL'] = link_id
    else:
        print(link_id)

    personalisation = {"link": link_id,
                       "first name": first_name}
    template_id = 'c778438a-c3fb-47e0-ad8a-936021abb1c8'

    return send_email(email, personalisation, template_id)


def magic_link_non_existent_email(email, link_id):
    """
    Method to send a magic link email, using notify.py, to allow applicant to log in
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """
    # If executing login function in test mode set env variable for later retrieval by test code
    if settings.EXECUTING_AS_TEST == 'True':
        os.environ['EMAIL_VALIDATION_URL'] = link_id
    else:
        print(link_id)

    personalisation = {"link": link_id}
    template_id = 'd2d7958a-269a-45c3-b66d-da8ec1911380'

    return send_email(email, personalisation, template_id)


def magic_link_text(phone, link_id):
    """
    Method to send a magic link sms using notify.py
    :param phone: string containing the phone number to send the code to
    :param link_id: string containing the magic link ID related to an application
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """

    personalisation = {"link": link_id}
    template_id = 'd285f17b-8534-4110-ba6c-e7e788eeafb2'

    return send_text(phone, personalisation, template_id)


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
        else:
            print(r)
    elif type == 'link':
        r = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(digits)])
    r = r.upper()

    return r


def has_expired(expiry):
    """
    Method to check whether a Magic Link URL or SMS code has expired
    :param expiry:
    :return:
    """
    # Expiry period is set in hours in settings.py
    exp_period = settings.EMAIL_EXPIRY * 60 * 60
    diff = int(time.time() - expiry)
    if diff <= exp_period:
        return False
    else:
        return True


def validate_magic_link(request, id):
    """
    Method to verify that the URL matches a magic link
    :param request: request to display a magic link page
    :param id: magic link ID
    :return: HttpResponse, directing to the correct page
    """
    try:
        acc = UserDetails.objects.get(magic_link_email=id)
        app_id = acc.application_id.pk
        exp = acc.email_expiry_date
        if not has_expired(exp) and len(id) > 0:
            acc.email_expiry_date = 0
            if 'email' in request.GET:
                acc.email = request.GET['email']
                acc.save()
                response = HttpResponseRedirect(reverse('Task-List-View') + '?id=' + str(app_id))
                CustomAuthenticationHandler.create_session(response, acc.email)
                return response
            if len(acc.mobile_number) == 0:
                acc.save()
                response = HttpResponseRedirect(reverse('Contact-Phone-View') + '?id=' + str(app_id))
                CustomAuthenticationHandler.create_session(response, acc.email)
                acc.email_expiry_date = 0
                acc.save()
                return response

            phone = acc.mobile_number
            rand_num = generate_random(5, 'code')
            expiry = int(time.time())
            acc.magic_link_sms = rand_num
            acc.sms_expiry_date = expiry
            acc.save()
            magic_link_text(phone, rand_num)
            return HttpResponseRedirect(settings.URL_PREFIX + '/security-code/?id=' + str(app_id))
        elif has_expired(exp) and acc.email_expiry_date != 0:
            return HttpResponseRedirect(settings.URL_PREFIX + '/link-expired/')
        else:
            return HttpResponseRedirect(settings.URL_PREFIX + '/link-used/')
    except Exception as ex:
        exception_data = traceback.format_exc().splitlines()
        exception_array = [exception_data[-3:]]
        log.error(exception_array)
        return HttpResponseRedirect(settings.URL_PREFIX + '/link-used/')


class SMSValidationView(View):
    def get(self, request):
        id = request.GET['id']
        application = Application.objects.get(pk=id)
        acc = UserDetails.objects.get(application_id=application)
        form = VerifyPhoneForm(id=id)

        # Max 3 resend attempts in 24 hours.
        if has_expired(acc.sms_resend_attempts_expiry_date):
            acc.sms_resend_attempts_expiry_date = 0

        if request.META.get('HTTP_REFERER') is not None:  # If they have come from email valdiation link, this is None.
            code_resent = True
        else:
            code_resent = False

        variables = {
            'form': form,
            'id': id,
            'phone_number': acc.mobile_number[-3:],
            'url': reverse('Security-Question') + '?id=' + str(application.application_id),
            'code_resent': code_resent,
            'sms_resend_attempts': acc.sms_resend_attempts,
        }
        return render(request, template_name='verify-phone.html', context=variables)

    def post(self, request):
        id = request.GET['id']
        application = Application.objects.get(pk=id)
        acc = UserDetails.objects.get(application_id=application)
        code = request.POST['magic_link_sms']
        form = VerifyPhoneForm(request.POST, id=id, correct_sms_code=acc.magic_link_sms)
        if len(code) > 0:
            exp = acc.sms_expiry_date

            if form.is_valid() and not has_expired(exp):
                response = login_redirect_helper.redirect_by_status(application)

                # Create session issue custom cookie to user
                CustomAuthenticationHandler.create_session(response, acc.email)

                acc.sms_resend_attempts = 0
                # Set SMS code to expired after a one time successful login
                acc.sms_expiry_date = int(time.time()) - ((settings.EMAIL_EXPIRY + 1) * 60 * 60)
                acc.save()

                # Forward back onto application
                return response

            else:

                # Ensure sign out and ask security question if SMS code has expired/already been used once
                response = HttpResponseRedirect(reverse('Security-Question') + '?id=' + id)

                CustomAuthenticationHandler.destroy_session(response)

                return response

        variables = {
            'form': form,
            'id': id,
            'phone_number': acc.mobile_number[-3:],
            'url': reverse('Security-Question') + '?id=' + str(application.application_id),
            'sms_resend_atempts': acc.sms_resend_attempts,
        }
        return render(request, template_name='verify-phone.html', context=variables)


class ResendSMSCodeView(View):
    def get(self, request):
        id = request.GET['id']
        acc = UserDetails.objects.get(application_id=id)

        if acc.sms_resend_attempts >= 3:
            return HttpResponseRedirect(reverse('Security-Question') + '?id=' + id)
        else:
            return render(request, 'resend-security-code.html', context={'id': id})

    def post(self, request):
        id = request.GET['id']
        acc = UserDetails.objects.get(application_id=id)
        mobile_number = acc.mobile_number
        acc.sms_expiry_date = int(time.time())
        new_sms_code = generate_random(5, 'code')
        acc.magic_link_sms = new_sms_code
        magic_link_text(mobile_number, new_sms_code)

        # Max 3 resend attempts in 24 hours.
        if acc.sms_resend_attempts == 0:
            acc.sms_resend_attempts_expiry_date = int(time.time())

        acc.sms_resend_attempts += 1
        acc.save()
        return HttpResponseRedirect(reverse('Security-Code') + '?id=' + id)

