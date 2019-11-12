"""
Method returning the template for the Type of childcare: guidance page (for a given application) and navigating
to the Type of childcare: childcare ages page when successfully completed
"""
import collections

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..summary_page_data import childcare_type_name_dict, childcare_type_link_dict, childcare_type_change_link_description_dict
from ..table_util import Table, create_tables, submit_link_setter
from .. import status
from ..business_logic import reset_declaration, childcare_type_logic, get_childcare_register_type
from ..forms import TimingOfChildcareGuidanceForm, TimingOfChildcareGroupsForm, TypeOfChildcareRegisterForm, \
    TypeOfChildcareOvernightCareForm
from ..models import Application, ChildcareType


def timing_of_childcare_guidance(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: guidance template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = TimingOfChildcareGuidanceForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_timing_status': application.childcare_timing_status,
            'login_details_status': application.login_details_status,
        }
        if application.childcare_timing_status != 'COMPLETED':
            status.update(app_id, 'childcare_timing_status', 'IN_PROGRESS')

        return render(request, 'childcare-timing-guidance.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TimingOfChildcareGuidanceForm(request.POST)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            if application.childcare_timing_status != 'COMPLETED':
                status.update(app_id, 'childcare_timing_status', 'IN_PROGRESS')

            return HttpResponseRedirect(
                reverse('Timing-Of-Childcare-Groups-View') + '?id=' + app_id)

        variables = {
            'form': form,
            'application_id': app_id
        }
        return render(request, 'childcare-timing-guidance.html', variables)


def timing_of_childcare_groups(request):
    """
    Method returning the template for the Type of childcare: age groups page (for a given application) and navigating
    to the task list when successfully completed; business logic is applied to either create or update the
    associated Childcare_Type record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: age groups template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = TimingOfChildcareGroupsForm(id=app_id)
        application = Application.get_id(app_id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_timing_status': application.childcare_timing_status,
            'login_details_status': application.login_details_status,
        }

        return render(request, 'childcare-timing-groups.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TimingOfChildcareGroupsForm(request.POST, id=app_id)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            # Create or update Childcare_Type record
            childcare_timing_record = childcare_timing_logic(app_id, form)

            # Check to see if the type of childcare training has been changed
            if ChildcareType.objects.filter(application_id=app_id).count() > 0:
                existing_record = ChildcareType.objects.get(application_id=app_id)

                if existing_record.zero_to_five != childcare_type_record.zero_to_five or \
                   existing_record.eight_plus != childcare_type_record.eight_plus:
                    application.childcare_training_status = 'NOT_STARTED'

            childcare_type_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Type-Of-Childcare-Register-View') + '?id=' + app_id)
        else:

            if application.application_status == 'FURTHER_INFORMATION':

                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'childcare_type_status': application.childcare_type_status
            }
            return render(request, 'childcare-age-groups.html', variables)


def type_of_childcare_register(request):
    """
    Method returning the template for the correct Type of childcare: register page (for a given application)
    and navigating to the task list when successfully confirmed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the correct rendered Type of childcare: register template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = TypeOfChildcareRegisterForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_type_status': application.childcare_type_status,
            'login_details_status': application.login_details_status,
        }

        childcare_register_type, childcare_register_cost = get_childcare_register_type(app_id)

        if childcare_register_type == 'EYR-CR-both':
            return render(request, 'childcare-register-EYR-CR-both.html', variables)
        elif childcare_register_type == 'EYR-CR-compulsory':
            return render(request, 'childcare-register-EYR-CR-compulsory.html', variables)
        elif childcare_register_type == 'EYR-CR-voluntary':
            return render(request, 'childcare-register-EYR-CR-voluntary.html', variables)
        elif childcare_register_type == 'EYR':
            return render(request, 'childcare-register-EYR.html', variables)
        elif childcare_register_type == 'CR-compulsory':
            return render(request, 'childcare-register-CR-compulsory.html', variables)
        elif childcare_register_type == 'CR-both':
            return render(request, 'childcare-register-CR-both.html', variables)
        elif childcare_register_type == 'CR-voluntary':
            return render(request, 'childcare-register-CR-voluntary.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        return HttpResponseRedirect(reverse('Type-Of-Childcare-Overnight-Care-View') + '?id=' + app_id)


def overnight_care(request):
    """
    Method for capturing the response supplied on the Overnight care provisioning page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the correct rendered Type of childcare: Overnight care page
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = TypeOfChildcareOvernightCareForm(id=app_id)
        application = Application.get_id(app_id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_type_status': application.childcare_type_status,
            'login_details_status': application.login_details_status,
        }
        return render(request, 'childcare-overnight-care.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TypeOfChildcareOvernightCareForm(request.POST, id=app_id)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            childcare_record = ChildcareType.objects.get(application_id=app_id)
            childcare_record.overnight_care = form.cleaned_data['overnight_care']
            childcare_record.save()

            application.date_updated = current_date
            application.save()

            reset_declaration(application)

        else:

            if application.application_status == 'FURTHER_INFORMATION':

                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'login_details_status': application.login_details_status,
                'childcare_type_status': application.childcare_type_status
            }

            return render(request, 'childcare-overnight-care.html', variables)

        app_id = request.POST["id"]
        return HttpResponseRedirect(reverse('Type-Of-Childcare-Summary-View') + '?id=' + app_id)


def childcare_type_summary(request):
    """
    Method for rendering a summary page for the childcare type task.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the correct rendered Type of childcare summary page
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        childcare_record = ChildcareType.objects.get(application_id=app_id)
        application = Application.objects.get(pk=app_id)

        childcare_age_groups = ''

        if childcare_record.zero_to_five:
            childcare_age_groups += '0 to 5 year olds,'

        if childcare_record.five_to_eight:
            childcare_age_groups += '5 to 7 year olds,'

        if childcare_record.eight_plus:
            childcare_age_groups += '8 years or older'

        # Format response by comma delimiting
        childcare_age_groups = childcare_age_groups.rstrip(',')
        childcare_age_groups = childcare_age_groups.replace(',', ', ')

        childcare_type_fields = collections.OrderedDict([
            ('childcare_age_groups', childcare_age_groups),
            ('overnight_care', childcare_record.overnight_care),
        ])

        childcare_type_table = collections.OrderedDict({
            'table_object': Table([childcare_record.pk]),
            'fields': childcare_type_fields,
            'title': '',
            'error_summary_title': 'There was a problem'
        })

        table_list = create_tables([childcare_type_table], childcare_type_name_dict, childcare_type_link_dict,
                                   childcare_type_change_link_description_dict)

        variables = {
            'application_id': app_id,
            'table_list': table_list,
            'childcare_type_status': application.childcare_type_status,
            'page_title': 'Check your answers: type of childcare'
        }

        variables = submit_link_setter(variables, table_list, 'personal_details', app_id)

        if application.childcare_type_status != 'COMPLETED' or application.childcare_type_status != 'FLAGGED':
            variables['submit_link'] = reverse('Personal-Details-Name-View')

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        status.update(application_id_local, 'childcare_type_status', 'COMPLETED')

        return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)


def local_authority_links(request):
    """
    View to return cancel application if 0-5 childcare_age_groups isn't selected.
    :param request: a request object used to generate the HttpResponse.
    :return: an HttpResponse object with the correct rendered cancel application page.
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        return HttpResponseRedirect(reverse('CR-Cancel-Application') + '?id=' + app_id)

    if request.method == 'POST':

        app_id = request.POST["id"]
        status.update(app_id, 'childcare_type_status', 'COMPLETED')

        if 'Cancel application' in request.POST.keys():
            return HttpResponseRedirect(reverse('CR-Cancel-Application') + '?id=' + app_id)
        else:
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + app_id)

