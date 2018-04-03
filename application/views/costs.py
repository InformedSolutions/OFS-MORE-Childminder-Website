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
    if request.method == 'GET':

        application_id = request.GET["id"]
        context = {
            'id': application_id
        }

        return render(request, 'costs-guidance.html', context)

