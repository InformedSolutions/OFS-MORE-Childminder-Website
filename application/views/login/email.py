"""
Method returning the template for the Your login and contact details:
email page (for a given application) and navigating to the Your login
and contact details: phone number page when successfully completed; business logic
is applied to either create or update the associated User_Details record;
the page redirects `the applicant to the login page if they have previously applied
"""

import time
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, request
from django.shortcuts import render
from timeline_logger.models import TimelineLog

from application import magic_link
from ...utils import test_notify
from ...forms import ContactEmailForm
from ...models import UserDetails, Application


def check_email(request):
    return render(request, 'email-sent.html')


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
            if not test_notify():
                return HttpResponseRedirect(reverse('Service-Down'))

            # Send login e-mail link if applicant has previously applied
            email = form.cleaned_data['email_address']
            if UserDetails.objects.filter(email=email).exists():
                send_magic_link(request, email)
                return HttpResponseRedirect(reverse('Existing-Email-Sent'))
            elif page == 'new':
                # Create Application & User Details
                acc = create_new_app()
                acc.email = email
                acc.save()
                send_magic_link(request, email)
                return HttpResponseRedirect(reverse('New-Email-Sent'))
            elif page == 'existing':
                return HttpResponseRedirect(reverse('Existing-Email-Sent'))

            # If the form has validation errors
            return render(request, 'contact-email.html', {'form': form})


def send_magic_link(request, email):
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


def create_new_app():
    application = Application.objects.create(
        application_type='CHILDMINDER',
        # login_id=user,
        application_status='DRAFTING',
        cygnum_urn='',
        login_details_status='NOT_STARTED',
        personal_details_status='NOT_STARTED',
        childcare_type_status='NOT_STARTED',
        first_aid_training_status='NOT_STARTED',
        eyfs_training_status='COMPLETED',
        criminal_record_check_status='NOT_STARTED',
        health_status='NOT_STARTED',
        references_status='NOT_STARTED',
        people_in_home_status='NOT_STARTED',
        declarations_status='NOT_STARTED',
        date_created=timezone.now(),
        date_updated=timezone.now(),
        date_accepted=None,
        order_code=None
    )
    user = UserDetails.objects.create(application_id=application)

    TimelineLog.objects.create(
        content_object=application,
        user=None,
        template='timeline_logger/application_action.txt',
        extra_data={'user_type': 'applicant', 'action': 'created', 'entity': 'application'}
    )

    return user
