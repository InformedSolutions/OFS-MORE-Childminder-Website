from django.utils import timezone
import collections

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import View

from ..table_util import Table, create_tables, submit_link_setter
from ..summary_page_data import eyfs_name_dict, eyfs_link_dict, eyfs_change_link_description_dict

from .. import status
from ..business_logic import (eyfs_details_logic,
                              reset_declaration)
from ..forms import (EYFSGuidanceForm,
                     EYFSDetailsForm,
                     EYFSCertificateForm,
                     EYFSSummaryForm)
from ..models import Application, ChildcareType, EYFS


def childcare_register_type(application_id):
    """
    Function to determine the childcare register to which the applicant is applying.
    :param application_id: app_id of the applicant for which the check is being made.
    :return: a string containing the register to which the applicant is applying.
    """
    childcare_type_record = ChildcareType.objects.get(application_id=application_id)
    if not childcare_type_record.zero_to_five and childcare_type_record.five_to_eight:
        return 'childcare_register_only'
    else:
        return 'early_years_register'


class ChildcareTrainingGuidanceView(View):
    template_name = 'childcare-training-guidance.html'

    def get(self, request):
        return render(request, template_name=self.template_name, context=self.get_context_data())

    def post(self, request):
        application_id = request.GET['id']
        application = Application.objects.get(pk=application_id)

        if application.eyfs_training_status != 'COMPLETED':
            status.update(application_id, 'eyfs_training_status', 'IN_PROGRESS')

        register = childcare_register_type(application_id)

        if register == 'childcare_register_only':
            success_url = 'Type-Of-Childcare-Training'
        elif register == 'early_years_register':
            success_url = 'Childcare-Training-Details'

        return HttpResponseRedirect(reverse(success_url) + '?id=' + application_id)

    def get_context_data(self):
        context = dict()
        application_id = self.request.GET['id']
        context['application_id'] = application_id
        context['register'] = childcare_register_type(application_id)
        return context


def eyfs_details(request):
    """
    Method returning the template for the Early Years details: details page (for a given application)
    and navigating to the Early Years details: certificate page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years details: details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSDetailsForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSDetailsForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local, 'eyfs_training_status', 'IN_PROGRESS')
            # Create or update EYFS record
            eyfs_record = eyfs_details_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(reverse('EYFS-Certificate-View') + '?id=' + application_id_local)
        else:

            form.error_summary_title = 'There was a problem with your course details'

            if application.application_status == 'FURTHER_INFORMATION':

                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-details.html', variables)


def eyfs_certificate(request):
    """
    Method returning the template for the Early Years knowledge: certificate page (for a given application)
    and navigating to the Early Years knowledge: question page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: certificate template
    """

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSCertificateForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-certificate.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSCertificateForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local, 'eyfs_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('EYFS-Summary-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-certificate.html', variables)


def eyfs_summary(request):
    """
    Method returning the template for the Early Years knowledge: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early years knowledge: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        form = EYFSSummaryForm()
        application = Application.objects.get(pk=application_id_local)

        eyfs_fields = collections.OrderedDict([
            ('eyfs_course_name', eyfs_record.eyfs_course_name),
            ('eyfs_course_date', '/'.join([str(eyfs_record.eyfs_course_date_day).zfill(2),
                                      str(eyfs_record.eyfs_course_date_month).zfill(2),
                                      str(eyfs_record.eyfs_course_date_year)]))
        ])

        eyfs_table = collections.OrderedDict({
            'table_object': Table([eyfs_record.pk]),
            'fields': eyfs_fields,
            'title': '',
            'error_summary_title': 'There was a problem',
        })

        table_list = create_tables([eyfs_table], eyfs_name_dict,
                                   eyfs_link_dict, eyfs_change_link_description_dict)

        variables = {
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'page_title': 'Check your answers: early years training',
            'eyfs_training_status': application.eyfs_training_status,
        }

        variables = submit_link_setter(variables, table_list, 'eyfs_training', application_id_local)

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        status.update(application_id_local, 'eyfs_training_status', 'COMPLETED')

        return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
