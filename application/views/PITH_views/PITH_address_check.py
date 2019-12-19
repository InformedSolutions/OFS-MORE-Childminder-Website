import logging

from django.http import HttpResponseRedirect

from application.views.PITH_views.your_adults import get_first_adult_number_for_address_entry
from application.utils import build_url, get_id
from application.models import AdultInHome, AdultInHomeAddress, ApplicantHomeAddress, ApplicantPersonalDetails, \
    Application, ChildAddress
from application.views.PITH_views.base_views.PITH_multi_radio_view import PITHMultiRadioView
from application.forms.PITH_forms.PITH_address_check import PITHAddressDetailsCheckForm

from .. import address_helper, status
# Initiate logging
log = logging.getLogger('')


class PITHAdultAddressCheckView(PITHMultiRadioView):

    template_name = 'PITH_templates/PITH_address_check.html'
    form_class = PITHAddressDetailsCheckForm
    success_url = ('PITH-Lived-Abroad-View', 'PITH-Address-Details-View')
    PITH_same_address_field = 'PITH_same_address'
    PITH_same_time_field = 'PITH_same_time'
    PITH_moved_in_date_field = 'PITH_moved_in_date_field'



    def get_form_kwargs(self, adult=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'PITH_same_address_field': self.PITH_same_address_field,
            'PITH_same_time_field': self.PITH_same_time_field,
            'PITH_moved_in_date_field': self.PITH_moved_in_date_field,
            'adult': adult}

        log.debug('Return keyword arguments to instantiate the form')

        return super().get_form_kwargs(context)

    def get_context_data(self, **kwargs):

        application_id = get_id(self.request)

        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=application_id).personal_detail_id
        childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  childcare_address=True)
        street_line1 = childcare_address.street_line1
        street_line2 = childcare_address.street_line2
        town = childcare_address.town
        county = childcare_address.county
        postcode = childcare_address.postcode
        log.debug('Generated address of applicant')

        context = {
            'application_id': application_id,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode
        }

        return super().get_context_data(**context, **kwargs)


    def get_success_url(self, get=None):
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)
        context = {
            'id': get_id(self.request)
        }
        if AdultInHome.objects.filter(application_id=application_id, PITH_same_address=False).exists():
            # adult = AdultInHome.objects.filter(application_id=application_id, PITH_same_address=False)
            first_adult = get_first_adult_number_for_address_entry(application_id)

            if not get:

                return build_url(self.get_choice_url(application_id), get={'id': application_id,
                                                                           'adult': str(first_adult)})

        else:
            return build_url(self.get_choice_url(application_id), get=context)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        log.debug('Checking if form is valid')

        application_id = get_id(self.request)

        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=application_id).personal_detail_id
        applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  current_address=True)
        street_line1 = applicant_home_address.street_line1
        street_line2 = applicant_home_address.street_line2
        town = applicant_home_address.town
        county = applicant_home_address.county
        country = applicant_home_address.country
        postcode = applicant_home_address.postcode

        adults = AdultInHome.objects.filter(application_id=application_id)
        for adult in adults:
            PITH_same_address_bool = self.request.POST.get(self.PITH_same_address_field + str(adult.pk))
            setattr(adult, self.PITH_same_address_field, PITH_same_address_bool)
            PITH_same_time_bool = self.request.POST.get(self.PITH_same_time_field + str(adult.pk))
            setattr(adult, self.PITH_same_time_field, PITH_same_time_bool)
            adult.save()
            adult_id = adult.adult_id
            if adult.PITH_same_address:
                if AdultInHomeAddress.objects.filter(adult_id=adult_id).count() == 0:
                    pith_address_record = AdultInHomeAddress(street_line1=street_line1,
                                                             street_line2=street_line2,
                                                             town=town,
                                                             county=county,
                                                             country=country,
                                                             postcode=postcode,
                                                             adult_in_home_address=None,
                                                             adult_id=AdultInHome.objects.get(adult_id=adult_id),
                                                             application_id=Application.objects.get(application_id=
                                                                                                    application_id)
                                                             )
                    pith_address_record.save()
                else:
                    PITH_same_address = AdultInHomeAddress.objects.filter(adult_id=adult_id)
                    PITH_same_address.update(street_line1=street_line1, street_line2=street_line2, town=town,
                                             county=county, country=country, postcode=postcode,
                                             )
            if adult.PITH_same_time:
                if AdultInHomeAddress.objects.filter(adult_id=adult_id).count() == 0:
                    pith_address_record = AdultInHomeAddress(moved_in_day=adult.moved_in_day,
                                                             moved_in_month=adult.moved_in_month,
                                                             moved_in_year=adult.moved_in_year,
                                                             adult_id=AdultInHome.objects.get(adult_id=adult_id),
                                                             application_id=Application.objects.get(application_id=
                                                                                                    application_id)
                                                             )
                    pith_address_record.save()
                else:
                    PITH_same_address = AdultInHomeAddress.objects.filter(adult_id=adult_id)
                    PITH_same_address.update(moved_in_day=adult.moved_in_day,moved_in_month=adult.moved_in_month,
                                             moved_in_year=adult.moved_in_year
                                             )
        return super().form_valid(form)

    def get_form_list(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)
        form_list = [self.form_class(**self.get_form_kwargs(adult=adult)) for adult in adults]
        sorted_form_list = sorted(form_list, key=lambda form: form.adult.adult)

        log.debug('Retrieving sorted form list')
        return sorted_form_list

    def get_initial(self):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)
        log.debug('Initialising form field data')
        initial_context = {}
        for adult in adults:
            initial_context.update({
                self.PITH_same_address_field + str(adult.pk): adult.PITH_same_address,
                self.PITH_same_time_field + str(adult.pk): adult.PITH_same_time,
                self.PITH_moved_in_date_field + str(adult.pk): None
            })
            if len(AdultInHomeAddress.objects.filter(adult_id=adult.pk)) > 0:
                initial_context.update({
                    self.PITH_moved_in_date_field + str(adult.pk):
                        AdultInHomeAddress.objects.get(adult_id=adult.pk).get_moved_in_date()
                })

        log.debug('Form field data initialised')

        return initial_context

    def get_choice_url(self, app_id):

        adults = AdultInHome.objects.filter(application_id=app_id)

        yes_choice, no_choice = self.success_url

        if any(not adult.PITH_same_address for adult in adults):

            log.debug('Adult lives at applicant\'s address')

            return no_choice

        else:

            log.debug('Adults live at different address')

            return yes_choice
