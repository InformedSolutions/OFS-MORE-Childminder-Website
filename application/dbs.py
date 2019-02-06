"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- dbs.py --

@author: Informed Solutions

Handler for dbs api
"""

import requests
import json

from django.conf import settings

DBS_API_ENDPOINT = settings.DBS_URL


def read(dbs_certificate_number):
    params = {'certificate_number': dbs_certificate_number}
    response = requests.get(DBS_API_ENDPOINT + '/api/v1/dbs/' + dbs_certificate_number + '/', data=params, verify=False)
    if response.status_code == 200:
        response.record = json.loads(response.text)
    return response


def create(dbs_certificate_number, date_issued, date_of_birth, certificate_information):
    params = {'certificate_number': dbs_certificate_number, 'certificate_information': certificate_information,
              'date_of_issue': date_issued,
              'date_of_birth': date_of_birth}
    response = requests.post(DBS_API_ENDPOINT + '/api/v1/dbs/', data=params, verify=False)
    return response
