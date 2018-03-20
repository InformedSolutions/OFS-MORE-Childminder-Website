"""Method returning the template for the Application saved page (for a given application)"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from application.forms import ApplicationSavedForm


def application_saved(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Application saved template
    """

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ApplicationSavedForm()

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ApplicationSavedForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse('Application-Saved-View') + '?id=' + application_id_local)

    variables = {
        'form': form,
        'application_id': application_id_local
    }
    return render(request, 'application-saved.html', variables)
