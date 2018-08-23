""""
Method for returning the template for the Feedback page
"""

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.conf import settings
from urllib.parse import quote

from ..notify import send_email
from ..forms import FeedbackForm, FeedbackConfirmationForm


def feedback(request):
    """
    Method returning the template for the Feedback page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Feedback template
    """

    if request.method == 'GET':
        previous_url = request.GET["url"]
        form = FeedbackForm()
        variables = {
            'form': form,
            'previous_url': previous_url
        }

        return render(request, 'feedback.html', variables)

    if request.method == 'POST':
        previous_url = request.POST["url"]
        app_id = None
        if 'id' in request.GET:
            app_id = request.GET["id"]
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.cleaned_data['feedback']
            email_address = form.cleaned_data['email_address']
            if email_address == '':
                email_address = 'Not provided'
            personalisation = {
                'feedback': feedback,
                'email_address': email_address
            }
            email = settings.FEEDBACK_EMAIL
            template_id = '650b7c59-dd31-4876-869d-ea8bfd76063a'
            r = send_email(email, personalisation, template_id)
            print(r)

            if app_id:
                return HttpResponseRedirect(reverse('Feedback-Confirmation') + '?url=' + quote(previous_url) + '&id=' + app_id)
            else:
                return HttpResponseRedirect(reverse('Feedback-Confirmation') + '?url=' + quote(previous_url))

        else:
            form.error_summary_title = 'There was a problem'
            variables = {
                'form': form,
                'previous_url': previous_url
            }

            return render(request, 'feedback.html', variables)


def feedback_confirmation(request):
    """
    Method returning the template for the Feedback confirmation page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Feedback confirmation template
    """

    if request.method == 'GET':
        previous_url = request.GET["url"]
        form = FeedbackConfirmationForm()
        variables = {
            'form': form,
            'previous_url': previous_url
        }

        return render(request, 'feedback-confirmation.html', variables)

    if request.method == 'POST':
        previous_url = request.POST["url"]
        form = FeedbackConfirmationForm(request.POST)

        if form.is_valid():

            return HttpResponseRedirect(previous_url)

        else:

            variables = {
                'form': form,
                'previous_url': previous_url
            }

            return render(request, 'feedback-confirmation.html', variables)
