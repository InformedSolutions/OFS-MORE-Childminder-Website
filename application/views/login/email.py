"""
Method returning the template for the Your login and contact details:
email page (for a given application) and navigating to the Your login
and contact details: phone number page when successfully completed; business logic
is applied to either create or update the associated User_Details record;
the page redirects `the applicant to the login page if they have previously applied
"""

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ...forms import ContactEmailForm
from ...models import UserDetails


def check_email(request):
    return render(request,'email-sent.html')


def new_email(request):

    if request.method == 'GET':
        variables = {
            'form': ContactEmailForm()
        }

        return render(request, 'contact-email.html', variables)
    else:
        return email_page(request, 'new')


def existing_email(request):
    if request.method == 'GET':
        variables = {
            'form': ContactEmailForm()
        }

        return render(request, 'contact-email.html', variables)
    else:
        return email_page(request, 'existing')


def email_page(request, page):
    """
    :param page: whether the request is for a new application or an existing one
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: email template
    """
    if request.method == 'POST':

        form = ContactEmailForm(request.POST)

        if form.is_valid():

            # Send login e-mail link if applicant has previously applied
            email = form.cleaned_data['email_address']
            if UserDetails.objects.filter(email=email).exists():
                # Send Magic Link Email
                return HttpResponseRedirect(reverse('Existing-Email-Sent'))
            elif page == 'new':
                # Create Application & User Details
                # Send Magic Link Email
                return HttpResponseRedirect(reverse('New-Email-Sent'))
            elif page == 'existing':
                return HttpResponseRedirect(reverse('Existing-Email-Sent'))

        # If the form has validation errors
        return render(request, 'contact-email.html', {'form':form})


