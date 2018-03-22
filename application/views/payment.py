import datetime
import json
import re
from uuid import UUID

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from .. import payment
from ..forms import (PaymentDetailsForm,
                     PaymentForm)
from ..models import (ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      UserDetails)


@never_cache
def card_payment_details(request):
    """
    Method returning the template for the Card payment details page (for a given application) and navigating to
    the payment confirmation page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Card payment details template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        paid = Application.objects.get(pk=application_id_local).order_code
        if paid is None:
            form = PaymentDetailsForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'payment-details.html', variables)
        elif paid is not None:
            variables = {
                'application_id': application_id_local,
                'order_code': paid
            }
            return render(request, 'paid.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PaymentDetailsForm(request.POST)
        if form.is_valid():
            card_number = re.sub('[ -]+', '', request.POST["card_number"])
            cardholders_name = request.POST["cardholders_name"]
            card_security_code = str(request.POST["card_security_code"])
            expiry_month = request.POST["expiry_date_0"]
            expiry_year = request.POST["expiry_date_1"]
            # Make payment
            payment_response = payment.make_payment(3500, cardholders_name, card_number, card_security_code,
                                                    expiry_month, expiry_year, 'GBP', application_id_local,
                                                    application_id_local)
            parsed_payment_response = json.loads(payment_response.text)
            # If the payment is successful
            if payment_response.status_code == 201:

                application = Application.objects.get(pk=application_id_local)
                # when functionality to resubmit an application is added this trigger must be added
                # trigger_audit_log(application_id_local, 'RESUBMITTED')
                trigger_audit_log(application_id_local, 'SUBMITTED')
                application.date_submitted = datetime.datetime.today()
                login_id = application.login_id.login_id
                login_record = UserDetails.objects.get(pk=login_id)
                personal_detail_id = ApplicantPersonalDetails.objects.get(
                    application_id=application_id_local).personal_detail_id
                applicant_name_record = ApplicantName.objects.get(
                    personal_detail_id=personal_detail_id)
                payment.payment_email(login_record.email,
                                      applicant_name_record.first_name)
                print('Email sent')
                order_code = parsed_payment_response["orderCode"]
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'order_code': order_code
                }
                application.order_code = UUID(order_code)
                application.save()
                return HttpResponseRedirect(settings.URL_PREFIX + '/confirmation/?id=' + application_id_local +
                                            '&orderCode=' + order_code, variables)
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'error_flag': 1,
                    'error_message': parsed_payment_response["message"],
                }
            return HttpResponseRedirect(settings.URL_PREFIX + '/payment-details/?id=' + application_id_local, variables)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'payment-details.html', variables)


def paypal_payment_completion(request):
    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = request.GET['orderCode']
        # If the payment has been successfully processed
        if payment.check_payment(order_code) == 200:
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
            }

            application = Application.objects.get(pk=application_id_local)
            application.date_submitted = datetime.datetime.today()
            application.order_code = UUID(order_code)
            application.save()

            return HttpResponseRedirect(settings.URL_PREFIX + '/confirmation/?id=' + application_id_local +
                                        '&orderCode=' + order_code, variables)
        else:
            print('HELP')
            return render(request, '500.html')


def payment_confirmation(request):
    """
    Method returning the template for the Payment confirmation page (for a given application)
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment confirmation template
    """
    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = request.GET['orderCode']
        # If the payment has been successfully processed
        if payment.check_payment(order_code) == 200:
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
            }
            local_app = Application.objects.get(
                application_id=application_id_local)
            local_app.application_status = 'SUBMITTED'
            local_app.save()
            return render(request, 'payment-confirmation.html', variables)
        else:
            form = PaymentForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return HttpResponseRedirect(settings.URL_PREFIX + '/payment/?id=' + application_id_local, variables)
