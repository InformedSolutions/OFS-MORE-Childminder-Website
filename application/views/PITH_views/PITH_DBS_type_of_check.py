import logging

from datetime import datetime
from application import dbs
from application.business_logic import date_issued_within_three_months, update_adult_in_home
from application.models import AdultInHome
from application.forms.PITH_forms.PITH_DBS_type_of_check_form import PITHDBSTypeOfCheckForm
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_multi_radio_view import PITHMultiRadioView

# Initiate logging
log = logging.getLogger('')


class PITHDBSTypeOfCheckView(PITHMultiRadioView):

    template_name = 'PITH_templates/PITH_DBS_type_of_check.html'
    form_class = PITHDBSTypeOfCheckForm
    success_url = 'PITH-DBS-Post-Or-Apply-View'

    capita_field = 'capita'
    on_update_field = 'on_update'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # for caching result of dbs lookups for this request
        self.adults_needing_info = None

    def get_form_kwargs(self, adult=None, ask_if_capita=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'adult': adult,
            'ask_if_capita': ask_if_capita,
            'capita_field': self.capita_field,
            'on_update_field': self.on_update_field
        }

        log.debug('Return keyword arguments to instantiate the form')

        return super().get_form_kwargs(context)

    def get_form_list(self):

        application_id = get_id(self.request)

        adult_tuples = self.get_adults_needing_info(application_id)

        form_list = [self.form_class(**self.get_form_kwargs(adult=adult, ask_if_capita=not found))
                     for adult, found in adult_tuples]

        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Sorted form list generated')

        return sorted_form_list

    def get_initial(self):

        application_id = get_id(self.request)

        adult_tuples = self.get_adults_needing_info(application_id)

        initial_context = {}

        for adult, _ in adult_tuples:

            initial_context.update({
                self.capita_field + str(adult.pk): adult.capita,
                self.on_update_field + str(adult.pk): adult.on_update,
            })

        log.debug('Initialising field data')

        return initial_context

    def get_choice_url(self, app_id):
        
        return self.success_url

    def form_valid(self, form_list):

        redirect = super().form_valid(form_list)

        # record to database
        for form in form_list:

            capita_val = form.cleaned_data[form.capita_field_name] == 'True' \
                if form.cleaned_data.get(form.capita_field_name, None) else None
            on_update_val = form.cleaned_data[form.on_update_field_name] == 'True' \
                if form.cleaned_data.get(form.on_update_field_name, None) else None

            self.update_adult_in_home_fields(form.adult.pk, capita_val, on_update_val)

        return redirect

    def get_adults_needing_info(self, application_id):
        """
        Finds the list of adults in the home for this application for whom we need more
            info about their dbs number
        :param application_id:
        :return: list of 2-tuples each containing the adult model and a bool to indicate
            whether they were on the capita list
        """

        if self.adults_needing_info is not None:
            return self.adults_needing_info

        filtered = []
        for adult in AdultInHome.objects.filter(application_id=application_id):

            # fetch dbs record
            dbs_record_response = dbs.read(adult.dbs_certificate_number)
            dbs_record = getattr(dbs_record_response, 'record', None)
            record_found = dbs_record is not None

            if record_found:
                issue_date = datetime.strptime(dbs_record['date_of_issue'], "%Y-%m-%d")
                if date_issued_within_three_months(issue_date):
                    continue

            filtered.append((adult, record_found))

        self.adults_needing_info = filtered
        return filtered

    def update_adult_in_home_fields(self, adult_id, capita_value, on_update_value):
        update_adult_in_home(adult_id, 'capita', capita_value)
        update_adult_in_home(adult_id, 'on_update', on_update_value)
