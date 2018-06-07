""""
Method for returning the template for the Feedback page
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms import FeedbackForm


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
        form = FeedbackForm(request.POST)

        if form.is_valid():
            return HttpResponseRedirect(previous_url)

        else:
            form.error_summary_title = 'There was a problem'
            variables = {
                'form': form
            }

            return render(request, 'feedback.html', variables)
