import uuid

from django.utils import timezone

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..summary_page_data import dbs_summary_dict
from ..table_util import table_creator, submit_link_setter
from .. import status
from ..business_logic import (get_criminal_record_check,
                              update_criminal_record_check,
                              dbs_check_logic,
                              reset_declaration)
from ..forms import (DBSLivedAbroadForm,
                     DBSCheckSummaryForm,
                     DBSCheckUploadDBSForm)
from ..models import (Application,
                      CriminalRecordCheck)

from ..utils import build_url

# New Imports TODO: -mop
from django.views.generic.edit import FormView
from django.views.generic import TemplateView

class DBSLivedAbroadView(FormView):
    template_name = 'dbs-lived-abroad.html'
    form_class = DBSLivedAbroadForm
    success_url = ('DBS-Good-Conduct-View', 'DBS-Military-View')

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

        # If no criminal_record_check exists for this user, create one
        if not CriminalRecordCheck.objects.filter(application_id=application_id).exists():
            application = Application.objects.get(application_id=application_id)
            CriminalRecordCheck.objects.create(criminal_record_id=uuid.uuid4(),
                                               application_id=application,
                                               dbs_certificate_number='')

        return super().get_context_data(id=application_id, **kwargs)

    def form_valid(self, form):
        application_id = self.request.GET.get('id')
        lived_abroad_bool = self.request.POST.get('lived_abroad') == 'True'

        successfully_updated = update_criminal_record_check(application_id, 'lived_abroad', lived_abroad_bool)

        return super().form_valid(form)

    def get_success_url(self):
        application_id = self.request.GET.get('id')
        good_conduct_url, military_url = self.success_url

        lived_abroad_bool = get_criminal_record_check(application_id, 'lived_abroad')

        if lived_abroad_bool:
            redirect_url = good_conduct_url
        elif not lived_abroad_bool:
            redirect_url = military_url
        else:
            raise ValueError("Wasn't able to select a url in DBSLivedAbroadView")

        return build_url(redirect_url, get={'id': application_id})

    def get_form_kwargs(self):
        application_id = self.request.GET.get('id')
        kwargs = super().get_form_kwargs()

        kwargs['id'] = application_id

        return kwargs

class DBSTemplateView(TemplateView):
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

        return super().get_context_data(id=application_id, **kwargs)

    def post(self):
        application_id = self.request.GET.get('id')

        return build_url(self.success_url, get={'id': application_id})


class DBSGuidanceView(DBSTemplateView):
    template_name = 'dbs-check-guidance.html'
    success_url = 'DBS-Type-View'


class DBSGoodConductView(DBSTemplateView):
    template_name = 'dbs-good-conduct.html'
    success_url = 'DBS-Email-Certificates-View'


class DBSEmailCertificatesView(DBSTemplateView):
    template_name = 'dbs-email-certificates.html'
    success_url = 'DBS-Email-Certificates-View'


# def dbs_check_dbs_details(request):
#     """
#     Method returning the template for the Your criminal record (DBS) check: details page (for a given application)
#     and navigating to the Your criminal record (DBS) check: upload DBS or summary page when successfully completed;
#     business logic is applied to either create or update the associated Criminal_Record_Check record
#     :param request: a request object used to generate the HttpResponse
#     :return: an HttpResponse object with the rendered Your criminal record (DBS) check: details template
#     """
#     current_date = timezone.now()
#     if request.method == 'GET':
#         application_id_local = request.GET["id"]
#         form = DBSCheckDBSDetailsForm(id=application_id_local)
#         form.check_flag()
#         application = Application.objects.get(pk=application_id_local)
#
#         if application.application_status == 'FURTHER_INFORMATION':
#             form.error_summary_template_name = 'returned-error-summary.html'
#             form.error_summary_title = 'There was a problem'
#
#         variables = {
#             'form': form,
#             'application_id': application_id_local,
#             'criminal_record_check_status': application.criminal_record_check_status
#         }
#         return render(request, 'dbs-check-dbs-details.html', variables)
#     if request.method == 'POST':
#         application_id_local = request.POST["id"]
#
#         # Reset status to in progress as question can change status of overall task
#         status.update(application_id_local, 'criminal_record_check_status', 'IN_PROGRESS')
#
#         form = DBSCheckDBSDetailsForm(request.POST, id=application_id_local)
#         form.remove_flag()
#         application = Application.objects.get(pk=application_id_local)
#         if form.is_valid():
#             # Create or update Criminal_Record_Check record
#             dbs_check_record = dbs_check_logic(application_id_local, form)
#             dbs_check_record.save()
#             application.date_updated = current_date
#             application.save()
#             reset_declaration(application)
#             cautions_convictions = form.cleaned_data['cautions_convictions']
#             if cautions_convictions == 'True':
#                 return HttpResponseRedirect(reverse('DBS-Check-Upload-DBS-View') + '?id=' + application_id_local)
#             elif cautions_convictions == 'False':
#                 return HttpResponseRedirect(reverse('DBS-Check-Summary-View') + '?id=' + application_id_local)
#         else:
#             form.error_summary_title = 'There was a problem with the DBS details'
#
#             if application.application_status == 'FURTHER_INFORMATION':
#                 form.error_summary_template_name = 'returned-error-summary.html'
#                 form.error_summary_title = 'There was a problem'
#
#             variables = {
#                 'form': form,
#                 'application_id': application_id_local
#             }
#             return render(request, 'dbs-check-dbs-details.html', variables)
#
#
# def dbs_check_upload_dbs(request):
#     """
#     Method returning the template for the Your criminal record (DBS) check: upload DBS page (for a given application)
#     and navigating to the Your criminal record (DBS) check: summary page when successfully completed;
#     :param request: a request object used to generate the HttpResponse
#     :return: an HttpResponse object with the rendered Your criminal record (DBS) check: upload DBS template
#     """
#
#     if request.method == 'GET':
#         application_id_local = request.GET["id"]
#         form = DBSCheckUploadDBSForm()
#         application = Application.objects.get(pk=application_id_local)
#
#         if application.application_status == 'FURTHER_INFORMATION':
#             form.error_summary_template_name = 'returned-error-summary.html'
#             form.error_summary_title = 'There was a problem'
#
#         variables = {
#             'form': form,
#             'application_id': application_id_local,
#             'criminal_record_check_status': application.criminal_record_check_status
#         }
#         return render(request, 'dbs-check-upload-dbs.html', variables)
#     if request.method == 'POST':
#         application_id_local = request.POST["id"]
#         form = DBSCheckUploadDBSForm(request.POST)
#         application = Application.objects.get(pk=application_id_local)
#         if form.is_valid():
#             return HttpResponseRedirect(reverse('DBS-Check-Summary-View') + '?id=' + application_id_local)
#         else:
#
#             form.error_summary_title = 'There was a problem'
#
#             if application.application_status == 'FURTHER_INFORMATION':
#                 form.error_summary_template_name = 'returned-error-summary.html'
#                 form.error_summary_title = 'There was a problem'
#
#             variables = {
#                 'form': form,
#                 'application_id': application_id_local
#             }
#             return render(request, 'dbs-check-upload-dbs.html', variables)
#
#
# def dbs_check_summary(request):
#     """
#     Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
#     displaying entered data for this task and navigating to the task list when successfully completed
#     :param request: a request object used to generate the HttpResponse
#     :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
#     """
#
#     if request.method == 'GET':
#         application_id_local = request.GET["id"]
#         criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
#         application = Application.objects.get(pk=application_id_local)
#         object_list = [[criminal_record_check]]
#
#         table_list = table_creator(object_list, dbs_summary_dict['display_names'], dbs_summary_dict['data_names'],
#                                    dbs_summary_dict['table_names'], dbs_summary_dict['table_error_names'],
#                                    dbs_summary_dict['back_url_names'])
#
#         form = DBSCheckSummaryForm()
#
#         if application.application_status == 'FURTHER_INFORMATION':
#             form.error_summary_template_name = 'returned-error-summary.html'
#
#         variables = {
#             'form': form,
#             'application_id': application_id_local,
#             'criminal_record_check_status': application.criminal_record_check_status,
#             'table_list': table_list,
#             'page_title': dbs_summary_dict['page_title']
#         }
#         variables = submit_link_setter(variables, table_list, 'criminal_record_check', application_id_local)
#
#         return render(request, 'generic-summary-template.html', variables)
#
#     if request.method == 'POST':
#
#         application_id_local = request.POST["id"]
#         status.update(application_id_local, 'criminal_record_check_status', 'COMPLETED')
#
#         return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
