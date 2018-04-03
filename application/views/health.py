import collections

from django.utils import timezone

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .. import status
from ..table_util import Table, create_tables, submit_link_setter
from ..summary_page_data import health_link_dict, health_name_dict
from ..business_logic import (health_check_logic,
                              reset_declaration)
from ..forms import (HealthBookletForm,
                     HealthIntroForm)
from ..models import (Application,
                      HealthDeclarationBooklet)


def health_intro(request):
    """
    Method returning the template for the Your health: intro page (for a given application)
    and navigating to the Your health: intro page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: intro template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = HealthIntroForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }
        return render(request, 'health-intro.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthIntroForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.health_status != 'COMPLETED':
                status.update(application_id_local,
                              'health_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/booklet?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-intro.html', variables)


def health_booklet(request):
    """
    Method returning the template for the Your health: booklet page (for a given application)
    and navigating to the Your health: answers page when successfully completed;
    business logic is applied to either create or update the associated Health_Declaration_Booklet record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: booklet template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = HealthBookletForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }
        return render(request, 'health-booklet.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthBookletForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update Health_Declaration_Booklet record
            hdb_record = health_check_logic(application_id_local, form)
            hdb_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.health_status != 'COMPLETED':
                status.update(application_id_local,
                              'health_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with this page.'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-booklet.html', variables)


def health_check_answers(request):
    """
    Method returning the template for the Your health: answers page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: answers template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        health_record = HealthDeclarationBooklet.objects.get(
            application_id=application_id_local)
        send_hdb_declare = health_record.send_hdb_declare
        form = HealthBookletForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)

        health_fields = collections.OrderedDict([('health_submission_consent', send_hdb_declare)])

        health_table = collections.OrderedDict({
            'table_object': Table([health_record.pk]),
            'fields': health_fields,
            'title': 'Your health',
            'error_summary_title': 'There is something wrong with your health'
        })

        table_list = create_tables([health_table], health_name_dict, health_link_dict)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'health_status': application.health_status,
            'page_title': 'Check your answers: your health'
        }
        variables = submit_link_setter(variables, table_list, 'health', application_id_local)

        return render(request, 'generic-summary-template.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthBookletForm(request.POST, id=application_id_local)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-check-answers.html', variables)
