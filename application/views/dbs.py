import uuid

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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

from django.views.generic.edit import FormView
from django.views.generic import TemplateView


class DBSTemplateView(TemplateView):
    template_name = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

        return super().get_context_data(id=application_id, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = request.GET.get('id')
        redirect_url = build_url(self.success_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)

class DBSGuidanceView(DBSTemplateView):
    template_name = 'dbs-guidance.html'
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
    success_url = 'DBS-Guidance-View'


class DBSPostView(DBSTemplateView):
    template_name = 'dbs-post.html'
    success_url = 'DBS-Summary-View'


class DBSRadioView(FormView):
    success_url = (None, None)
    dbs_field_name = None
    nullify_field_list = []

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

        return super().get_context_data(id=application_id, **kwargs)

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
        update_criminal_record_check(app_id, self.nullify_field_list, None)
        return True


class DBSSummaryView(DBSTemplateView):
    template_name = 'dbs-summary.html'
    success_url = 'Task-List-View'

    def get_context_data(self, **kwargs):
        application_id = self.request.GET.get('id')

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
                'url': self.get_certificate_number_url(application_id),
                'alt_text': 'Change DBS certificate number'
            },
            {
                'field': 'cautions_convictions',
                'title': 'Do you have any criminal cautions or convictions?',
                'url': 'DBS-Check-Capita-View',
                'alt_text': 'Change answer on cautions or convictions?'
            }
        ]

        # Create a dictionary with the field as the key from rows_to_generate
        # This is so that the relevant information can be accessed without having to loop through rows_to_generate
        rows_to_generate_dict = {dict['field']: dict for dict in rows_to_generate}

        # Generate a list of fields to pass into get_criminal_record_check()
        field_list = [row['field'] for row in rows_to_generate]

        # Dictionary is of format {'dbs_cert': ((dbs_cert_value_in_database)), ...}
        table_content_dict = get_criminal_record_check(application_id, field_list)

        # Create a list in format [{'id': dbs_cert, 'title': title_list[id], ...}, ...]
        table_content = [
            {'id': key,
             'title': rows_to_generate_dict[key]['title'],
             'value': value,
             'url': rows_to_generate_dict[key]['url'],
             'alt_text': rows_to_generate_dict[key]['alt_text']
             }
            for key, value in table_content_dict.items()]

        return super().get_context_data(table=table_content, **kwargs)

    def get_certificate_number_url(self, app_id):
        capita_status = get_criminal_record_check(app_id, 'capita')
        if capita_status:
            return 'DBS-Check-Capita-View'
        elif not capita_status:
            return 'DBS-Check-No-Capita-View'
        else:
            raise ValueError('capita_status should be either True or False by this point, but it is {0}'.format(capita_status))

    def post(self, request, *args, **kwargs):
        application_id = request.GET.get('id')

        # Update the task status to 'COMPLETED' in all cases
        status.update(application_id, 'criminal_record_check_status', 'COMPLETED')

        return super().post(request, *args, **kwargs)


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

    def form_valid(self, form):
        application_id = self.request.GET.get('id')
        initial_bool = form.initial[self.dbs_field_name]
        update_bool = form.cleaned_data[self.dbs_field_name] == 'True'

        # If the 'Type of DBS check' is changed then clear the user's dbs_certificate_number
        if update_bool != initial_bool:
            successfully_updated = update_criminal_record_check(application_id, 'dbs_certificate_number', '')

        return super().form_valid(form)


class DBSMilitaryView(DBSRadioView):
    template_name = 'dbs-military.html'
    form_class = DBSMilitaryForm
    success_url = ('DBS-Ministry-Of-Defence-View', 'DBS-Guidance-View')
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
        if dbs_task_status == 'NOT_STARTED' or 'IN_PROGRESS':
            # Update the task status to 'IN_PROGRESS' from 'NOT_STARTED'
            status.update(application_id, 'criminal_record_check_status', 'IN_PROGRESS')

            # If no criminal_record_check exists for this user, create one
            if not CriminalRecordCheck.objects.filter(application_id=application_id).exists():
                CriminalRecordCheck.objects.create(criminal_record_id=uuid.uuid4(),
                                                   application_id=application,
                                                   dbs_certificate_number='')

        elif dbs_task_status == 'FLAGGED' or 'COMPLETED':
            # Re-route user to summary page
            redirect_url = build_url(reverse('DBS-Summary-View'), get={'id': application_id})
            return HttpResponseRedirect(redirect_url)

        else:
            raise ValueError('Unexpected task_status passed: {0}'.format(dbs_task_status))

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