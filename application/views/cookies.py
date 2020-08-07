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
        # Set default form value if preferences are already set
        initial_form_state = None
        if 'cookie_preferences' in request.COOKIES:
            preference = request.COOKIES['cookie_preferences']
            initial_form_state = {'cookie_selection': preference}

        form = AnalyticsCookieSelection(initial=initial_form_state)
        cookie_preference_set = 'cookie_preferences' in request.COOKIES
        context = {
            'form': form,
            'cookie_preference_set': cookie_preference_set
        }

        return render(request, 'cookies.html', context)

    elif request.method == 'POST':
        # Set cookie based on what the user put in the form
        form = AnalyticsCookieSelection(request.POST)
        if form.is_valid():
            cookie_value = form.cleaned_data['cookie_selection']
            response = render(request, 'cookies.html', {
                'form': form,
                'cookie_preference_set': True,
                'show_preference_set_confirmation': True
            })
            response.set_cookie('cookie_preferences', cookie_value)
        else:
            response = render(request, 'cookies.html', {
                'form': form,
                'cookie_preference_set': False
            })

        return response
