"""
Utility functions for generating a new unique application reference number
"""
import json

import requests
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def create_application_reference():
    """
    Function for getting the next available URN from NOO such that it can be allocated to a Childminder application
    :return: a unique reference number for an application
    """
    try:
        integration_adapter_endpoint = settings.INTEGRATION_ADAPTER_URL
        response = requests.get(integration_adapter_endpoint + '/api/v1/urns/')

        response_body_as_json = response.json()
        urn = response_body_as_json['URN']

        # Note that the EY prefix is appended here as this is not returned by NOO
        return str(urn)
    except Exception as e:
        logger.error('Failed to allocate application reference number: ' + str(e))

