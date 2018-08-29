import collections

from django.utils import timezone
from datetime import date

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from .. import status
from ..table_util import Table, create_tables, submit_link_setter
from ..summary_page_data import first_aid_name_dict, first_aid_link_dict, first_aid_change_link_description_dict
from ..business_logic import (childcare_register_type,
                              first_aid_logic,
                              reset_declaration)
from ..forms import (FirstAidTrainingDeclarationForm,
                     FirstAidTrainingDetailsForm,
                     FirstAidTrainingGuidanceForm,
                     FirstAidTrainingRenewForm,
                     FirstAidTrainingSummaryForm,
                     FirstAidTrainingTrainingForm)
from ..models import (Application,
                      FirstAidTraining)


def first_aid_training_guidance(request):
    """
    Method returning the template for the First aid training: guidance page (for a given application)
    and navigating to the First aid training: details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingGuidanceForm()
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status,
            'register': childcare_register_type(application_id_local)
        }
        return render(request, 'first-aid-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingGuidanceForm(request.POST)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.first_aid_training_status != 'COMPLETED':
                status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('First-Aid-Training-Details-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'register': childcare_register_type(application_id_local)
            }
            return render(request, 'first-aid-training-guidance.html', variables)


def first_aid_training_details(request):
    """
    Method returning the template for the First aid training: details page (for a given application)
    and navigating to the First aid training: renew, declaration or training page depending on
    the age of the first aid training certificate when successfully completed;
    business logic is applied to either create or update the associated First_Aid_Training record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: details template
    """
    current_date = timezone.now()

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDetailsForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status,
            'register': childcare_register_type(application_id_local)
        }
        return render(request, 'first-aid-details.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
        form = FirstAidTrainingDetailsForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)

        if form.is_valid():
            # Calculate certificate age and determine which page to navigate to.
            certif_day, certif_month, certif_year = form.cleaned_data.get('course_date')
            certificate_date = date(certif_year, certif_month, certif_day)
            today = date.today()
            certificate_date_difference = today - certificate_date
            certificate_age = certificate_date_difference.days / 365  # Integer division can return float in Python 3.

            if certificate_age >= 3:
                return HttpResponseRedirect(reverse('First-Aid-Training-Training-View') + '?id=' + application_id_local)

            # If certificate not out-of-date, update  First_Aid_Training record.
            first_aid_training_record = first_aid_logic(application_id_local, form)
            first_aid_training_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            if 2.5 <= certificate_age < 3:
                return HttpResponseRedirect(reverse('First-Aid-Training-Renew-View') + '?id=' + application_id_local)
            else:
                return HttpResponseRedirect(
                    reverse('First-Aid-Training-Declaration-View') + '?id=' + application_id_local)

        else:
            form.error_summary_title = 'There was a problem with your course details'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local,
                'register': childcare_register_type(application_id_local)
            }
            return render(request, 'first-aid-details.html', variables)


def first_aid_training_declaration(request):
    """
    Method returning the template for the First aid training: declaration page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: declaration template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDeclarationForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status,
            'register': childcare_register_type(application_id_local)
        }
        return render(request, 'first-aid-declaration.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingDeclarationForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('First-Aid-Training-Summary-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'register': childcare_register_type(application_id_local)
            }
            return render(request, 'first-aid-declaration.html', variables)


def first_aid_training_renew(request):
    """
    Method returning the template for the First aid training: renew page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: renew template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingRenewForm()
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-renew.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingRenewForm(request.POST)
        form.remove_flag()
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('First-Aid-Training-Summary-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-renew.html', variables)


def first_aid_training_training(request):
    """
    Method returning the template for the First aid training: training page (for a given application)
    and navigating to the task list
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: training template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingTrainingForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-training.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingTrainingForm(request.POST)
        if form.is_valid():
            status.update(application_id_local, 'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-training.html', variables)


def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_aid_record = FirstAidTraining.objects.get(
            application_id=application_id_local)
        form = FirstAidTrainingSummaryForm()
        application = Application.objects.get(pk=application_id_local)

        first_aid_fields = collections.OrderedDict([
            ('first_aid_training_organisation', first_aid_record.training_organisation),
            ('title_of_training_course', first_aid_record.course_title),
            ('course_date', '/'.join([str(first_aid_record.course_day).zfill(2),
                                      str(first_aid_record.course_month).zfill(2),
                                      str(first_aid_record.course_year)]))
        ])

        first_aid_table = collections.OrderedDict({
            'table_object': Table([first_aid_record.pk]),
            'fields': first_aid_fields,
            'title': '',
            'error_summary_title': 'There was a problem',
        })

        table_list = create_tables([first_aid_table], first_aid_name_dict,
                                   first_aid_link_dict, first_aid_change_link_description_dict)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'page_title': 'Check your answers: first aid training',
            'first_aid_training_status': application.first_aid_training_status
        }

        variables = submit_link_setter(variables, table_list, 'first_aid_training', application_id_local)

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        status.update(application_id_local, 'first_aid_training_status', 'COMPLETED')

        return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
