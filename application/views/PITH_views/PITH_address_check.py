import logging

from django.http import HttpResponseRedirect

from application.utils import build_url, get_id
from application.models import AdultInHome, AdultInHomeAddress, ApplicantHomeAddress, ApplicantPersonalDetails, Application
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_address_check import PITHAddressDetailsCheckForm
from .. import address_helper, status
# Initiate logging
log = logging.getLogger('')


class PITHAdultAddressCheckView(PITHRadioView):

    template_name = 'PITH_templates/PITH_address_check.html'
    form_class = PITHAddressDetailsCheckForm
    success_url = ('PITH-Lived-Abroad-View', 'PITH-Address-Details-View')
    PITH_field_name = 'adult_in_home_address'

    def get(self, request, *args, **kwargs):

        application_id = get_id(request)
        num_adults = int(request.GET('adults'))

        # Rearrange adults to remove empty spaces in adult list.
        rearrange_adults(num_adults, application_id)
        log.debug('Adults rearranged')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        application_id = get_id(self.request)
        num_adults = int(self.request.GET.get('adults'))
        PITH_status = get_application(application_id, 'people_in_home_status')
        num_adults = 1 if num_adults == 0 else num_adults


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
            same_address_bool = self.request.POST.get(self.PITH_field_name+str(adult.pk))

            setattr(adult, self.PITH_field_name, same_address_bool)
            adult.save()

        return super().form_valid(form)

    def get_form_list(self):

        application_id = get_id(self.request)
        adults = AdultInHomeAddress.objects.filter(application_id=application_id)
        form_list = [self.form_class(**self.get_form_kwargs(adult=adult)) for adult in adults]
        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Retrieving sorted form list')

        return sorted_form_list

    def get_initial(self):

        application_id = get_id(self.request)
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=application_id).personal_detail_id
        applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  current_address=True)
        street_line1 = applicant_home_address.street_line1
        street_line2 = applicant_home_address.street_line2
        town = applicant_home_address.town
        county = applicant_home_address.county
        postcode = applicant_home_address.postcode

        initial = {}
        adults = AdultInHomeAddress.objects.filter(application_id=application_id)
        for adult in adults:
            initial[self.PITH_field_name+str(adult.pk)] = adult.adult_in_home_address
        initial[self.street_line1] = street_line1
        initial[self.street_line2] = street_line2
        initial[self.town] = town
        initial[self.county] = county
        initial[self.postcode] = postcode

        log.debug('Form field data initialised')
        return initial

    def get_choice_url(self, app_id):

        adults = AdultInHomeAddress.objects.filter(application_id=app_id)

        yes_choice, no_yes_choice, no_no_choice = self.success_url

        if any(adult.adult_in_home_address for adult in adults):

            log.debug('Adults at same address')

            return yes_choice

        else:

            log.debug('Adults not at same address')