"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- magic_link.py --

@author: Informed Solutions
"""

import json
import random
import requests
import string
import time
import logging
import traceback

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from . import login_redirect_helper
from .middleware import CustomAuthenticationHandler
from .forms import EmailLoginForm, VerifyPhoneForm
from .models import Application, UserDetails

log = logging.getLogger('django.server')


def existing_application(request):
    """
    Method returning the template for the Existing application page and navigating to the email sent page when
    successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Existing application template
    """
    form = EmailLoginForm()
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        email = request.POST['email_address']
        if form.is_valid():
            try:
                acc = UserDetails.objects.get(email=email)
            except Exception as ex:
                exception_data = traceback.format_exc().splitlines()
                exception_array = [exception_data[-3:]]
                log.error(exception_array)
                return HttpResponseRedirect(settings.URL_PREFIX + '/email-sent')
            # Send time-boxed e-mail link to log back in
            domain = request.META.get('HTTP_REFERER', '')
            domain = domain[:-21]
            link = generate_random(12, 'link')
            expiry = int(time.time())
            acc.email_expiry_date = expiry
            acc.magic_link_email = link
            acc.save()
            magic_link_email(email, domain + 'validate/' + link)
            # The same response is returned whether the e-mail is valid or not
            return HttpResponseRedirect(settings.URL_PREFIX + '/email-sent')
    return render(request, 'existing-application.html', {'form': form})


def magic_link_email(email, link_id):
    """
    Method to send a magic link email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: an email
    """
    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}
    notification_request = {
        'email': email,
        'personalisation': {
            'link': link_id
        },
        'reference': 'string',
        'templateId': 'ecd2a788-257b-4bb9-8784-5aed82bcbb92'
    }
    r = requests.post(base_request_url + '/api/v1/notifications/email/',
                      json.dumps(notification_request),
                      headers=header)
    print(link_id)
    return r


def magic_link_text(phone, link_id):
    """
    Method to send an SMS verification code using the Notify Gateway API
    :param phone: string containing the phone number to send the code to
    :param link_id: string containing the magic link ID related to an application
    :return: an SMS
    """
    print('Sending SMS Message: ' + link_id)
    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}
    notification_request = {
        'personalisation': {
            'link': link_id
        },
        'phoneNumber': phone,
        'reference': 'string',
        'templateId': 'd285f17b-8534-4110-ba6c-e7e788eeafb2'
    }
    r = requests.post(base_request_url + '/api/v1/notifications/sms/', json.dumps(notification_request),
                      headers=header)
    print(r.status_code)
    return r


def generate_random(digits, type):
    """
    Method to generate a random code or random string of varying size for the SMS code or Magic Link URL
    :param digits: integer indicating the desired length
    :param type: flag to indicate the SMS code or Magic Link URL
    :return:
    """
    if type == 'code':
        r = ''.join([random.choice(string.digits) for n in range(digits)])
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
    if diff < exp_period or diff == exp_period:
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
        exp = acc.email_expiry_date
        if not has_expired(exp) and len(id) > 0:
            acc.email_expiry_date = 0
            phone = acc.mobile_number
            g = generate_random(5, 'code')
            expiry = int(time.time())
            acc.magic_link_sms = g
            acc.sms_expiry_date = expiry
            acc.save()
            magic_link_text(phone, g)
            return HttpResponseRedirect(settings.URL_PREFIX + '/verify-phone/?id=' + id)
        else:
            return HttpResponseRedirect(settings.URL_PREFIX + '/code-expired/')
    except Exception as ex:
        exception_data = traceback.format_exc().splitlines()
        exception_array = [exception_data[-3:]]
        log.error(exception_array)
        return HttpResponseRedirect(settings.URL_PREFIX + '/bad-link/')


def sms_verification(request):
    """
    Method to display the SMS code verification page
    :param request: request to display the SMS verification page
    :return: HttpResponse displaying the SMS verification page
    """
    id = request.GET['id']
    acc = UserDetails.objects.get(magic_link_email=id)
    if 'f' in request.GET.keys():
        phone = acc.mobile_number
        g = generate_random(5, 'code')
        expiry = int(time.time())
        acc.magic_link_sms = g
        acc.sms_expiry_date = expiry
        acc.save()
        magic_link_text(phone, g).status_code
        return HttpResponseRedirect(settings.URL_PREFIX + '/verify-phone/?id=' + id)
    form = VerifyPhoneForm(id=id)
    app = acc.application_id
    application = Application.objects.get(application_id=app.pk)
    if request.method == 'POST':
        form = VerifyPhoneForm(request.POST, id=id)
        code = request.POST['magic_link_sms']
        if len(code) > 0:
            exp = acc.sms_expiry_date
            if form.is_valid() and not has_expired(exp):
                if code == acc.magic_link_sms:
                    response = login_redirect_helper.redirect_by_status(app)

                    # Create session issue custom cookie to user
                    CustomAuthenticationHandler.create_session(response, acc.email)

                    # Forward back onto application
                    return response
                else:
                    print(4)
                    return HttpResponseRedirect(settings.URL_PREFIX + '/verify-phone/?id=' + id)
    return render(request, 'verify-phone.html', {'form': form, 'id': id,
                                                 'url': settings.URL_PREFIX + '/security-question?id=' + str(
                                                     application.application_id)})
