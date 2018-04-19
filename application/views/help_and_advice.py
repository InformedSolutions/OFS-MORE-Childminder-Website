"""
Method for returning the template for the Help page
"""
from django.shortcuts import render


def help_and_advice(request):
    """
    Renders the help and advice page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Help and Advice template
    """
    application_id_local = request.GET.get('id')
    context = {
        'application_id': application_id_local
    }
    return render(request, 'help-and-advice.html', context)
