"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- payment_service.py --

@author: Informed Solutions
"""

import json
import time
from urllib.parse import quote
from .models import CriminalRecordCheck
from application.notify import send_email

import requests

from django.conf import settings


def make_payment(amount, name, number, cvc, expiry_m, expiry_y, currency, customer_order_code, desc):
    """
    Function used to send a WorldPay card payment request to the payment gateway, all validation is done by the gateway,
    appropriate error response will be sent in JSON
    :param amount: amount of money to be charged, send as an integer. Done in pence, so £35 would be 3500
    :param name: name of the card holder, send as a string. This should be what is written on the card
    :param number: card number, sent as an integer. This should be what is written on the card
    :param cvc: cvc number on back of card. This should be sent as an integer
    :param expiry_m: expiry month on the card, sent as an integer. This should be what is written on the card
    :param expiry_y: expiry year on the card, sent as an integer. This should be what is written on the card
    :param currency: Currency code that should be charged, sent as a string, see below for full list:
    https://developer.worldpay.com/jsonapi/faq/articles/what-currencies-can-i-accept-payments-in
    :param customer_order_code: This is the order code the customer will be provided with on the confirmation page
    :param desc: This is the order description the user will see attached to their payment when on PayPal, this should
    be a string
    :return: returns a full http response object containing either order details on success or an error message on
    failure
    """
    base_url = settings.PAYMENT_URL
    header = {'content-type': 'application/json'}
    payload = {
        "amount": amount,
        "cardHolderName": name,
        "cardNumber": number,
        "cvc": cvc,
        "expiryMonth": expiry_m,
        "expiryYear": expiry_y,
        "currencyCode": currency,
        "customerOrderCode": customer_order_code,
        "orderDescription": desc
    }
    response = requests.post(base_url + "/api/v1/payments/card/", json.dumps(payload),
                             headers=header, timeout=int(settings.PAYMENT_HTTP_REQUEST_TIMEOUT))
    return response


def check_payment(payment_reference):
    """
    A function to confirm a worldpay order code exists in Worldpay's records
    :param payment_reference: the order code of the payment that needs to be checked
    :return: a status code to confirm whether this payment exists or not, these responses are defined in swagger
    """
    base_url = settings.PAYMENT_URL
    header = {'content-type': 'application/json'}
    query_path = base_url + "/api/v1/payments/" + quote(payment_reference)
    response = requests.get(query_path, headers=header, timeout=int(settings.PAYMENT_HTTP_REQUEST_TIMEOUT))
    return response


def payment_email(email, name, application_reference, application_id):
    """
    A function to send an email through the notify gateway with a payment template, currently used to confirm a Worldpay
    card order has been successful
    :param email: The address to send the email to, sent as a string
    :param name: The name to be placed on the email template to be sent to the user
    :param application_reference
    :param application_id
    :return: Returns the response object obtained from the PayPal gateway method, as defined in swagger
    """
    conviction = CriminalRecordCheck.objects.get(application_id=application_id).cautions_convictions

    if conviction is False:
        template_id = '2cd5f1c5-4900-4922-a627-a0d1f674136b'
    elif conviction is True:
        template_id = 'c7500574-df3c-4df1-b7f7-8755f6b61c7f'

    response = send_email(email, {"firstName": name, "ref": application_reference}, template_id)

    return response


def created_formatted_payment_reference(application_reference):
    """
    Function for formatting a payment reference to be issued to the payment provider
    :param application_reference: a unique applicaiton reference
    :return: a formatted payment reference
    """
    prefix = 'MORE'
    timestamp = time.strftime("%Y%m%d%H%M%S")
    formatted_payment_reference = str(prefix + ':' + application_reference + ':' + timestamp)
    return formatted_payment_reference
