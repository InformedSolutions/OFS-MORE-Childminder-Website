import collections
import datetime

from django.utils import timezone

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..table_util import create_tables, Table, submit_link_setter
from ..summary_page_data import contact_info_link_dict, contact_info_name_dict
from .. import status
from ..business_logic import reset_declaration, login_contact_logic_add_phone, login_contact_logic_mobile_phone
from ..forms import ContactAddPhoneForm, ContactMobilePhoneForm, ContactSummaryForm
from ..models import Application, UserDetails


def contact_phone(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: phone template
    """

    current_date = timezone.now()
    flag = ''
    if request.method == 'GET':
        app_id = request.GET["id"]
        mobile_form = ContactMobilePhoneForm(id=app_id)
        mobile_form.check_flag()
        add_phone_form = ContactAddPhoneForm(id=app_id)
        add_phone_form.check_flag()
        application = Application.get_id(app_id=app_id)
        acc = UserDetails.objects.get(application_id=app_id)
        if len(acc.mobile_number) == 0 and 'f' not in request.GET:
            flag = '&f=1'
            # Update date last accessed when successfully logged in
            application.date_last_accessed = datetime.now()
            application.save()
            return HttpResponseRedirect(reverse('Contact-Phone-View') + '?id=' + app_id + flag)

        if application.application_status == 'FURTHER_INFORMATION':
            mobile_form.error_summary_template_name = 'returned-error-summary.html'
            mobile_form.error_summary_title = 'There was a problem'
            add_phone_form.error_summary_template_name = 'returned-error-summary.html'
            add_phone_form.error_summary_title = 'There was a problem'

        variables = {
            'mobile_form': mobile_form,
            'add_phone_form': add_phone_form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }
        return render(request, 'contact-phone.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]

        mobile_form = ContactMobilePhoneForm(request.POST, id=app_id)
        mobile_form.remove_flag()
        add_phone_form = ContactAddPhoneForm(request.POST, id=app_id)
        add_phone_form.remove_flag()
        application = Application.get_id(app_id=app_id)
        acc = UserDetails.objects.get(application_id=app_id)
        if len(acc.mobile_number) == 0 and 'f' not in request.GET:
            flag = '&f=1'

        # Validate both forms (sets of checkboxes)
        if mobile_form.is_valid():
            acc = UserDetails.objects.get(application_id=app_id)
            if len(acc.mobile_number) == 0 or 'f' in request.GET:
                flag = '&f=1'
            user_details_record = login_contact_logic_mobile_phone(app_id, mobile_form)
            user_details_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            if add_phone_form.is_valid():

                user_details_record = login_contact_logic_add_phone(app_id, add_phone_form)
                user_details_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)

                return HttpResponseRedirect(reverse('Contact-Summary-View') + '?id=' + app_id + flag)

        else:

            if application.application_status == 'FURTHER_INFORMATION':
                mobile_form.error_summary_template_name = 'returned-error-summary.html'
                mobile_form.error_summary_title = 'There was a problem'
                add_phone_form.error_summary_template_name = 'returned-error-summary.html'
                add_phone_form.error_summary_title = 'There was a problem'

        variables = {
            'mobile_form': mobile_form,
            'add_phone_form': add_phone_form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-phone.html', variables)


def contact_summary(request):
    """
    Method returning the template for the Your login and contact details: summary page (for a given application)
    displaying entered data for this task and navigating to the Type of childcare page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your login and contact details: summary template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        user_details = UserDetails.objects.get(application_id=app_id)
        email = user_details.email
        mobile_number = user_details.mobile_number
        add_phone_number = user_details.add_phone_number

        contact_info_fields = collections.OrderedDict([
            ('email_address', email),
            ('mobile_number', mobile_number),
            ('add_phone_number', add_phone_number)
        ])

        contact_info_table = collections.OrderedDict({
            'table_object': Table([user_details.pk]),
            'fields': contact_info_fields,
            'title': '',
            'error_summary_title': 'There was a problem'
        })

        table_list = create_tables([contact_info_table], contact_info_name_dict, contact_info_link_dict)

        form = ContactSummaryForm()

        variables = {
            'form': form,
            'application_id': app_id,
            'table_list': table_list,
            'page_title': 'Check your answers: your sign in details',
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        variables = submit_link_setter(variables, table_list, 'login_details', app_id)

        if application.childcare_type_status == 'COMPLETED' or application.childcare_type_status == 'FLAGGED':
            variables['submit_link'] = reverse('Task-List-View')

        elif application.childcare_type_status != 'COMPLETED':

            variables['submit_link'] = reverse('Type-Of-Childcare-Guidance-View')

        if 'f' in request.GET:
            return render(request, 'no-link-summary-template.html', variables)
        else:
            return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)

        status.update(app_id, 'login_details_status', 'COMPLETED')

        if application.childcare_type_status == 'COMPLETED' or application.childcare_type_status == 'FLAGGED':

            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + app_id)

        elif application.childcare_type_status != 'COMPLETED':

            return HttpResponseRedirect(reverse('Type-Of-Childcare-Guidance-View') + '?id=' + app_id)

        variables = {
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-summary.html', variables)

