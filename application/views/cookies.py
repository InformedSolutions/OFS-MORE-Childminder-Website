""""
Method for returning the template for the Cookie Policy page
"""

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.conf import settings
from urllib.parse import quote

from ..forms import AnalyticsCookieSelection


# ToDo - Allow the cookie policy page to be viewed when not logged in.
def cookie_policy(request):
    """
    Method returning the template for the cookies page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered cookies template
    """
    if request.method == 'GET':
        form = AnalyticsCookieSelection()
        context = {
            'form': form
        }

        return render(request, 'cookies.html', context)

    elif request.method == 'POST':
        form = AnalyticsCookieSelection(request.POST)
        if form.is_valid():
            cookie_selection = form.cleaned_data['cookie_selection']
            if 'opt in' in cookie_selection:
                cookie_value = 'opted_in'
            if 'opt out' in cookie_selection:
                cookie_value = 'opted_out'

        response = render(request, 'cookies.html', {'form': form})
        response.set_cookie('cookie_preferences', cookie_value)
        return response
