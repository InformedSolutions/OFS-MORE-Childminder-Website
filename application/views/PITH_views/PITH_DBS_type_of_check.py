import logging

from datetime import datetime
from application import dbs
from application.business_logic import update_adult_in_home, find_dbs_status, DBSStatus
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

    enhanced_check_field = 'enhanced_check'
    on_update_field = 'on_update'

    def get_form_kwargs(self, adult=None, ask_if_enhanced_check=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'adult': adult,
            'ask_if_enhanced_check': ask_if_enhanced_check,
            'enhanced_check_field': self.enhanced_check_field,
            'on_update_field': self.on_update_field
        }

        log.debug('Return keyword arguments to instantiate the form')

        return super().get_form_kwargs(context)

    def get_form_list(self):

        application_id = get_id(self.request)

        adult_tuples = self.get_adults_needing_info(application_id)

        form_list = [self.form_class(**self.get_form_kwargs(
                        adult=adult,
                        ask_if_enhanced_check=dbs_status == DBSStatus.NEED_ASK_IF_ENHANCED_CHECK))
                     for adult, dbs_status in adult_tuples]

        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Sorted form list generated')

        return sorted_form_list

    def get_initial(self):

        application_id = get_id(self.request)

        adult_tuples = self.get_adults_needing_info(application_id)

        initial_context = {}

        for adult, _ in adult_tuples:

            initial_context.update({
                self.enhanced_check_field + str(adult.pk): adult.enhanced_check,
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

            enhanced_check_val = form.cleaned_data[form.enhanced_check_field_name] == 'True' \
                if form.cleaned_data.get(form.enhanced_check_field_name, None) else None
            on_update_val = form.cleaned_data[form.on_update_field_name] == 'True' \
                if form.cleaned_data.get(form.on_update_field_name, None) else None

            self.update_adult_in_home_fields(form.adult.pk, enhanced_check_val, on_update_val)

        return redirect

    def get_adults_needing_info(self, application_id):
        """
        Finds the list of adults in the home for this application for whom we need more
            info about their dbs number
        :param application_id:
        :return: list of 2-tuples each containing the adult model and their DBSStatus
        """

        filtered = []
        for adult in AdultInHome.objects.filter(application_id=application_id):

            dbs_status = find_dbs_status(adult, adult)

            if dbs_status in (DBSStatus.NEED_ASK_IF_ENHANCED_CHECK, DBSStatus.NEED_ASK_IF_ON_UPDATE):
                filtered.append((adult, dbs_status))

        return filtered

    def update_adult_in_home_fields(self, adult_id, enhanced_check_value, on_update_value):
        update_adult_in_home(adult_id, 'enhanced_check', enhanced_check_value)
        update_adult_in_home(adult_id, 'on_update', on_update_value)
