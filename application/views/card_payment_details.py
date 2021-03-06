"""
Method returning the template for the Card payment details page
(for a given application) and navigating to the payment confirmation
page when successfully completed
"""

import datetime
import logging
import re
import json
import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from ..services import payment_service, noo_integration_service
from ..forms import PaymentDetailsForm
from ..models import Application, ApplicantName, Payment, ChildcareType
from ..messaging.sqs_handler import SQSHandler

from ..business_logic import get_childcare_register_type

logger = logging.getLogger(__name__)

sqs_handler = SQSHandler(settings.PAYMENT_NOTIFICATIONS_QUEUE_NAME)


@never_cache
def card_payment_details(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Card payment details template
    """
    if request.method == 'GET':
        return card_payment_get_handler(request)

    if request.method == 'POST':
        return card_payment_post_handler(request)


def card_payment_get_handler(request):
    """
    GET handler for card payment details page
    :param request: inbound HTTP request
    :return: A page for capturing card payment details
    """
    app_id = request.GET["id"]
    application = Application.objects.get(pk=app_id)
    paid = application.application_reference
    prior_payment_record_exists = Payment.objects.filter(application_id=application).exists()
    childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

    if not prior_payment_record_exists:
        form = PaymentDetailsForm()
        variables = {
            'form': form,
            'application_id': app_id,
            'cost': childcare_register_cost,
        }

        return render(request, 'payment-details.html', variables)

    # If a previous attempt has been made, fetch payment record
    payment_record = Payment.objects.get(application_id=application)

    # If payment has been fully authorised show fee paid page
    if payment_record.payment_authorised:
        variables = {
            'application_id': app_id,
            'order_code': paid,
            'cost': childcare_register_cost,
        }
        return render(request, 'paid.html', variables)

    # If none of the above have resulted in a yield, show payment page
    form = PaymentDetailsForm()
    variables = {
        'form': form,
        'application_id': app_id,
        'cost': childcare_register_cost,
    }

    return render(request, 'payment-details.html', variables)


def card_payment_post_handler(request):
    """
    Handler for managing card payment POST requests
    :param request: inbound HTTP POST request
    :return: confirmation of payment or error page based on payment processing outcome
    """
    logger.info('Received request to process card payment')

    app_id = request.POST["id"]
    form = PaymentDetailsForm(request.POST)
    childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

    # If form is erroneous due to an invalid form, simply return form to user as an early return
    if not form.is_valid():
        variables = {
            'form': form,
            'application_id': app_id,
            'cost': childcare_register_cost
        }
        return render(request, 'payment-details.html', variables)

    application = Application.objects.get(pk=app_id)
    childcare_type = ChildcareType.objects.get(application_id=app_id)
    amount = int(childcare_register_cost) * 100  # Payment amount needs to be in pence

    # Boolean flag for managing logic gates
    prior_payment_record_exists = Payment.objects.filter(application_id=application).exists()

    # Ensure payment record exists so any following requests do not enter logic gate
    __create_payment_record(application)

    # If no prior payment record exists, request to capture the payment
    if not prior_payment_record_exists:

        # Assign the application reference - request goes to NOO to reserve this
        try:
            __assign_application_reference(application)
        except Exception as e:
            logger.error('An error was incurred whilst attempting to fetch a new URN')
            logger.error(str(e))
            __rollback_payment_submission_status(application)
            # In the event a URN could not be fetched yield error page to user as the payment reference
            # cannot be generated without said URN
            return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                            childcare_register_cost)

        # Set the official payment reference (uses the application reference)
        payment_reference = __assign_payment_reference(application)

        # Attempt to lodge payment by pulling form POST details
        card_number = re.sub('[ -]+', '', request.POST["card_number"])  
        cardholders_name = request.POST["cardholders_name"]
        card_security_code = str(request.POST["card_security_code"])
        expiry_month = request.POST["expiry_date_0"]
        expiry_year = '20' + request.POST["expiry_date_1"]

        # Invoke Payment Gateway API
        create_payment_response = payment_service.make_payment(
            amount, cardholders_name, card_number, card_security_code,
            expiry_month, expiry_year, 'GBP', payment_reference,
            'Ofsted Fees')

        if create_payment_response.status_code == 201:

            # Mark payment submission flag to show an initial request has been lodged
            # if response status indicates success
            __mark_payment_record_as_submitted(application)

            # Parse JSON response
            parsed_payment_response = json.loads(create_payment_response.text)

            if parsed_payment_response.get('lastEvent') == "AUTHORISED":

                # If payment response is immediately authorised, yield success page
                return __handle_authorised_payment(application, amount)

            if parsed_payment_response.get('lastEvent') == "REFUSED":

                # If payment has been marked as a REFUSED by Worldpay then payment has
                # been attempted but was not successful in which case a new order should be attempted.
                __rollback_payment_submission_status(application)
                return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                                childcare_register_cost)

            if parsed_payment_response.get('lastEvent') == "ERROR":
                __rollback_payment_submission_status(application)
                return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                                childcare_register_cost)

        else:
            # If non-201 return status, this indicates a Payment gateway or Worldpay failure
            logger.info('Payment failed - rolling back payment status for application ' +
                        str(application.application_id))
            __rollback_payment_submission_status(application)
            return __yield_general_processing_error_to_user(request, form, app_id, childcare_register_cost)

    # If above logic gates have not been triggered, this indicates a form re-submission whilst processing
    # was taking place
    return resubmission_handler(request, form, application, amount, childcare_register_cost)


def resubmission_handler(request, form, application, amount, childcare_register_cost):
    """
    Handling logic for managing page re-submissions to avoid duplicate payments being created
    :param request: Inbound HTTP post request
    :param form: the Django form for the card details page
    :param application: the user's childminder application
    :param amount: the payment amount in pence
    :param childcare_register_cost: the payment amount in GBP
    :return: HTTP response redirect based on payment status check outcome
    """
    logger.info('Resubmission handler triggered due to multiple payment requests')

    # All logic below acts as a handler for page re-submissions
    time.sleep(int(settings.PAYMENT_STATUS_QUERY_INTERVAL_IN_SECONDS))

    prior_payment_record_exists = Payment.objects.filter(application_id=application).exists()
    if prior_payment_record_exists:
        payment = Payment.objects.get(application_id=application)
        if payment.payment_reference is not None and payment.payment_reference != "PENDING":
            # Check at this point whether Worldpay has marked the payment as authorised
            payment_status_response_raw = payment_service.check_payment(payment.payment_reference)

            # If no record of the payment could be found, yield error
            if payment_status_response_raw.status_code == 404:
                logger.info('Worldpay payment record does not exist for application ' + str(application.application_id))
                # If payment record was rolled back then payment has not successfully been taken
                return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                                    childcare_register_cost)

            # Deserialize Payment Gateway API response
            parsed_payment_response = json.loads(payment_status_response_raw.text)

            if parsed_payment_response.get('lastEvent') == "AUTHORISED":
                # If payment has been marked as a AUTHORISED by Worldpay then payment has been captured
                # meaning user can be safely progressed to confirmation page
                return __handle_authorised_payment(application, amount)
            if parsed_payment_response.get('lastEvent') == "REFUSED":
                # If payment has been marked as a REFUSED by Worldpay then payment has
                # been attempted but was not successful in which case a new order should be attempted.
                __rollback_payment_submission_status(application)
                return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                                childcare_register_cost)
            if parsed_payment_response.get('lastEvent') == "ERROR":
                return __yield_general_processing_error_to_user(request, form, application.application_id,
                                                                childcare_register_cost)
            else:
                if 'processing_attempts' in request.META:
                    processing_attempts = int(request.META.get('processing_attempts'))

                    # If 3 attempts to process the payment have already been made without success
                    # yield error to user
                    if processing_attempts >= settings.PAYMENT_PROCESSING_ATTEMPTS:
                        form.add_error(None, 'There has been a problem when trying to process your payment. '
                                             'Please contact Ofsted for assistance.',)
                        form.error_summary_template_name = 'error-summary.html'

                        variables = {
                            'form': form,
                            'application_id': application.application_id,
                            'cost': childcare_register_cost
                        }

                        return HttpResponseRedirect(
                            reverse('Payment-Details-View') + '?id=' + application.application_id, variables)

                    # Otherwise increment processing attempt count
                    request.META['processing_attempts'] = processing_attempts + 1
                else:
                    request.META['processing_attempts'] = 1

                # Retry processing of payment
                return resubmission_handler(request, form, application, amount, childcare_register_cost)

        else:
            # No payment reference exists - clear the payment record so that applicant can try again
            __rollback_payment_submission_status(application)
            __yield_general_processing_error_to_user(request, form, application.application_id,
                                                     childcare_register_cost)

    else:
        # No payment record exists
        __yield_general_processing_error_to_user(request, form, application.application_id,
                                                 childcare_register_cost)


def __assign_application_reference(application):
    """
    Private helper function for assigning an application reference number if one has not already allocated
    :param application: the application for which a reference is to be assigned
    :returns application reference number
    """
    # If form is valid create application reference number and assign
    # it to the application if not already present
    if application.application_reference is None:
        logger.info('Generating application reference number '
                    'for application with id: ' + str(application.application_id))
        application_reference = noo_integration_service.create_application_reference()
        application.application_reference = application_reference
        application.save()
        return application_reference
    else:
        return application.application_reference


def __assign_payment_reference(application):
    """
    Private helper method to create formatted payment reference for finance reconciliation purposes
    :param application: the application for which a new payment reference is to be assigned
    :return: a payment reference number for an application (either new or existing)
    """
    payment_record = Payment.objects.get(application_id=application.application_id)
    if payment_record.payment_reference == "PENDING":
        logger.info('Assigning new payment reference for application with id ' + str(application.application_id))
        payment_reference = payment_service.created_formatted_payment_reference(application.application_reference)
        payment_record.payment_reference = payment_reference
        payment_record.save()
        return payment_reference
    else:
        logger.info('Returning existing payment reference for application with id: ' + str(application.application_id))
        return payment_record.payment_reference


def __create_payment_record(application):
    """
    Private helper function for creating a payment record in the event one does not previously exist.
    :param application: the application for which a new payment record is to be created
    """

    prior_payment_record_exists = Payment.objects.filter(application_id=application).exists()

    # Lodge payment record if does not currently exist
    if not prior_payment_record_exists:
        logger.info('Creating new payment record '
                    'for application with id: ' + str(application.application_id))

        Payment.objects.create(
            application_id=application,
            payment_reference="PENDING"
        )


def __handle_authorised_payment(application, amount):
    """
    Private helper function for managing a rejected payment
    :param application: application associated with the payment attempting to be made
    :return: redirect to payment confirmation page
    """

    # Update payment record to finalise approval of payment
    __mark_payment_record_as_authorised(application)

    # Transition application to submitted
    logger.info('Assigning submitted date for application with id: ' + str(application.application_id))
    application.date_submitted = datetime.datetime.today()
    application.save()

    # Send ad-hoc payment to NOO
    app_cost_float = float(amount / 100)
    msg_body = __build_message_body(application, format(app_cost_float, '.4f'))
    sqs_handler.send_message(msg_body)

    return __redirect_to_payment_confirmation(application.application_id)


def __mark_payment_record_as_submitted(application):
    """
    Private helper function for marking a payment as submitted to Worldpay
    :param application: the application for which a payment record is to be marked as submitted
    """
    logger.info('Marking payment as SUBMITTED for application with id: ' + str(application.application_id))
    payment_record = Payment.objects.get(application_id=application.application_id)
    payment_record.payment_submitted = True
    payment_record.save()


def __mark_payment_record_as_authorised(application):
    """
    Private helper function for marking a payment as processed by Worldpay
    :param application: the application for which a payment record is to be marked as authorised
    """
    logger.info('Marking payment as AUTHORISED for application with id: ' + str(application.application_id))
    payment_record = Payment.objects.get(application_id=application.application_id)
    payment_record.payment_authorised = True
    payment_record.save()


def __yield_general_processing_error_to_user(request, form, app_id, childcare_register_cost):
    """
    Private helper function to show a non-field relevant error on the payment details page
    :param request: inbound HTTP request
    :param form: the Django/GOV.UK form to which the error will be appended
    :param app_id: the user's application id
    :param childcare_register_cost: the payment amount in GBP
    :return: HTML template inclusive of a processing error
    """

    form.add_error(None, 'There has been a problem when trying to process your payment. '
                         'Your card has not been charged. '
                         'Please check your card details and try again.')
    form.error_summary_template_name = 'error-summary.html'

    # Payment failure path if server error encountered
    variables = {
        'form': form,
        'application_id': app_id,
        'cost': childcare_register_cost
    }

    return render(request, 'payment-details.html', variables)


def __rollback_payment_submission_status(application):
    """
    Method for rolling back a payment submission if card details have been declined
    :param application: the application for which a payment is to be rolled back
    """
    logger.info('Rolling payment back for application with id: '
                + str(application.application_id))

    if Payment.objects.filter(application_id=application).exists():
        payment_record = Payment.objects.get(application_id=application.application_id)
        if not payment_record.payment_authorised:
            # Only delete the record if the payment is not authorised
            payment_record.delete()
        else:
            logger.info('Rollback cancelled - payment has already been authorised')


def __redirect_to_payment_confirmation(app_id):
    """
    Private helper function for redirecting to the payment confirmation page
    :return: payment confirmation page redirect
    """
    application = Application.objects.get(pk=app_id)
    return HttpResponseRedirect(
        reverse('Payment-Confirmation')
        + '?id=' + str(app_id)
        + '&orderCode=' + application.application_reference
    )


def __build_message_body(application, amount):
    """
    Helper method to build an SQS request to be picked up by the Integration Adapter component
    for relay to NOO
    :param application: the application for which a payment request is to be generated
    :param amount: the amount that the payment was for
    :return: an SQS request that can be consumed up by the Integration Adapter component
    """

    application_reference = application.application_reference
    applicant_name_obj = ApplicantName.objects.get(application_id=application)

    if len(applicant_name_obj.middle_names):
        applicant_name = applicant_name_obj.last_name + ',' + applicant_name_obj.first_name + " " + applicant_name_obj.middle_names
    else:
        applicant_name = applicant_name_obj.last_name + ',' + applicant_name_obj.first_name

    payment_reference = Payment.objects.get(application_id=application).payment_reference

    return {
        "payment_action": "SC1",
        "payment_ref": payment_reference,
        "payment_amount": amount,
        "urn": str(settings.PAYMENT_URN_PREFIX) + application_reference,
        "setting_name": applicant_name
    }
