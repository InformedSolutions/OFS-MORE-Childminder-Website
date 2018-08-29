import time

from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from timeline_logger.models import TimelineLog

from ...views import magic_link
from ...utils import test_notify, build_url
from ...forms import ContactEmailForm
from ...models import UserDetails, Application, ApplicantName


class NewUserSignInView(View):
    """
    This class handles the requests for a new user signing in.
    """
    def get(self, request):
        return render(request, 'contact-email.html', context={'form': ContactEmailForm()})

    def post(self, request):
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            if not test_notify():
                return HttpResponseRedirect(reverse('Service-Down'))

            email = form.cleaned_data['email_address']

            if UserDetails.objects.filter(email=email).exists():
                send_magic_link(email)  # acc created here so conditional must be made before then.
                return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)
            else:
                acc = create_new_app()  # Create new account here such that send_magic_link sends correct email.
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
        return render(request, 'existing-application.html', context={'form': ContactEmailForm()})

    def post(self, request):
        form = ContactEmailForm(request.POST)
        if form.is_valid():
            if not test_notify():
                return HttpResponseRedirect(reverse('Service-Down'))

            email = form.cleaned_data['email_address']
            send_magic_link(email)
            return HttpResponseRedirect(reverse('Existing-Email-Sent') + '?email=' + email)

        return render(request, 'existing-application.html', {'form': form})


class UpdateEmailView(View):
    """
    This class handles the requests for an existing user updating their email address.
    """
    def get(self, request):
        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        form = ContactEmailForm(id=app_id)
        form.field_list = ['email_address']
        form.pk = UserDetails.objects.get(application_id=application).login_id
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        application = Application.objects.get(pk=app_id)

        return self.render_update_email_template(request, form=form, application=application)

    def post(self, request):
        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        acc = UserDetails.objects.get(application_id=app_id)
        form = ContactEmailForm(request.POST, id=app_id)
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
                # Send an email to the new email adddress, with the account's ID in the link.
                update_magic_link(email, app_id)
                redirect_url = build_url('Update-Email-Sent', get={'email': email, 'id': app_id})
                return HttpResponseRedirect(redirect_url)
        else:

            return self.render_update_email_template(request, form=form, application=application)

    def render_update_email_template(self, request, form, application):

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application.application_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'update-email.html', variables)


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
        'change_email': False
    }

    return render(request, 'email-sent.html', variables)


def login_email_link_resent(request):
    """
    Resend email page
    :param request: Http request
    :return: Http response
    """
    email = request.GET['email']

    if len(email) > 0:
            send_magic_link(email)  # Resend magic link

    return render(request, 'resend-email.html', context={'email': email})


def update_email_link_sent(request):
    """
    :param request:
    :return:
    """
    email = request.GET['email']
    id = request.GET.get('id')

    # Build url with app_id so that update_email_link_resent may use it, if 'resend email' clicked.
    resend_url = build_url('Update-Email-Resent', get={'email': email, 'id': id})

    variables = {
        'email': email,
        'resend_url': resend_url,
        'change_email': True
    }
    return render(request, 'email-sent.html', variables)


def update_email_link_resent(request):
    """
    :param request:
    :return:
    """
    email = request.GET['email']
    id = request.GET['id']
    update_magic_link(email=email, app_id=id)

    return render(request, 'resend-email.html', context={'email': email})


def send_magic_link(email):
    """
    Send email containing link to access an account.
    :param email: email address for the account to be accessed.
    """
    try:
        acc = UserDetails.objects.get(email=email)
        email_func = magic_link.magic_link_confirmation_email

    except ObjectDoesNotExist:  # if acc doesn't exist, create one and send corresponding email.
        acc = create_new_app()
        acc.email = email
        email_func = magic_link.magic_link_non_existent_email

    link = create_account_magic_link(account=acc)  # acc.save() called in here.
    email_func(email, str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + link)


def update_magic_link(email, app_id):
    """
    Send email containing link to change an account's email.

    Pass email to magic_link_update_email() as query string for magic_link.validate_url() to use in changing account's
    email address.
    :param email: The new email address for the account.
    :param app_id: ID for the account whose email is to be changed.
    """
    if UserDetails.objects.filter(application_id=app_id).exists():
        acc = UserDetails.objects.get(application_id=app_id)
        link = create_account_magic_link(account=acc)

        try:
            first_name = ApplicantName.objects.get(application_id=app_id).first_name
        except ObjectDoesNotExist:
            first_name = 'applicant'

        full_link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + link + '?email=' + email
        magic_link.magic_link_update_email(email, first_name, full_link)


def create_account_magic_link(account):
    link = magic_link.generate_random(12, "link")
    expiry = int(time.time())
    account.email_expiry_date = expiry
    account.magic_link_email = link
    account.save()
    return link


def create_new_app():
    application = Application.objects.create(
        application_type='CHILDMINDER',
        application_status='DRAFTING',
        cygnum_urn='',
        login_details_status='NOT_STARTED',
        personal_details_status='NOT_STARTED',
        childcare_type_status='NOT_STARTED',
        first_aid_training_status='NOT_STARTED',
        childcare_training_status='NOT_STARTED',
        criminal_record_check_status='NOT_STARTED',
        health_status='NOT_STARTED',
        references_status='NOT_STARTED',
        people_in_home_status='NOT_STARTED',
        declarations_status='NOT_STARTED',
        date_created=timezone.now(),
        date_updated=timezone.now(),
        date_accepted=None,
        application_reference=None
    )
    user = UserDetails.objects.create(application_id=application)

    TimelineLog.objects.create(
        content_object=application,
        user=None,
        template='timeline_logger/application_action.txt',
        extra_data={'user_type': 'applicant', 'action': 'created by', 'entity': 'application'}
    )

    return user

