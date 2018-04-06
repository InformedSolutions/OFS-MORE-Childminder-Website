from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application.models import Application


def cancel_app(request):

    if request.method == 'GET':
        print("WHY?")
        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'cancel-application.html', variables)

    if request.method == 'POST':
        try:
            app_id = request.POST["id"]
            if Application.objects.filter(application_id=app_id).exists():
                Application.objects.get(application_id=app_id).delete()
        except Exception as ex:
            print(ex)
        print("about to go")
        return HttpResponseRedirect(reverse('Cancel-Application-Confirmation'))


def cancel_app_confirmation(request):
    print("HERE")
    return render(request, 'cancel-application-confirmation.html')


def cr_cancel_app(request):

    if request.method == 'GET':
        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'cr-cancel-application.html', variables)

    if request.method == 'POST':
        try:
            app_id = request.POST["id"]
            if Application.objects.filter(application_id=app_id).exists():
                Application.objects.get(application_id=app_id).delete()
        except Exception as ex:
            print(ex)
        return HttpResponseRedirect(reverse('CR-Cancel-Application-Confirmation'))


def cr_cancel_app_confirmation(request):
    print("HERE")
    return render(request, 'cr-cancel-application-confirmation.html')