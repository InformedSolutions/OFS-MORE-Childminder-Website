"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- utils.py --

@author: Informed Solutions
"""
import json
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import render

from .models import Application, Reference, CriminalRecordCheck, EYFS, HealthDeclarationBooklet, ChildInHome, \
    ChildcareType, FirstAidTraining, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, AdultInHome


def get_app_task_models(app_id):
    """
    Fucntion to get the models corresponding to each task for a given application.
    :param app_id: ID of the application.
    :return: dict whose keys are the models for each task with values that are the IDs of the task.
    """

    if app_id:

        models = [
            Application, Reference, CriminalRecordCheck, EYFS, HealthDeclarationBooklet, ChildInHome,
            ChildcareType, FirstAidTraining, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress,
            AdultInHome
        ]
        app_id_models = dict()

        for model in models:
            app_id_models[model.__name__] = getattr(model, 'get_id', None)

        return app_id_models

    return False


def can_cancel(application):
    """
    This method checks to see if the application status is in Drafting to see if it can be can be cancelled.
    :param application: application object
    :return: Boolean
    """
    if application.application_status == 'DRAFTING':
        return True
    else:
        return False

    return can_cancel


def test_notify():
    # If running exclusively as a test return true to avoid overuse of the notify API
    if settings.EXECUTING_AS_TEST:
        return True

    if test_notify_connection():
        return True
    else:
        return False


def test_notify_settings():
    """
    Function to check if url for notify app is defined.
    return; Bool
    """
    url = settings.NOTIFY_URL
    if 'url' in locals():
        return True
    else:
        return False


def test_notify_connection():
    """
    Function to test connection with Notify API.
    :return: Bool
    """
    try:
        # Test Sending Email
        header = {'content-type': 'application/json'}
        req = requests.Session()
        notification_request = {
            'email': 'simulate-delivered@notifications.service.gov.uk',
            'personalisation': {
                'link': 'test'
            },
            'templateId': 'ecd2a788-257b-4bb9-8784-5aed82bcbb92'
        }
        r = req.post(settings.NOTIFY_URL + '/api/v1/notifications/email/',
                     json.dumps(notification_request),
                     headers=header, timeout=10)
        if r.status_code == 201:
            return True
    except Exception as ex:
        print(ex)
        return False


def service_down(request):
    """
    View to be returned when the servie is down.
    :param request: request used to generate HttpResponse.
    :return: rendered service-down.html template.
    """
    return render(request, 'service-down.html')


def date_formatter(day, month, year):
    """

    :param day: The day of the date to be formatted (should be integer on arrival)
    :param month: The month of the date to be formatted (should be integer on arrival)
    :param year: The year of the date to be formatted (should be integer on arrival)
    :return: The day, month, and year all formatted as strings with formatting specified in [CCN3-784]
    """

    output_day = str(day).zfill(2)
    output_month = str(month).zfill(2)
    output_year = str(year)

    return output_day, output_month, output_year


def date_combiner(day, month, year):
    date = day + '.' + month + '.' + year + '.'
    return date


def date_splitter(date):
    split_date = date.split('.')
    return split_date


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url
