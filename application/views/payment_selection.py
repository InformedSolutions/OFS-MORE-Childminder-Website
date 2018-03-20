"""
Method returning the template for the Payment page (for a given application) and navigating to
the card payment details page or PayPal site when successfully completed
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from .. import payment
from ..forms import PaymentForm
from ..models import Application


def payment_selection(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment template
    """
    if request.method == 'GET':

        application_id_local = request.GET["id"]
        paid = Application.objects.get(pk=application_id_local).order_code
        print(paid)

        if paid is None:

            form = PaymentForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'payment.html', variables)

        elif paid is not None:

            variables = {
                'application_id': application_id_local,
                'order_code': paid
            }
            return render(request, 'paid.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        form = PaymentForm(request.POST)

        if form.is_valid():

            payment_method = form.cleaned_data['payment_method']
            application_url_base = settings.PUBLIC_APPLICATION_URL

            if payment_method == 'Credit':

                return HttpResponseRedirect(
                    reverse('Payment-Details-View') + '?id=' + application_id_local)

            elif payment_method == 'PayPal':

                paypal_url = payment.make_paypal_payment(
                    "GB", 3500,
                    "GBP",
                    "Childminder Registration Fee",
                    application_id_local, application_url_base +
                    "/paypal-payment-completion/?id=" + application_id_local,
                    application_url_base + "/payment/?id=" + application_id_local,
                    application_url_base + "/payment/?id=" + application_id_local,
                    application_url_base + "/payment/?id=" + application_id_local)
                return HttpResponseRedirect(paypal_url)

    form.error_summary_title = 'There was a problem on this page'
    variables = {
        'form': form,
        'application_id': application_id_local
    }
    return render(request, 'payment.html', variables)
