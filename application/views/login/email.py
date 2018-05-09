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
from django.views import View
from timeline_logger.models import TimelineLog

from application.views import magic_link
from ...utils import test_notify, build_url
from ...forms import ContactEmailForm
from ...models import UserDetails, Application


class NewUserSignInView(View):
    """
    This class handles the requests for a new user signing in.
    """
    def get(self, request):
        variables = {'form': ContactEmailForm()}
        return render(request, 'contact-email.html', variables)

    def post(self, request):
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            if not test_notify():
                return HttpResponseRedirect(reverse('Service-Down'))

            email = form.cleaned_data['email_address']

            if UserDetails.objects.filter(email=email).exists():
                send_magic_link(email)
                return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)
            else:
                acc = create_new_app()
                acc.email = email
                acc.save()
                send_magic_link(email)
                return HttpResponseRedirect(reverse('New-Email-Sent') + '?email=' + email)

        return render(request, 'contact-email.html', {'form': form})


class ExistingUserSignInView(View):
    """
    This class handles the requests for an existing user signing in.
    """
    def get(self, request):
        variables = {'form': ContactEmailForm()}
        return render(request, 'existing-application.html', variables)

    def post(self, request):
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            if not test_notify():
                return HttpResponseRedirect(reverse('Service-Down'))

            email = form.cleaned_data['email_address']

            if UserDetails.objects.filter(email=email).exists():
                send_magic_link(email)

            return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)

        return render(request, 'existing-application.html', {'form': form})


class UpdateEmailView(View):
    """
    This class handles the requests for an existing user updating their email address.
    """
    def get(self, request):
        app_id = request.GET["id"]
        form = ContactEmailForm()
        form.check_flag()
        application = Application.objects.get(pk=app_id)

        return self.render_update_email_template(request, form=form, application=application)

    def post(self, request):
        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        acc = UserDetails.objects.get(application_id=app_id)
        form = ContactEmailForm(request.POST)
        form.remove_flag()

        if form.is_valid():
            email = form.cleaned_data['email_address']

            if acc.email == email:
                return HttpResponseRedirect(reverse('Contact-Summary-View') + '?id=' + app_id)

            elif UserDetails.objects.filter(email=email).exists():
                if settings.DEBUG:
                    print ("You will not see an email validation link printed because an account already exists with that email.")
                return HttpResponseRedirect(reverse('Update-Email-Sent') + '?email=' + email)

            else:
                update_magic_link(email, app_id)
                redirect_url = build_url('Update-Email-Sent', get={'email': email, 'id': app_id})
                return HttpResponseRedirect(redirect_url)
        else:
            return self.render_update_email_template(request, form=form, application=application)

    def render_update_email_template(self, request, form, application):
        variables = {
            'form': form,
            'application_id': application.application_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'update-email.html', variables)


def update_email_link_resent(request):
    """
    :param request:
    :return:
    """
    email = request.GET['email']
    id = request.GET['id']
    update_magic_link(email=email, app_id=id)
    variables = {
        'email': email
    }
    return render(request, 'resend-email.html', variables)


def update_email_link_sent(request):
    """
    :param request:
    :return:
    """
    email = request.GET['email']
    id = request.GET.get('id')
    resend_url = build_url('Update-Email-Resent', get={'email': email, 'id': id})
    variables = {
        'email': email,
        'resend_url': resend_url,
    }
    return render(request, 'email-sent.html', variables)


def login_email_link_resent(request):
    """
    Resend email page
    :param request: Http request
    :return: Http responsne
    """
    email = request.GET['email']
    if len(email) > 0:
            send_magic_link(email)  # Resend magic link

    variables = {
        'email': email
    }
    return render(request, 'resend-email.html', variables)


def login_email_link_sent(request):
    """
    Check email page
    :param request: Http request
    :return: Http response
    """
    email = request.GET['email']
    resend_url = "/childminder/email-resent/?email=" + email

    variables = {
        'email': email,
        'resend_url': resend_url,
    }

    return render(request, 'email-sent.html', variables)


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


