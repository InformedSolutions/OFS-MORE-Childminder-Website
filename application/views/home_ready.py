"""Method returning the template for the Get your home ready page"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms import HomeReadyForm


def home_ready(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Get your home ready template
    """
    if request.method == 'GET':
        application_id_local = request.GET['id']
        form = HomeReadyForm()
        variables = {
            'application_id': application_id_local,
            'form': form
        }
        return render(request, 'next-steps-home.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        form = HomeReadyForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/next-steps/interview?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }

            return render(request, 'next-steps-home.html', variables)
