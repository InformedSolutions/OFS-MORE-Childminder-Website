import datetime
from uuid import UUID

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from timeline_logger.models import TimelineLog

from .. import payment
from ..forms import (PaymentForm)
from ..models import (Application)
from ..models import (CriminalRecordCheck)

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
            try:
                conviction = CriminalRecordCheck.objects.get(application_id=application_id_local).cautions_convictions
            except CriminalRecordCheck.DoesNotExist:
                conviction = False
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
                'conviction': conviction,
                'health_status': Application.objects.get(application_id=application_id_local).health_status
            }
            local_app = Application.objects.get(
                application_id=application_id_local)
            local_app.application_status = 'SUBMITTED'
            local_app.save()

            # Payment presents the first true trigger for submission so is logged as submitted at this point
            TimelineLog.objects.create(
                content_object=local_app,
                user=None,
                template='timeline_logger/application_action.txt',
                extra_data={'user_type': 'applicant', 'action': 'submitted by', 'entity': 'application'}
            )

            return render(request, 'payment-confirmation.html', variables)
        else:
            form = PaymentForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return HttpResponseRedirect(settings.URL_PREFIX + '/payment/?id=' + application_id_local, variables)

    if request.method == 'POST':
        application_id_local = request.GET['id']
