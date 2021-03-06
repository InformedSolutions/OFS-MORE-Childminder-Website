import uuid
from datetime import datetime

from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .. import status
from ..business_logic import date_issued_within_three_months
from ..business_logic import (get_criminal_record_check,
                              update_criminal_record_check)
from ..dbs import read
from ..forms import (DBSLivedAbroadForm,
                     DBSMilitaryForm,
                     DBSTypeForm,
                     DBSCheckCapitaForm,
                     DBSCheckNoCapitaForm,
                     DBSUpdateForm)
from ..models import (Application,
                      CriminalRecordCheck)
from ..table_util import Table, Row
from ..utils import build_url, get_id

NO_ADDITIONAL_CERTIFICATE_INFORMATION = ['Certificate contains no information']


class DBSTemplateView(TemplateView):
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)

        return super().get_context_data(id=application_id, application_id=application_id, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = request.GET.get('id')
        redirect_url = build_url(self.success_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)


class DBSGuidanceView(DBSTemplateView):
    template_name = 'dbs-guidance.html'
    success_url = 'DBS-Lived-Abroad-View'


class DBSGuidanceSecondView(DBSTemplateView):
    template_name = 'dbs-guidance-second.html'
    success_url = 'DBS-Check-No-Capita-View'


class DBSGoodConductView(DBSTemplateView):
    template_name = 'dbs-good-conduct.html'
    success_url = 'DBS-Email-Certificates-View'


class DBSEmailCertificatesView(DBSTemplateView):
    template_name = 'dbs-email-certificates.html'
    success_url = 'DBS-Military-View'


class DBSGetView(DBSTemplateView):
    template_name = 'dbs-get.html'
    success_url = 'Task-List-View'

    def post(self, request, *args, **kwargs):
        application_id = get_id(self.request)

        # Update the task status to 'IN_PROGRESS' in all cases
        status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

        return super().post(request, *args, **kwargs)


class DBSMinistryOfDefenceView(DBSTemplateView):
    template_name = 'dbs-ministry-of-defence.html'
    success_url = 'DBS-Guidance-Second-View'


class DBSPostView(DBSTemplateView):
    template_name = 'dbs-post.html'
    success_url = 'DBS-Summary-View'


class DBSUpdateCheckView(DBSTemplateView):
    template_name = 'dbs-update-check.html'
    success_urls = ('DBS-Post-View', 'DBS-Summary-View')

    def post(self, request, *args, **kwargs):
        post_view, summary_view = self.success_urls
        app_id = get_id(self.request)
        capita = get_criminal_record_check(app_id, 'capita')

        info = get_criminal_record_check(app_id, 'certificate_information')

        # if the dbs is on capita with no certificate info go to summary
        if capita and info in NO_ADDITIONAL_CERTIFICATE_INFORMATION:
            self.success_url = summary_view
        #  else go to the post dbs view
        else:
            self.success_url = post_view

        return super().post(request, *args, **kwargs)



class DBSApplyNewView(DBSTemplateView):
    template_name = 'dbs-apply-new.html'
    success_url = 'Task-List-View'


class DBSRadioView(FormView):
    success_url = (None, None)
    dbs_field_name = None
    nullify_field_list = []
    show_cautions_convictions = None
    capita = None

    def get_initial(self):
        application_id = get_id(self.request)
        initial = super().get_initial()
        dbs_field = get_criminal_record_check(application_id, self.dbs_field_name)
        initial[self.dbs_field_name] = dbs_field

        return initial

    def get_success_url(self):
        application_id = get_id(self.request)
        yes_choice, no_choice = self.success_url

        choice_bool = get_criminal_record_check(application_id, self.dbs_field_name)

        if choice_bool:
            redirect_url = yes_choice
        elif not choice_bool:
            redirect_url = no_choice
        else:
            raise ValueError("Wasn't able to select a url in {0}".format(self.__name__))

        return build_url(redirect_url, get={'id': application_id})

    def get_form_kwargs(self):
        application_id = get_id(self.request)
        kwargs = super().get_form_kwargs()

        kwargs['id'] = application_id
        kwargs['dbs_field_name'] = self.dbs_field_name

        return kwargs

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        application = Application.objects.get(application_id=application_id)
        form = self.get_form()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem on this page'

        form.check_flag()

        context = {'id': application_id}
        if 'form' not in kwargs:
            context['form'] = form

        return super().get_context_data(**context, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        form.remove_flag()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        application_id = get_id(self.request)
        application = Application.objects.get(application_id=application_id)

        # Update task status if flagged or completed (criminal_record_check_status)
        dbs_task_status = application.criminal_record_check_status

        if dbs_task_status in ['FLAGGED', 'COMPLETED']:
            # Update the task status to 'IN_PROGRESS' from 'FLAGGED'
            status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

        # The following check will mean that cautions_convictions is not updated in the DBSCheckNoCapitaView
        if not (self.dbs_field_name == 'cautions_convictions' and not self.show_cautions_convictions):
            update_bool = self.request.POST.get(self.dbs_field_name) == 'True'

            successfully_updated = update_criminal_record_check(application_id, self.dbs_field_name, update_bool)

            if not successfully_updated:
                raise BrokenPipeError("Something went wrong when updating criminal_record_check")

        successfully_nullified = self.nullify_fields(application_id)

        if not successfully_nullified:
            raise BrokenPipeError("Something went wrong when nullifying fields in criminal_record_check")

        return super().form_valid(form)

    def nullify_fields(self, app_id):
        """
        Takes a list of fields from self (nullify_field_list) and changes them to 'None' within the database ('Null')
        This is due to the different journeys in the workflow.
        For example, if the applicant has a capita application, they don't need the 'on_update' field, so it is nullified.
        :param app_id: applicant's application id
        :return: True if successfully nullified given field
        """
        successfully_updated = update_criminal_record_check(app_id, self.nullify_field_list, None)
        return successfully_updated


class DBSSummaryView(DBSTemplateView):
    template_name = 'generic-summary-template.html'
    success_url = 'Task-List-View'

    @staticmethod
    def get_certificate_number_url(app_id):
        """
        Returns the url to redirect to when changing the dbs_certificate_number
        :param app_id: applicant's application id
        :return: Void
        """
        # Kept for legacy reasons, but now logic simply returns one view.
        return 'DBS-Check-No-Capita-View'

    @staticmethod
    def get_rows_to_generate(app_id):
        """
        Returns a dictionary with the purpose of dynamically generating the summary table.
        :param app_id: applicant's application id
        :return: Dictionary of 'rows'.
        """
        # Modify rows_to_generate to change displayed information
        rows_to_generate = [
            {
                'field': 'lived_abroad',
                'title': 'Have you lived outside of the UK in the last 5 years?',
                'url': 'DBS-Lived-Abroad-View',
                'alt_text': 'answer to living outside of the UK in the last 5 years'
            },
            {
                'field': 'military_base',
                'title': 'Have you lived or worked on a British military base outside of the UK in the last 5 years?',
                'url': 'DBS-Military-View',
                'alt_text': 'answer to living or working on a military base outside of the UK in the last 5 years'
            },
            {
                'field': 'dbs_certificate_number',
                'title': 'DBS certificate number',
                'url': DBSSummaryView.get_certificate_number_url(app_id),
                'alt_text': 'answer to DBS certificate number'
            },
            {
                'field': 'enhanced_check',
                'title': 'Is it an enhanced DBS check for home-based childcare?',
                'url': 'DBS-Check-Type-View',
                'alt_text': 'answer to DBS being enhanced and home-based'
            },
            {
                'field': 'on_update',
                'title': 'Are you on the DBS Update Service?',
                'url': 'DBS-Update-View',
                'alt_text': 'answer to DBS being on the Update Service'
            }
        ]
        return rows_to_generate

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)

        # table_obj is used for getting errors and displaying template context, it is the Table class object.
        table_obj = self.get_table_object(application_id)

        context = {'table_list': [table_obj],
                   'page_title': 'Check your answers: your criminal record checks'}

        return super().get_context_data(**context, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = request.GET.get('id')

        # Update the task status to 'COMPLETED' in all cases
        status.update(application_id, 'criminal_record_check_status', 'COMPLETED')

        return super().post(request, *args, **kwargs)

    @staticmethod
    def get_table_object(app_id):
        criminal_record_check_record = CriminalRecordCheck.objects.get(application_id=app_id)
        criminal_record_id = criminal_record_check_record.pk

        # childcare_training_row = Row('childcare_training', 'What type of childcare course have you completed?', row_value, 'Type-Of-Childcare-Training', None)

        rows_to_gen_list = DBSSummaryView.get_rows_to_generate(app_id)
        rows_to_gen_tuple = tuple(rows_to_gen_list)

        # Initialize rows initially as their rows_to_generate value IN ORDER.
        lived_abroad_row, \
        military_base_row, \
        enhanced_check_row, \
        dbs_certificate_number_row, \
        on_update_row = rows_to_gen_tuple

        row_list = [lived_abroad_row,
                    military_base_row,
                    enhanced_check_row,
                    dbs_certificate_number_row,
                    on_update_row]

        non_empty_row_list = [row for row in row_list if get_criminal_record_check(app_id, row['field']) is not None]

        Row_Obj_row_list = [Row(row['field'],
                                row['title'],
                                get_criminal_record_check(app_id, row['field']),
                                row['url']
                                , '',
                                change_link_description=row['alt_text'])
                            for row in non_empty_row_list]

        criminal_record_check_summary_table = Table([criminal_record_id])
        criminal_record_check_summary_table.error_summary_title = 'There was a problem on this page'
        criminal_record_check_summary_table.row_list = Row_Obj_row_list
        criminal_record_check_summary_table.get_errors()

        return criminal_record_check_summary_table

    @staticmethod
    def get_context_data_static(app_id):
        return DBSSummaryView.get_table_object(app_id)


class DBSUpdateView(DBSRadioView):
    template_name = 'dbs-update.html'
    form_class = DBSUpdateForm
    success_url = ('DBS-Update-Check-View', 'DBS-Get-View')
    dbs_field_name = 'on_update'



class DBSTypeView(DBSRadioView):
    template_name = 'dbs-type.html'
    form_class = DBSTypeForm
    success_url = ('DBS-Apply-New-View', 'DBS-Get-View', 'DBS-Update-Check-View')
    dbs_field_name = 'enhanced_check'

    nullify_field_list = []

    def form_valid(self, form):
        application_id = get_id(self.request)
        application = Application.objects.get(application_id=application_id)

        initial_bool = form.initial[self.dbs_field_name]
        update_bool = form.cleaned_data[self.dbs_field_name] == 'True'

        if update_bool:
            update_bool_update = self.request.POST.get('on_update') == 'True'
            successfully_updated = update_criminal_record_check(application_id, 'on_update', update_bool_update)
        else:
            successfully_updated = update_criminal_record_check(application_id, 'on_update', None)

        return super().form_valid(form)

    def get_success_url(self):
        no_enhanced, enhanced_no_update, enhanced_on_update = self.success_url
        app_id = get_id(self.request)
        crc = criminal_record_check_record = CriminalRecordCheck.objects.get(application_id=app_id)
        if (crc.enhanced_check):
            if (crc.on_update):
                redirect_url = enhanced_on_update
            elif (crc.enhanced_check != None):
                redirect_url = enhanced_no_update
        else:
            redirect_url = no_enhanced
        return build_url(redirect_url, get={'id': app_id})


class DBSMilitaryView(DBSRadioView):
    template_name = 'dbs-military.html'
    form_class = DBSMilitaryForm
    success_url = ('DBS-Ministry-Of-Defence-View', 'DBS-Guidance-Second-View')
    dbs_field_name = 'military_base'


class DBSLivedAbroadView(DBSRadioView):
    template_name = 'dbs-lived-abroad.html'
    form_class = DBSLivedAbroadForm
    success_url = ('DBS-Good-Conduct-View', 'DBS-Military-View')
    dbs_field_name = 'lived_abroad'

    def get(self, request, *args, **kwargs):
        application_id = get_id(self.request)
        application = Application.objects.get(application_id=application_id)

        # Re-route depending on task status (criminal_record_check_status)
        dbs_task_status = application.criminal_record_check_status
        if dbs_task_status == 'NOT_STARTED':
            # If no criminal_record_check exists for this user, create one
            if not CriminalRecordCheck.objects.filter(application_id=application_id).exists():
                CriminalRecordCheck.objects.create(criminal_record_id=uuid.uuid4(),
                                                   application_id=application,
                                                   dbs_certificate_number='')

            # Update the task status to 'IN_PROGRESS' from 'NOT_STARTED'
            status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

        return super().get(request, *args, **kwargs)


class DBSCheckDetailsView(DBSRadioView):
    dbs_field_name = 'cautions_convictions'
    show_cautions_convictions = None

    def form_valid(self, form):
        application_id = get_id(self.request)
        update_string = self.request.POST.get('dbs_certificate_number')

        successfully_updated = update_criminal_record_check(application_id, 'dbs_certificate_number', update_string)

        return super().form_valid(form)

    def get_initial(self):
        application_id = get_id(self.request)
        initial = super().get_initial()
        dbs_certificate_number_field = get_criminal_record_check(application_id, 'dbs_certificate_number')
        initial['dbs_certificate_number'] = dbs_certificate_number_field

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['show_cautions_convictions'] = self.show_cautions_convictions
        return kwargs


class DBSCheckCapitaView(DBSCheckDetailsView):
    # Currently Unused View
    template_name = 'dbs-check-capita.html'
    form_class = DBSCheckCapitaForm
    success_url = ('DBS-Post-View', 'DBS-Summary-View', 'DBS-Update-View', 'DBS-Check-Type-View')
    nullify_field_list = []
    show_cautions_convictions = False


class DBSCheckNoCapitaView(DBSCheckDetailsView):
    template_name = 'dbs-check-capita.html'
    form_class = DBSCheckNoCapitaForm
    success_url = ('DBS-Post-View', 'DBS-Summary-View', 'DBS-Update-View', 'DBS-Check-Type-View')
    nullify_field_list = []
    show_cautions_convictions = False

    def get_success_url(self):
        capita_info, capita_no_info, capita_old, no_capita = self.success_url
        dbs_certificate_number = self.request.POST.get('dbs_certificate_number')
        application_id = get_id(self.request)

        response = read(dbs_certificate_number)

        if response.status_code == 200:
            record = response.record
            issue_date = datetime.strptime(record['date_of_issue'], "%Y-%m-%d")
            info = record['certificate_information']

            update_criminal_record_check(application_id, 'capita', True)
            update_criminal_record_check(application_id, 'certificate_information', info)

            # Nullify fields on the capita = False route
            update_criminal_record_check(application_id, 'enhanced_check', None)
            update_criminal_record_check(application_id, 'on_update', None)

            if date_issued_within_three_months(issue_date):
                update_criminal_record_check(application_id, 'within_three_months', True)
                if not info in NO_ADDITIONAL_CERTIFICATE_INFORMATION:
                    redirect_url = capita_info
                else:
                    redirect_url = capita_no_info
            else:
                update_criminal_record_check(application_id, 'within_three_months', False)
                redirect_url = capita_old
        else:
            update_criminal_record_check(application_id, 'capita', False)
            redirect_url = no_capita

            # Nullify fields on the capita = True route
            update_criminal_record_check(application_id, 'within_three_months', None)
            update_criminal_record_check(application_id, 'certificate_information', "")

            # TODO: Currently just redirecting as if not a valid dbs number if DBS API is inaccessible.

        return build_url(redirect_url, get={'id': application_id})
