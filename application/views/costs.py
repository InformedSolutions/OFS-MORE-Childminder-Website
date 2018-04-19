"""
View logic for rendering the costs page
"""
from django.shortcuts import render


def costs(request):
    """
    Method for rendering the costs page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered costs template
    """
    application_id_local = request.GET.get('id')
    context = {
        'id': application_id_local
    }
    return render(request, 'costs-guidance.html', context)

