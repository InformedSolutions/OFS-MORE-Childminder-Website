"""
Method returning the template for the Your login and contact details:
email page (for a given application) and navigating to the Your login
and contact details: phone number page when successfully completed; business logic
is applied to either create or update the associated User_Details record;
the page redirects `the applicant to the login page if they have previously applied
"""
import collections
import time
from django.utils import timezone

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..table_util import create_tables, Table, submit_link_setter
from ..summary_page_data import contact_info_link_dict, contact_info_name_dict
from .. import magic_link, status
from ..business_logic import login_contact_logic, reset_declaration, login_contact_logic_phone
from ..forms import ContactEmailForm, ContactPhoneForm, ContactSummaryForm
from ..middleware import CustomAuthenticationHandler
from ..models import Application, UserDetails


def contact_email(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: email template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = ContactEmailForm(id=app_id)
        form.check_flag()
        application = Application.objects.get(pk=app_id)

        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-email.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = ContactEmailForm(request.POST, id=app_id)
        form.remove_flag()

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
                application = Application.objects.get(pk=app_id)
                user_details_record = login_contact_logic(app_id, form)
                user_details_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                if application.login_details_status == 'COMPLETED':
                    response = HttpResponseRedirect(reverse('Contact-Summary-View') + '?id=' + app_id)
                else:
                    response = HttpResponseRedirect(reverse('Contact-Phone-View') + '?id=' + app_id)
                    # Create session and issue cookie to user
                    CustomAuthenticationHandler.create_session(response, user_details_record.email)

                return response

            return render(request, 'contact-email.html', variables)


"""
Method returning the template for the Your login and contact details: phone number page (for a given application)
and navigating to the Your login and contact details: question page when successfully completed
"""


def contact_phone(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: phone template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = ContactPhoneForm(id=app_id)
        form.check_flag()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-phone.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = ContactPhoneForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        if form.is_valid():
            # Update User_Details record
            user_details_record = login_contact_logic_phone(app_id, form)
            user_details_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Question-View') + '?id=' + app_id)

        else:
            variables = {
                'form': form,
                'application_id': app_id,
                'login_details_status': application.login_details_status,
                'childcare_type_status': application.childcare_type_status
            }

            return render(request, 'contact-phone.html', variables)


"""
Method returning the template for the Your login and contact details: summary page (for a given application)
displaying entered data for this task and navigating to the Type of childcare page when successfully completed
"""


def contact_summary(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        login_id = application.login_id.login_id
        user_details = UserDetails.objects.get(login_id=login_id)
        email = user_details.email
        mobile_number = user_details.mobile_number
        add_phone_number = user_details.add_phone_number
        security_question = user_details.security_question
        security_answer = user_details.security_answer

        if application.login_details_status != 'COMPLETED':
            status.update(app_id, 'login_details_status', 'COMPLETED')

        contact_info_fields = collections.OrderedDict([
            ('email_address', email),
            ('mobile_number', mobile_number),
            ('add_phone_number', add_phone_number),
            ('security_question', security_question),
            ('security_answer', security_answer),
        ])

        contact_info_table = collections.OrderedDict({
            'table_object': Table([user_details.pk]),
            'fields': contact_info_fields,
            'title': 'Your login details',
            'error_summary_title': 'There is something wrong with your login details'
        })

        table_list = create_tables([contact_info_table], contact_info_name_dict, contact_info_link_dict)

        form = ContactSummaryForm()
        variables = {
            'form': form,
            'application_id': app_id,
            'table_list': table_list,
            'page_title': 'Check your answers: your login details',
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        variables = submit_link_setter(variables, table_list, 'login_details', app_id)

        variables['submit_link'] = reverse('Type-Of-Childcare-Guidance-View')

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = ContactSummaryForm(request.POST)
        application = Application.objects.get(pk=app_id)

        if form.is_valid():
            status.update(app_id, 'login_details_status', 'COMPLETED')
            return HttpResponseRedirect(reverse('Type-Of-Childcare-Guidance-View') + '?id=' + app_id)

        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-summary.html', variables)
