"""
Method returning the template for the Card payment details page
(for a given application) and navigating to the payment confirmation
page when successfully completed
"""

import datetime
import re
import json
from uuid import UUID

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from timeline_logger.models import TimelineLog

from .. import payment
from ..forms import PaymentDetailsForm
from ..models import Application, UserDetails, ApplicantPersonalDetails, ApplicantName


@never_cache
def card_payment_details(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Card payment details template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        paid = Application.objects.get(pk=app_id).order_code

        if paid is None:

            form = PaymentDetailsForm()
            variables = {
                'form': form,
                'application_id': app_id
            }
            return render(request, 'payment-details.html', variables)

        elif paid is not None:

            variables = {
                'application_id': app_id,
                'order_code': paid
            }
            return render(request, 'paid.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PaymentDetailsForm(request.POST)

        if form.is_valid():

            card_number = re.sub('[ -]+', '', request.POST["card_number"])
            cardholders_name = request.POST["cardholders_name"]
            card_security_code = str(request.POST["card_security_code"])
            expiry_month = request.POST["expiry_date_0"]
            expiry_year = request.POST["expiry_date_1"]

            print("Card number: " + card_number)
            print("Cardholders name: " + cardholders_name)
            print("Card security code: " + card_security_code)
            print("Expiry month: " + expiry_month)
            print("Expiry year: " + expiry_year)

            # Make payment
            payment_response = payment.make_payment(
                3500, cardholders_name, card_number, card_security_code,
                expiry_month, expiry_year, 'GBP', app_id,
                app_id)
            parsed_payment_response = json.loads(payment_response.text)

            # If the payment is successful
            if payment_response.status_code == 201:

                application = Application.objects.get(pk=app_id)
                application.date_submitted = datetime.datetime.today()
                login_record = UserDetails.objects.get(application_id=application)
                personal_detail_id = ApplicantPersonalDetails.objects.get(
                    application_id=app_id).personal_detail_id
                applicant_name_record = ApplicantName.objects.get(
                    personal_detail_id=personal_detail_id)
                payment.payment_email(login_record.email,
                                      applicant_name_record.first_name)

                print('Email sent')

                order_code = parsed_payment_response["orderCode"]
                variables = {
                    'form': form,
                    'application_id': app_id,
                    'order_code': order_code
                }

                application.order_code = UUID(order_code)
                application.save()

                # when functionality to resubmit an application is added this trigger must be added
                # trigger_audit_log(app_id, 'RESUBMITTED')
                TimelineLog.objects.create(
                    content_object=application,
                    user=None,
                    template='timeline_logger/application_action.txt',
                    extra_data={'user_type': 'applicant', 'action': 'submitted', 'entity': 'application'}
                )

                return HttpResponseRedirect(
                    reverse('Payment-Confirmation') \
                        + '?id=' + app_id + '&orderCode=' + order_code,
                    variables)

            else:

                variables = {
                    'form': form,
                    'application_id': app_id,
                    'error_flag': 1,
                    'error_message': parsed_payment_response["message"],
                }
            return HttpResponseRedirect(
                reverse('Payment-Details-View') + '?id=' + app_id, variables)

        else:
            variables = {
                'form': form,
                'application_id': app_id
            }
            return render(request, 'payment-details.html', variables)
