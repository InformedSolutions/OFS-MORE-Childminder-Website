import logging
import collections

from django.http import HttpResponseRedirect

from application.models import AdultInHome
from application.forms.PITH_forms.PITH_DBS_check_form import PITHDBSCheckForm
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_multi_form_view import PITHMultiFormView
from application.business_logic import update_adult_in_home, DBSStatus, find_dbs_status

# Initiate logging
log = logging.getLogger('')


class PITHDBSCheckView(PITHMultiFormView):

    template_name = 'PITH_templates/PITH_DBS_check.html'
    form_class = PITHDBSCheckForm
    success_url = ('PITH-Children-Check-View', 'PITH-DBS-Type-Of-Check-View')

    dbs_field = 'dbs_certificate_number'

    def get_form_kwargs(self, adult=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'adult': adult,
            'dbs_field': self.dbs_field,
        }

        log.debug('Return keyword arguments to instantiate the form')

        return super().get_form_kwargs(context)

    def get_form_list(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        form_list = [self.form_class(**self.get_form_kwargs(adult=adult)) for adult in adults]

        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Sorted form list generated')

        return sorted_form_list

    def validate_form_list(self, form_list):
        if not super().validate_form_list(form_list):
            return False
        # validation of individual forms is done in the form objects themselves. This extra step checks the forms
        # against each other to check that the dbs numbers are unique
        dbs_counts = collections.defaultdict(int)
        for form in form_list:
            dbs_counts[form.cleaned_data[form.dbs_field_name]] += 1
        valid = True
        for form in form_list:
            if dbs_counts[form.cleaned_data[form.dbs_field_name]] > 1:
                form.add_error(form.dbs_field, 'Please enter a different DBS number. '
                                               'You entered this number for someone in your childcare location')
                valid = False
        return valid

    def get_initial(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        initial_context = {}

        for adult in adults:

            initial_context.update({
                self.dbs_field + str(adult.pk): adult.dbs_certificate_number,
            })

        log.debug('Initialising field data')

        return initial_context

    def get_success_url(self, form_list=[]):

        ok_url, need_info_url = self.success_url

        if any(find_dbs_status(form.adult, form.adult) in (
                    DBSStatus.NEED_ASK_IF_ENHANCED_CHECK, DBSStatus.NEED_ASK_IF_ON_UPDATE)
               for form in form_list):
            url = need_info_url
        else:
            url = ok_url

        return super().get_success_url(url)

    def form_valid(self, form_list):

        # ignore redirect from super
        super().form_valid(form_list)

        # Save dbs numbers to database
        for form in form_list:
            dbs_number = form.data[form.dbs_field_name]
            update_adult_in_home(form.pk, self.dbs_field, dbs_number)

        # pass in form list to determine redirect url
        return HttpResponseRedirect(self.get_success_url(form_list))



