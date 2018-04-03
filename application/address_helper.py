"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- address_helper.py --

@author: Informed Solutions
"""

import requests
import json
from django.conf import settings


class AddressHelper:

    @staticmethod
    def create_address_lookup_list(postcode):
        """
        Helper method for building a select list of addresses with a count at the top.
        :param postcode: the postcode on which a search will be made (issued to Addressing Service API)
        :return: list of indexed one-line addresses formatted for a ChoiceField
        """
        headers = {"content-type": "application/json"}
        response = requests.get(settings.ADDRESSING_URL + '/api/v1/addresses/' + postcode + '/', headers=headers,
                                verify=False)
        if response.status_code == 200:
            address_matches = json.loads(response.text)
            results = address_matches['results']
            count = address_matches['count']
            results_no = str(count) + ' addresses found'
            addresses = [(None, results_no)]
            for index, address in enumerate(results):
                one_line = address['combinedAddress']
                addresses.append((index, one_line))
            return addresses
        else:
            addresses = []
            return addresses


    @staticmethod
    def issue_postcode_search_address_elements(postcode):
        """
        Helper method for building a select list of addresses with a count at the top.
        :param postcode: the postcode on which a search will be made (issued to Addressing Service API)
        :return: list of one-addresses and JavaScript objects containing address elements
        """
        headers = {"content-type": "application/json"}
        response = requests.get(settings.ADDRESSING_URL + '/api/v1/addresses/' + postcode + '/', headers=headers,
                                verify=False)
        if response.status_code == 200:
            address_matches = json.loads(response.text)
            results = address_matches['results']
            addresses = []
            for address in results:
                one_line = address['combinedAddress']
                elements = {
                    'line1': address['line1'],
                    'line2': address['line2'],
                    'townOrCity': address['townOrCity'],
                    'postcode': address['postcode']
                }
                addresses.append((one_line, elements))
            return addresses
        else:
            addresses = []
            return addresses


    @staticmethod
    def get_posted_address(selected_address_index, postcode):
        """
        Gets a dictionary representation of an address that has been posted in a form
        :param field_name: the name of a POST body field to be queried for an address submission
        :return: a dictionary response object representing a chosen addresss
        """
        addresses = AddressHelper.issue_postcode_search_address_elements(postcode)
        for index, address in enumerate(addresses):
            if index == selected_address_index:
                return address[1]
