from django.utils import timezone

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..summary_page_data import dbs_summary_dict
from ..table_util import table_creator, submit_link_setter
from .. import status
from ..business_logic import (dbs_check_logic,
                              reset_declaration)
from ..forms import (DBSCheckDBSDetailsForm,
                     DBSCheckGuidanceForm,
                     DBSCheckSummaryForm,
                     DBSCheckUploadDBSForm)
from ..models import (Application,
                      CriminalRecordCheck)


def dbs_check_guidance(request):
    """
    Method returning the template for the Your criminal record (DBS) check: guidance page (for a given application)
    and navigating to the Your criminal record (DBS) check: details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DBSCheckGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local,
                              'criminal_record_check_status', 'IN_PROGRESS')
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/criminal-record/your-details?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-guidance.html', variables)


def dbs_check_dbs_details(request):
    """
    Method returning the template for the Your criminal record (DBS) check: details page (for a given application)
    and navigating to the Your criminal record (DBS) check: upload DBS or summary page when successfully completed;
    business logic is applied to either create or update the associated Criminal_Record_Check record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckDBSDetailsForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-dbs-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'criminal_record_check_status', 'IN_PROGRESS')

        form = DBSCheckDBSDetailsForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update Criminal_Record_Check record
            dbs_check_record = dbs_check_logic(application_id_local, form)
            dbs_check_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            cautions_convictions = form.cleaned_data['convictions']
            if cautions_convictions == 'True':
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/criminal-record/post-certificate?id=' + application_id_local)
            elif cautions_convictions == 'False':
                if application.criminal_record_check_status != 'COMPLETED':
                    status.update(application_id_local,
                                  'criminal_record_check_status', 'COMPLETED')
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/criminal-record/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with your DBS details'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-dbs-details.html', variables)


def dbs_check_upload_dbs(request):
    """
    Method returning the template for the Your criminal record (DBS) check: upload DBS page (for a given application)
    and navigating to the Your criminal record (DBS) check: summary page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: upload DBS template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckUploadDBSForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-upload-dbs.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DBSCheckUploadDBSForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            declare = form.cleaned_data['declaration']
            dbs_check_record = CriminalRecordCheck.objects.get(
                application_id=application_id_local)
            dbs_check_record.send_certificate_declare = declare
            dbs_check_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local,
                              'criminal_record_check_status', 'COMPLETED')
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/criminal-record/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-upload-dbs.html', variables)


def dbs_check_summary(request):
    """
    Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
    """

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
        object_list = [[criminal_record_check]]

        table_list = table_creator(object_list, dbs_summary_dict['display_names'], dbs_summary_dict['data_names'],
                                   dbs_summary_dict['table_names'], dbs_summary_dict['table_error_names'],
                                   dbs_summary_dict['back_url_names'])

        form = DBSCheckSummaryForm()

        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status,
            'table_list': table_list,
            'page_title': dbs_summary_dict['page_title']
        }
        variables = submit_link_setter(variables, table_list, 'criminal_record_check', application_id_local)

        return render(request, 'generic-summary-template.html', variables)
    if request.method == 'POST':

        application_id_local = request.POST["id"]
        form = DBSCheckSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-summary.html', variables)
