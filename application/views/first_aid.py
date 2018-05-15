import collections

from django.utils import timezone
from datetime import date
import calendar

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .. import status
from ..table_util import Table, create_tables, submit_link_setter
from ..summary_page_data import first_aid_name_dict, first_aid_link_dict
from ..business_logic import (first_aid_logic,
                              reset_declaration)
from ..forms import (FirstAidTrainingDeclarationForm,
                     FirstAidTrainingDetailsForm,
                     FirstAidTrainingGuidanceForm,
                     FirstAidTrainingRenewForm,
                     FirstAidTrainingSummaryForm,
                     FirstAidTrainingTrainingForm)
from ..models import (Application,
                      FirstAidTraining)


# This view has yet to be refactored

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
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingGuidanceForm(request.POST)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.first_aid_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/details?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
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
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
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
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/update?id=' + application_id_local)

            # If certificate not out-of-date, update  First_Aid_Training record.
            first_aid_training_record = first_aid_logic(application_id_local, form)
            first_aid_training_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            if 2.5 <= certificate_age < 3:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/renew?id=' + application_id_local)
            else:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/certificate?id=' + application_id_local)

        else:
            form.error_summary_title = 'There was a problem with your course details'
            variables = {
                'form': form,
                'application_id': application_id_local
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
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-declaration.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingDeclarationForm(request.POST)
        if form.is_valid():
            status.update(application_id_local,
                          'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
            variables = {
                'form': form,
                'application_id': application_id_local
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
            status.update(application_id_local, 'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
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
            status.update(application_id_local,
                          'first_aid_training_status', 'NOT_STARTED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list/?id=' + application_id_local)
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
            ('course_date', ' '.join([str(first_aid_record.course_day), calendar.month_name[first_aid_record.course_month], str(first_aid_record.course_year)]))
        ])

        first_aid_table = collections.OrderedDict({
            'table_object': Table([first_aid_record.pk]),
            'fields': first_aid_fields,
            'title': '',
            'error_summary_title': 'There is something wrong with your first aid training'
        })

        table_list = create_tables([first_aid_table], first_aid_name_dict, first_aid_link_dict)

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
        form = FirstAidTrainingSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-summary.html', variables)
