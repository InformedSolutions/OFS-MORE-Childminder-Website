"""Method returning the template for the Application saved page (for a given application)"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from application.forms import ApplicationSavedForm


# noinspection PyUnboundLocalVariable
def application_saved(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Application saved template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = ApplicationSavedForm()

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = ApplicationSavedForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse('Application-Saved-View') + '?id=' + app_id)
        else:
            variables = {
                'form': form,
                'application_id': app_id
            }
            return render(request, 'application-saved.html', variables)

    variables = {
        'form': form,
        'application_id': app_id
    }
    return render(request, 'application-saved.html', variables)
