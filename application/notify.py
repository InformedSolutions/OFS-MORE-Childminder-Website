"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- notify.py --

@author: Informed Solutions

Handler for dispatching email notifications via the GOV.UK notify gateway api.
"""

import json

import requests
from django.conf import settings


def send_email(email, personalisation, template_id):
    """
    Method to send an email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param personalisation: object containing the personalisation related to an application
    :param template_id: string containing the templateId of the notification request
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """

    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}

    # If executing function in test mode override email address
    if settings.EXECUTING_AS_TEST == 'True':
        email = 'simulate-delivered@notifications.service.gov.uk'

    notification_request = {
        'email': email,
        'personalisation': personalisation,
        'templateId': template_id
    }
    r = requests.post(base_request_url + '/api/v1/notifications/email/',
                      json.dumps(notification_request),
                      headers=header)

    return r


def send_text(phone, personalisation, template_id):
    """
    Method to send an SMS verification code using the Notify Gateway API
    :param phone: string containing the phone number to send the code to
    :param personalisation: object containing the personalisation related to an application
    :param template_id: string containing the templateId of the notification request
    :return: :class:`Response <Response>` object containing http request response
    :rtype: requests.Response
    """
    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}

    # If executing function in test mode override phone number
    if settings.EXECUTING_AS_TEST == 'True':
        phone = '07700900111'

    notification_request = {
        'phoneNumber': phone,
        'personalisation': personalisation,
        'templateId': template_id
    }
    r = requests.post(base_request_url + '/api/v1/notifications/sms/', json.dumps(notification_request),
                      headers=header)
    return r
