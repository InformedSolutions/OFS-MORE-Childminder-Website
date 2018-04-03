"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- notify.py --

@author: Informed Solutions

Handler for dispatching email notifications via the GOV.UK notify gateway api.
"""

import json

import requests
from django.conf import settings


def send_email(email, template):
    """
    Method to send a magic link email using the Notify Gateway API
    :param email: string containing the e-mail address to send the e-mail to
    :param link_id: string containing the magic link ID related to an application
    :return: an email
    """

    if template == 'submitted':
        template_id = ''
    elif template == '':
        template_id = ''

    base_request_url = settings.NOTIFY_URL
    template_id = ''
    header = {'content-type': 'application/json'}
    notification_request = {
        'email': email,
        # 'personalisation': {
        #     'link': 'This is a temporary email for '
        # },
        'reference': 'string',
        'templateId': template_id
    }
    r = requests.post(base_request_url + '/api/v1/notifications/email/',
                      json.dumps(notification_request),
                      headers=header)
    return r