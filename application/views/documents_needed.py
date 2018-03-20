"""Method returning the template for the Documents you need for the visit page"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..models import Application
from ..forms import DocumentsNeededForm


def documents_needed(request):
    """
    Method returning the template for the Documents you need for the visit page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Documents you need for the visit template
    """
    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = Application.objects.get(
            pk=application_id_local).order_code
        form = DocumentsNeededForm()
        variables = {
            'application_id': application_id_local,
            'order_code': order_code,
            'form': form
        }
        return render(request, 'next-steps-documents.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DocumentsNeededForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/next-steps/home?id=' + application_id_local)

    variables = {
        'form': form,
        'application_id': application_id_local
    }
    return render(request, 'next-steps-documents.html', variables)
