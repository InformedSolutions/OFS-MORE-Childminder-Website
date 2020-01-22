"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- magic_link.py --

@author: Informed Solutions
"""

import os
import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve
from django.views import View
from django.core.exceptions import PermissionDenied

from application import login
from application.middleware import CustomAuthenticationHandler
from application.forms import VerifyPhoneForm
from application.notify import send_email, send_text


log = logging.getLogger('django.server')

r"""
2-factor auth: 

User is sent first validation code to entered email address. User can repeat
this process to generate a new email link.

    _O_  ---- GET sign-in page ---->
     |   <---------- page ----------
    / \  ---- POST email addr ----->   
                                      Expire email code
                                      Generate new email code 
                                      Send email          -----> [><]
         <-------- redirect --------  
         --- GET email sent page -->
         <--------- page -----------
          
User uses first code, via link, to be sent second code to their mobile. User
can repeat this process to generate new sms codes too, with the same email 
link, but are limited to three re-sends.

[><]_O_  ------ GET validate ------>
     |                                Validate email code
    / \                               Expire SMS code
                                      Generate new SMS code      (( * ))
                                      Send SMS            ----->   /-\
         <-------- redirect --------
         ---- GET sms sent page --->
         <-- page with email code --
         
User enters second code into form and submits to log in. The form posts both
codes which are both validated.
 
( * )       
  []_O_  ----- POST sms code ------>   
     |        with email code         Validate email code again
    / \                               Validate SMS code
                                      Expire email code
                                      Expire SMS code
                                      Create session cookie (log user in)
         <------- redirect ---------
         --- GET e.g. task list --->
                                      Validate session cookie
         <--------- page -----------

"""


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
        'Your children',
        'First aid training',
        'Criminal record (DBS) check',
        'Early years training',
        'Health declaration booklet',
        'People in your home',
        'References',
    ]

    for task in all_tasks:
        personalisation[task] = task in updated_tasks

    # Remove parentheses from 'Criminal record (DBS) check' - Notify cannot format such variables.
    personalisation['Criminal record DBS check'] = personalisation.pop('Criminal record (DBS) check')

    template_id = '3f8b41d2-62b5-42ea-a64d-61ad661fcc15'

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


def validate_magic_link(request, code):
    """
    Method to verify that the URL matches a magic link
    :param request: request to display a magic link page
    :param code: magic link code
    :return: HttpResponse, directing to the correct page
    """
    magic_email_link_code = code

    try:
        user_details = login.magic_link_validation(magic_email_link_code)
    except PermissionDenied as e:
        return login.invalid_email_link_redirect(e)
    if user_details.email != user_details.change_email and user_details.change_email is not None:
        user_details.email = user_details.change_email
        user_details.save()
    # First sign-in (no mobile yet, sms check not required)
    if len(user_details.mobile_number) == 0:
        # Successful login.
        response = HttpResponseRedirect(reverse('Contact-Phone-View') + '?id=' + str(user_details.application_id.pk))
        login.log_user_in(user_details, response)
        return response

    # Subsequent sign-in (sms check required)
    else:
        # don't expire magic link yet - allow it to be used to re-send sms.
        # Increment the resend counter each time this link is used
        if not login.refresh_and_check_sms_resends(user_details):
            return login.invalid_sms_code_redirect(magic_email_link_code)

        # create and send sms code
        login.create_and_send_sms_code(user_details)

        # pass email validation code to form page so it can be re-validated as well as sms code.
        return HttpResponseRedirect(settings.URL_PREFIX + '/security-code/?validation=' + magic_email_link_code)


class SMSValidationView(View):

    def get(self, request):

        magic_link_email = request.GET['validation']
        try:
            user_details = login.magic_link_validation(magic_link_email)
        except PermissionDenied as e:
            return login.invalid_email_link_redirect(e)

        form = VerifyPhoneForm(correct_sms_code='')

        return self._render_page(request, user_details, form)

    def post(self, request):

        magic_link_email = request.POST['validation']
        try:
            user_details = login.magic_link_validation(magic_link_email)
        except PermissionDenied as e:
            return login.invalid_email_link_redirect(e)

        form = VerifyPhoneForm(request.POST, correct_sms_code=user_details.magic_link_sms)

        if form.is_valid():

            try:
                login.sms_code_validation(user_details, form.cleaned_data['magic_link_sms'])
            except PermissionDenied:
                # Ensure sign out and ask security question if SMS code has expired/already been used once
                response = login.invalid_sms_code_redirect(magic_link_email)
                CustomAuthenticationHandler.destroy_session(response)
                return response


            # Successful login
            application = user_details.application_id
            response = login.redirect_by_status(application)
            login.log_user_in(user_details, response)
            return response

        return self._render_page(request, user_details, form)

    def _render_page(self, request, user_details, form):

        # Don't care if user is out of re-sends here - we just display a different message on the page
        login.refresh_and_check_sms_resends(user_details)

        # If they have come from email validation link, this is None.
        code_resent = request.META.get('HTTP_REFERER') is not None

        variables = {
            'form': form,
            'magic_link_email': user_details.magic_link_email,
            'phone_number_end': user_details.mobile_number[-3:],
            'code_resent': code_resent,
            'sms_resend_attempts': user_details.sms_resend_attempts,
        }
        return render(request, template_name='verify-phone.html', context=variables)


class ResendSMSCodeView(View):

    def get(self, request):

        magic_link_email = request.GET['validation']
        try:
            user_details = login.magic_link_validation(magic_link_email)
        except PermissionDenied as e:
            return login.invalid_email_link_redirect(e)

        if not login.refresh_and_check_sms_resends(user_details):
            return login.invalid_sms_code_redirect(magic_link_email)

        return render(request, 'resend-security-code.html', context={'magic_link_email': magic_link_email})

    def post(self, request):

        magic_link_email = request.POST['validation']
        try:
            user_details = login.magic_link_validation(magic_link_email)
        except PermissionDenied as e:
            return login.invalid_email_link_redirect(e)

        if not login.refresh_and_check_sms_resends(user_details):
            return login.invalid_sms_code_redirect(magic_link_email)

        login.create_and_send_sms_code(user_details)

        return HttpResponseRedirect(reverse('Security-Code') + '?validation=' + magic_link_email)


