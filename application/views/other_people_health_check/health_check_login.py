import time
import traceback
import logging

from django.conf import settings
from django.shortcuts import render
from django.urls import reverse

from application.models import Application, ApplicantName
from application.utils import build_url
from ...middleware import CustomAuthenticationHandler
from ...models.adult_in_home import AdultInHome

log = logging.getLogger('django.server')


def validate_magic_link(request, id):
    """
    Method to verify that the URL matches a magic link
    :param request: request to display a magic link page
    :param id: magic link ID
    :return: HttpResponse, directing to the correct page
    """
    try:
        person = AdultInHome.objects.get(token=id)
        application = Application.objects.get(pk=person.application_id.pk)

        if person.validated is not True:
            try:
                applicant_name = ApplicantName.objects.get(application_id=application.pk)
                name = ' '.join([applicant_name.first_name, applicant_name.middle_names, applicant_name.last_name])
            except:
                name = 'An applicant'

            dob_url = build_url('Health-Check-Dob', get={'person_id': person.pk})

            context = {
                'name': name,
                'dob_url': dob_url,
            }

            response = render(request, 'other_people_health_check/start.html', context)
            CustomAuthenticationHandler.create_session(response, person.email)
            return response
        else:
            return render(request, 'bad-link.html')

    except Exception as ex:
        exception_data = traceback.format_exc().splitlines()
        exception_array = [exception_data[-3:]]
        log.error(exception_array)
        return render(request, 'bad-link.html')


def has_expired(expiry):
    """
    Method to check whether a Magic Link URL has expired
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
