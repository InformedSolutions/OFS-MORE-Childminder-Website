"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- dbs.py --

@author: Informed Solutions

Handler for dbs api
"""

import requests
import json


def read(dbs_certificate_number):
    params = {'certificate_number': dbs_certificate_number}
    response = requests.get('http://127.0.0.1:8005/api/v1/dbs/'+dbs_certificate_number+'/', data=params)
    if response.status_code == 200:
        response.record = json.loads(response.text)
    return response


def create(dbs_certificate_number, date_issued, date_of_birth, certificate_information):
    params = {'certificate_number': dbs_certificate_number, 'certificate_information': certificate_information,
              'date_of_issue': date_issued,
              'date_of_birth': date_of_birth}
    response = requests.post('http://127.0.0.1:8005/api/v1/dbs/', data=params)
    return response
