import logging

from django.http import HttpResponseRedirect

from application.utils import build_url, get_id
from application.models import AdultInHome
from application.views.PITH_views.base_views.PITH_multi_radio_view import PITHMultiRadioView
from application.forms.PITH_forms.PITH_address_details import PITHAddressForm
from application.business_logic import get_childcare_register_type

# Initiate logging
log = logging.getLogger('')


class PITHAddressDetailsView(PITHMultiRadioView):

    template_name = 'PITH_templates/PITH_address_details.html'
    form_class = PITHAddressForm
    success_url = ('PITH-Lived-Abroad-View', 'PITH-Address-Select-View', 'PITH-Address-Manual-View')
    PITH_field_name = 'PITH_same_address'

    def get_form_kwargs(self, adult=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'PITH_field_name': self.PITH_field_name,
            'adult': adult}

        log.debug('Return keyword arguments to instantiate the form')

        return super().get_form_kwargs(context)

    def get_success_url(self, get=None):
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)

        if not get:

            return build_url(self.get_choice_url(application_id), get={'id': application_id})

        else:

            return build_url(self.get_choice_url(application_id), get=get)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        log.debug('Checking if form is valid')

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        for adult in adults:

            PITH_same_address_bool = self.request.POST.get(self.PITH_field_name+str(adult.pk))

            setattr(adult, self.PITH_field_name, PITH_same_address_bool)
            adult.save()

        return super().form_valid(form)

    def get_form_list(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id, PITH_same_address=False)
        form_list = [self.form_class(**self.get_form_kwargs(adult=adult)) for adult in adults]
        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Retrieving sorted form list')
        log.debug('Sorted form list is: {}'.format(sorted_form_list))

        return sorted_form_list

    def get_initial(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        initial_context = {self.PITH_field_name+str(adult.pk): adult.lived_abroad
                           for adult in adults}

        log.debug('Form field data initialised')

        return initial_context

    def get_choice_url(self, app_id):

        adults = AdultInHome.objects.filter(application_id=app_id)

        yes_choice, no_yes_choice, no_no_choice = self.success_url

        childcare_register_status, childcare_register_cost = get_childcare_register_type(app_id)

        if any(adult.lived_abroad for adult in adults):

            log.debug('Adults have lived abroad')

            return yes_choice

        else:

            log.debug('Adults have not lived abroad')

            if not ('CR' in childcare_register_status and 'EYR' not in childcare_register_status):

                log.debug('Only applying to Childcare Register')

                return no_yes_choice

            else:

                log.debug('Not applying to Childcare Register')

                return no_no_choice
