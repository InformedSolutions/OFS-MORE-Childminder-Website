from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application.models import Application


def cancel_app(request):
    """
    This is the page where you can cancel your application and delete all your data
    :param request: HTTP Request
    :return: HTTP Response
    """
    if request.method == 'GET':
        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'cancel-application.html', variables)

    if request.method == 'POST':
        app_id = request.POST["id"]
        delete_app(app_id)
        return HttpResponseRedirect(reverse('Cancel-Application-Confirmation'))


def cancel_app_confirmation(request):
    """
    This is one of the cancel application confirmation pages
    :param request: Http Request
    :return: Http Response
    """
    return render(request, 'cancel-application-confirmation.html')


def cr_cancel_app(request):
    """
    This is the page where you can cancel your application and delete all your data
    :param request: HTTP Request
    :return: HTTP Response
    """
    if request.method == 'GET':
        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'cr-cancel-application.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        delete_app(app_id)

        return HttpResponseRedirect(reverse('CR-Cancel-Application-Confirmation'))


def cl_cancel_app(request):
    """
    Method returning the service unavailable page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Service unavailable template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'cl-cancel-application.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        delete_app(app_id)

        # The cr-cancel-application-confirmation is an appropriate template for both the cl and cr journey.
        return HttpResponseRedirect(reverse('CR-Cancel-Application-Confirmation'))


def cr_cancel_app_confirmation(request):
    """
    This is one of the cancel application confirmation pages
    :param request: Http Request
    :return: Http Response
    """
    return render(request, 'cr-cancel-application-confirmation.html')


def delete_app(app_id):
    """
    Method for deleting an existing application.
    :param app_id: ID of the app to be deleted.
    :return: None.
    """
    if Application.objects.filter(application_id=app_id).exists():
        Application.objects.get(application_id=app_id).delete()
