""""
Method for returning the template for the Cookie Policy page
"""

from django.shortcuts import render

from ..forms import AnalyticsCookieSelection


def cookie_policy(request):
    """
    Method returning the template for the cookies page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered cookies template
    """
    if request.method == 'GET':
        previous_url = request.GET["url"]
        # Set default form value if preferences are already set
        initial_form_state = None
        if 'cookie_preferences' in request.COOKIES:
            preference = request.COOKIES['cookie_preferences']
            initial_form_state = {'cookie_selection': preference}

        form = AnalyticsCookieSelection(initial=initial_form_state)
        cookie_preference_set = 'cookie_preferences' in request.COOKIES
        context = {
            'form': form,
            'cookie_preference_set': cookie_preference_set,
            'previous_url': previous_url
        }

        return render(request, 'cookies.html', context)

    elif request.method == 'POST':
        previous_url = request.POST["url"]
        # Set cookie based on what the user put in the form
        form = AnalyticsCookieSelection(request.POST)
        if form.is_valid():
            cookie_value = form.cleaned_data['cookie_selection']
            response = render(request, 'cookies.html', {
                'form': form,
                'cookie_preference_set': True,
                'show_preference_set_confirmation': True,
                'previous_url': previous_url
            })
            response.set_cookie('cookie_preferences', cookie_value)
            response.set_cookie('seen_cookie_message', 'yes')
        else:
            response = render(request, 'cookies.html', {
                'form': form,
                'cookie_preference_set': False,
                'previous_url': previous_url
            })

        return response
