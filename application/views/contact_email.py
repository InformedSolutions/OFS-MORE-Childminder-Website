"""
Method returning the template for the Your login and contact details:
email page (for a given application) and navigating to the Your login
and contact details: phone number page when successfully completed; business logic
is applied to either create or update the associated User_Details record;
the page redirects `the applicant to the login page if they have previously applied
"""

import time
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..forms import ContactEmailForm
from ..models import Application, UserDetails
from ..middleware import CustomAuthenticationHandler

from .. import magic_link
from ..business_logic import login_contact_logic, reset_declaration

def contact_email(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: email template
    """

    current_date = datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = ContactEmailForm(id=app_id)
        form.check_flag()
        application = Application.objects.get(pk=app_id)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = ContactEmailForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.objects.get(pk=app_id)

        if form.is_valid():

            # Send login e-mail link if applicant has previously applied
            email = form.cleaned_data['email_address']

            if UserDetails.objects.filter(email=email).exists():

                acc = UserDetails.objects.get(email=email)
                domain = request.META.get('HTTP_REFERER', "")
                domain = domain[:-54]
                link = magic_link.generate_random(12, "link")
                expiry = int(time.time())
                acc.email_expiry_date = expiry
                acc.magic_link_email = link
                acc.save()
                magic_link.magic_link_email(email, domain + 'validate/' + link)

                return HttpResponseRedirect(reverse('Email-Sent-Template') + '?id=' + app_id)

            else:

                # Create or update User_Details record
                user_details_record = login_contact_logic(app_id, form)
                user_details_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                response = HttpResponseRedirect(reverse('Contact-Phone-View') + '?id=' + app_id)

                # Create session and issue cookie to user
                CustomAuthenticationHandler.create_session(response, application.login_id.email)

                return response

        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'contact-email.html', variables)
