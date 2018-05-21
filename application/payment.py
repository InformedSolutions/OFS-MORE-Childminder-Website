"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- payment.py --

@author: Informed Solutions
"""

import json
import requests

from django.conf import settings


def make_payment(amount, name, number, cvc, expiry_m, expiry_y, currency, code, desc):
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
    :param code: This is the order code the customer will be provided with on the confirmation page, make sure it is the
    same as their application id, this should be a string
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
        "customerOrderCode": code,
        "orderDescription": desc
    }
    response = requests.post(base_url + "/api/v1/payments/card/", json.dumps(payload), headers=header)
    return response


def make_paypal_payment(shopper_country_code, amount, currency_code, order_description, customer_order_code,
                        success_url, pending_url, failure_url, cancel_url):
    """
    Function used to obtain the redirect url that will allow a user to authorise a payment through paypal base off of
    the below parameters
    :param shopper_country_code: The country from which the user is accessing the service
    :param amount: the amount of money to be charge to the users PayPal account
    :param currency_code: Currency code that should be charged, sent as a string, see below for full list:
    https://developer.worldpay.com/jsonapi/faq/articles/what-currencies-can-i-accept-payments-in
    :param order_description: This is the order description the user will see attached to their payment when on PayPal,
    this should be a string
    :param customer_order_code: This is the order code the customer will be provided with on the confirmation page, make
    sure it is the ame as their application id, this should be a string
    :param success_url: This is the url the user should be redirected to upon successfully paying the amount requested,
    sent as a string
    :param pending_url: This is the url the user should be redirected to whilst their payment is pending,
    sent as a string
    :param failure_url: This is the url the user should be redirected to should their payment fail, sent as a string
    :param cancel_url: this is the url the user should be redirected to should they cancel the payment, sent as a string
    :return: Returns the redirect url for the user to be redirected to in order to authorise the payment.
    This is taken from the JSON object the payment gateway gives us, returned as a string
    """
    base_url = settings.PAYMENT_URL
    header = {'content-type': 'application/json'}
    payload = {
        "shopperCountryCode": shopper_country_code,
        "amount": amount,
        "currencyCode": currency_code,
        "customerOrderCode": customer_order_code,
        "orderDescription": order_description,
        "successUrl": success_url,
        "pendingUrl": pending_url,
        "failureUrl": failure_url,
        "cancellationUrl": cancel_url,
    }
    response = requests.post(base_url + "/api/v1/payments/paypal/", json.dumps(payload), headers=header)
    # We deal with the entire object as parsing out just the requestURL in the payment API may be undesirable for other
    # services
    response_url = json.loads(response.text)["redirectURL"]
    return response_url


def check_payment(order_code):
    """
    A function to confirm a worldpay order code exists in Worldpay's records
    :param order_code: the order code of the payment that needs to be checked
    :return: a status code to confirm whether this payment exists or not, these responses are defined in swagger
    """
    base_url = settings.PAYMENT_URL
    header = {'content-type': 'application/json'}
    response = requests.get(base_url + "/api/v1/payments/" + order_code, headers=header)
    return response.status_code


def payment_email(email, name):
    """
    A function to send an email through the notify gateway with a payment template, currently used to confirm a Worldpay
    card order has been successful
    :param email: The address to send the email to, sent as a string
    :param name: The name to be placed on the email template to be sent to the user
    :return: Returns the response object obtained from the PayPal gateway method, as defined in swagger
    """
    base_url = settings.NOTIFY_URL
    header = {'content-type': 'application/json'}
    payload = {
        "email": email,
        "personalisation": {
            "firstName": name
        },
        "reference": "string",
        "templateId": "a741fed2-7948-4b1a-b44a-fec8485ec700"
    }
    response = requests.post(base_url + "/api/v1/notifications/email/", json.dumps(payload),
                             headers=header)
    return response
