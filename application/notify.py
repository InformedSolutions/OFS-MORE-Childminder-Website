"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- notify.py --

@author: Informed Solutions

Handler for dispatching email notifications via the GOV.UK notify gateway api.
"""

import json

import requests
import os
from django.conf import settings


def send_email(email, link_id):
    """
    Method to send a magic link email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: an email
    """

    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}

    # If executing login function in test mode set env variable for later retrieval by test code and override email address
    if settings.EXECUTING_AS_TEST == 'True':
        os.environ['EMAIL_VALIDATION_URL'] = link_id
        email = 'simulate-delivered@notifications.service.gov.uk'
    else:
        print(link_id)

    notification_request = {
        'email': email,
        'personalisation': {
            'link': link_id
        },
        'templateId': 'ecd2a788-257b-4bb9-8784-5aed82bcbb92'
    }
    r = requests.post(base_request_url + '/api/v1/notifications/email/',
                      json.dumps(notification_request),
                      headers=header)

    return r


def send_text(phone, link_id):
    """
    Method to send an SMS verification code using the Notify Gateway API
    :param phone: string containing the phone number to send the code to
    :param link_id: string containing the magic link ID related to an application
    :return: an SMS
    """
    base_request_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}

    if settings.EXECUTING_AS_TEST == 'True':
        phone = '07700900111'
    else:
        print(link_id)

    notification_request = {
        'personalisation': {
            'link': link_id
        },
        'phoneNumber': phone,
        'templateId': 'd285f17b-8534-4110-ba6c-e7e788eeafb2'
    }
    r = requests.post(base_request_url + '/api/v1/notifications/sms/', json.dumps(notification_request),
                      headers=header)
    return r
