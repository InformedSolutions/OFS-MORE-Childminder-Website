import uuid

from django.http import HttpResponseRedirect

from .. import status
from ..business_logic import (get_criminal_record_check,
                              update_criminal_record_check)
from ..forms import (DBSLivedAbroadForm,
                     DBSMilitaryForm,
                     DBSTypeForm,
                     DBSCheckCapitaForm,
                     DBSCheckNoCapitaForm,
                     DBSUpdateForm)
from ..models import (Application,
                      CriminalRecordCheck)

from ..utils import build_url
from ..table_util import Table, Row

from django.views.generic.edit import FormView
from django.views.generic import TemplateView


class DBSTemplateView(TemplateView):
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

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
    success_url = 'DBS-Type-View'


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
        application_id = self.request.GET.get('id')

        # Update the task status to 'IN_PROGRESS' in all cases
        status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

        return super().post(request, *args, **kwargs)


class DBSMinistryOfDefenceView(DBSTemplateView):
    template_name = 'dbs-ministry-of-defence.html'
    success_url = 'DBS-Guidance-Second-View'


class DBSPostView(DBSTemplateView):
    template_name = 'dbs-post.html'
    success_url = 'DBS-Summary-View'


class DBSRadioView(FormView):
    success_url = (None, None)
    dbs_field_name = None
    nullify_field_list = []

    def get(self, request, *args, **kwargs):
        application_id = self.request.GET.get('id')
        application = Application.objects.get(application_id=application_id)

        # Re-route depending on task status (criminal_record_check_status)
        dbs_task_status = application.criminal_record_check_status

        if dbs_task_status == 'FLAGGED':
            # Update the task status to 'IN_PROGRESS' from 'FLAGGED'
            status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        application_id = self.request.GET.get('id')
        initial = super().get_initial()
        dbs_field = get_criminal_record_check(application_id, self.dbs_field_name)
        initial[self.dbs_field_name] = dbs_field

        return initial

    def get_success_url(self):
        application_id = self.request.GET.get('id')
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
        application_id = self.request.GET.get('id')
        kwargs = super().get_form_kwargs()

        kwargs['id'] = application_id
        kwargs['dbs_field_name'] = self.dbs_field_name

        return kwargs

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')
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

    def form_valid(self, form):
        application_id = self.request.GET.get('id')
        update_bool = self.request.POST.get(self.dbs_field_name) == 'True'

        successfully_updated = update_criminal_record_check(application_id, self.dbs_field_name, update_bool)

        successfully_nullified = self.nullify_fields(application_id)

        if not successfully_updated:
            raise BrokenPipeError("Something went wrong when updating criminal_record_check")
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
        capita_status = get_criminal_record_check(app_id, 'capita')
        if capita_status:
            return 'DBS-Check-Capita-View'
        elif not capita_status:
            return 'DBS-Check-No-Capita-View'
        else:
            raise ValueError('capita_status should be either True or False by this point, but it is {0}'.format(capita_status))

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
                'alt_text': 'Change answer to living outside of the UK in the last 5 years'
            },
            {
                'field': 'military_base',
                'title': 'Have you lived or worked on a British military base in the last 5 years?',
                'url': 'DBS-Military-View',
                'alt_text': 'Change answer to living or working on a military base outside of the UK in the last 5 years'
            },
            {
                'field': 'capita',
                'title': 'Do you have an Ofsted DBS Check?',
                'url': 'DBS-Type-View',
                'alt_text': 'Change answer to having an Ofsted DBS Check'
            },
            {
                'field': 'on_update',
                'title': 'Are you on the DBS update service?',
                'url': 'DBS-Update-View',
                'alt_text': 'Change answer to being on the DBS update service'
            },
            {
                'field': 'dbs_certificate_number',
                'title': 'DBS certificate number',
                'url': DBSSummaryView.get_certificate_number_url(app_id),
                'alt_text': 'Change DBS certificate number'
            },
            {
                'field': 'cautions_convictions',
                'title': 'Do you have any criminal cautions or convictions?',
                'url': 'DBS-Check-Capita-View',
                'alt_text': 'Change answer on cautions or convictions?'
            }
        ]
        return rows_to_generate

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

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

        #Initialize rows initially as their rows_to_generate value IN ORDER.
        lived_abroad_row,\
        military_base_row, \
        capita_row, \
        on_update_row, \
        dbs_certificate_number_row, \
        cautions_convictions_row = rows_to_gen_tuple

        row_list = [lived_abroad_row,
                    military_base_row,
                    capita_row,
                    on_update_row,
                    dbs_certificate_number_row,
                    cautions_convictions_row]

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
    success_url = ('DBS-Check-No-Capita-View', 'DBS-Get-View')
    dbs_field_name = 'on_update'
    nullify_field_list = ['cautions_convictions']


class DBSTypeView(DBSRadioView):
    template_name = 'dbs-type.html'
    form_class = DBSTypeForm
    success_url = ('DBS-Check-Capita-View', 'DBS-Update-View')
    dbs_field_name = 'capita'
    nullify_field_list = ['cautions_convictions']

    def form_valid(self, form):
        application_id = self.request.GET.get('id')
        initial_bool = form.initial[self.dbs_field_name]
        update_bool = form.cleaned_data[self.dbs_field_name] == 'True'

        application = Application.objects.get(application_id=application_id)

        # If the 'Type of DBS check' is changed then clear the user's dbs_certificate_number
        # Also check that the application is not in review as this can lead to blank fields being submitted.
        if update_bool != initial_bool and application.application_status != 'FURTHER_INFORMATION':
            successfully_updated = update_criminal_record_check(application_id, 'dbs_certificate_number', '')

        return super().form_valid(form)


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
        application_id = self.request.GET.get('id')
        application = Application.objects.get(application_id=application_id)

        # Re-route depending on task status (criminal_record_check_status)
        dbs_task_status = application.criminal_record_check_status
        if dbs_task_status == 'NOT_STARTED':
            # Update the task status to 'IN_PROGRESS' from 'NOT_STARTED'
            status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

            # If no criminal_record_check exists for this user, create one
            if not CriminalRecordCheck.objects.filter(application_id=application_id).exists():
                CriminalRecordCheck.objects.create(criminal_record_id=uuid.uuid4(),
                                                   application_id=application,
                                                   dbs_certificate_number='')

        return super().get(request, *args, **kwargs)


class DBSCheckDetailsView(DBSRadioView):
    dbs_field_name = 'cautions_convictions'
    show_cautions_convictions = None

    def form_valid(self, form):
        application_id = self.request.GET.get('id')
        update_string = self.request.POST.get('dbs_certificate_number')

        successfully_updated = update_criminal_record_check(application_id, 'dbs_certificate_number', update_string)

        return super().form_valid(form)

    def get_initial(self):
        application_id = self.request.GET.get('id')
        initial = super().get_initial()
        dbs_certificate_number_field = get_criminal_record_check(application_id, 'dbs_certificate_number')
        initial['dbs_certificate_number'] = dbs_certificate_number_field

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['show_cautions_convictions'] = self.show_cautions_convictions
        return kwargs


class DBSCheckCapitaView(DBSCheckDetailsView):
    template_name = 'dbs-check-capita.html'
    form_class = DBSCheckCapitaForm
    success_url = ('DBS-Post-View', 'DBS-Summary-View')
    nullify_field_list = ['on_update']
    show_cautions_convictions = True


class DBSCheckNoCapitaView(DBSCheckDetailsView):
    template_name = 'dbs-check-capita.html'
    form_class = DBSCheckNoCapitaForm
    success_url = 'DBS-Post-View'
    show_cautions_convictions = False

    def get_success_url(self):
        application_id = self.request.GET.get('id')
        return build_url(self.success_url, get={'id': application_id})