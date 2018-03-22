"""Method returning the template for the Prepare for your interview page"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..forms import PrepareForInterviewForm
from ..models import Application


def prepare_for_interview(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Prepare for your interview template
    """

    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = Application.objects.get(
            pk=application_id_local).order_code
        form = PrepareForInterviewForm()
        variables = {
            'application_id': application_id_local,
            'order_code': order_code,
            'form': form
        }
        return render(request, 'next-steps-interview.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        order_code = Application.objects.get(
            pk=application_id_local).order_code
        form = PrepareForInterviewForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(
                reverse('Payment-Confirmation') + '?id=' + application_id_local
                + '&orderCode=' + str(order_code))
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'next-steps-interview.html', variables)
