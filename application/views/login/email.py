"""
Method returning the template for the Your login and contact details:
email page (for a given application) and navigating to the Your login
and contact details: phone number page when successfully completed; business logic
is applied to either create or update the associated User_Details record;
the page redirects `the applicant to the login page if they have previously applied
"""
import time

from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from timeline_logger.models import TimelineLog

from application import magic_link
from ...utils import test_notify
from ...forms import ContactEmailForm
from ...models import UserDetails, Application

def update_email(request):
    """
    This method returns a page to update your email address
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: email template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = ContactEmailForm()
        form.check_flag()
        application = Application.objects.get(pk=app_id)

        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'update-email.html', variables)

    if request.method == 'POST':
        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        acc = UserDetails.objects.get(application_id=app_id)
        form = ContactEmailForm(request.POST)
        form.remove_flag()

        if form.is_valid():
            # Send login e-mail link if applicant has previously applied
            email = form.cleaned_data['email_address']
            if acc.email == email:
                return HttpResponseRedirect(reverse('Contact-Summary-View') + '?id=' + app_id)
            elif UserDetails.objects.filter(email=email).exists():
                return HttpResponseRedirect(reverse('Update-Email-Sent') + '?email=')
            else:
                # Update User_Details record
                update_magic_link(email, app_id)
                return HttpResponseRedirect(reverse('Update-Email-Sent') + '?email=' + email)

            return render(request, 'update-email.html', {'form': form, 'application_id': app_id})
        else:
            variables = {
                'form': form,
                'application_id': app_id,
                'login_details_status': application.login_details_status,
                'childcare_type_status': application.childcare_type_status
            }

            return render(request, 'update-email.html', variables)


def email_resent(request):
    """
    Resend email page
    :param request: Http request
    :return: Http responsne
    """
    email = request.GET['email']
    if len(email) > 0:
        # Resend magic link
        send_magic_link(email)
    variables = {
        'email': email
    }
    return render(request, 'resend-email.html', variables)


def check_email(request):
    """
    Check email page
    :param request: Http request
    :return: Http response
    """
    email = request.GET['email']
    variables = {
        'email': email
    }
    return render(request, 'email-sent.html', variables)


def new_email(request):
    """
    New application sign up form (enter email)
    :param request: Http request
    :return: Http response
    """
    if request.method == 'GET':
        variables = {
            'form': ContactEmailForm()
        }

        return render(request, 'contact-email.html', variables)
    else:
        return email_page(request, 'new')


def existing_email(request):
    """
    Existing user sign in form (enter email)
    :param request: Http request
    :return: Http response
    """
    if request.method == 'GET':
        variables = {
            'form': ContactEmailForm()
        }

        return render(request, 'existing-application.html', variables)
    else:
        return email_page(request, 'existing')


def email_page(request, page):
    """
    This is the functionality behind the new/existing user sign in/up pages
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
                send_magic_link(email)
                return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)

            elif page == 'new':
                # Create Application & User Details
                acc = create_new_app()
                acc.email = email
                acc.save()
                send_magic_link(email)
                return HttpResponseRedirect(reverse('New-Email-Sent') + '?email=' + email)

            elif page == 'existing':
                return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)

            # If the form has validation errors
            return render(request, 'contact-email.html', {'form': form})

        elif page == 'existing':
            return render(request, 'existing-application.html', {'form': form})
        elif page == 'new':
            return render(request, 'contact-email.html', {'form': form})


def send_magic_link(email):
    """
    Send magic link
    :param request:
    :param email:
    :return:
    """
    if UserDetails.objects.filter(email=email).exists():
        acc = UserDetails.objects.get(email=email)
        link = magic_link.generate_random(12, "link")
        expiry = int(time.time())
        acc.email_expiry_date = expiry
        acc.magic_link_email = link
        acc.save()
        # Note url has been updated to use the domain set in the settings
        magic_link.magic_link_email(email, str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + link)


def update_magic_link(email, app_id):
    """
    Send magic link
    :param request:
    :param email:
    :return:
    """
    if UserDetails.objects.filter(application_id=app_id).exists():
        acc = UserDetails.objects.get(application_id=app_id)
        link = magic_link.generate_random(12, "link")
        expiry = int(time.time())
        acc.email_expiry_date = expiry
        acc.magic_link_email = link
        acc.save()
        # Note url has been updated to use the domain set in the settings
        magic_link.magic_link_email(email,
                                    str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + link + '?email=' + email)


def create_new_app():
    application = Application.objects.create(
        application_type='CHILDMINDER',
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


