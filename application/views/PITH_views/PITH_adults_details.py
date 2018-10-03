import logging

from django.http import HttpResponseRedirect

from application.business_logic import remove_adult, rearrange_adults, get_application
from application.forms.PITH_forms.PITH_adult_details_form import PITHAdultDetailsForm
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView

# Initiate logging
log = logging.getLogger('')


class PITHAdultDetailsView(PITHRadioView):

    template_name = 'PITH_templates/PITH_adults_details.html'
    form_class = PITHAdultDetailsForm
    success_url = ('PITH-Adult-Details-View', 'PITH-Children-Check-View')
    application_field_name = 'adults_in_home'

    def get(self, request, *args, **kwargs):

        application_id = get_id(request)
        num_adults = int(request.GET.get('adults'))
        remove_person = int(request.GET.get('remove'))

        if remove_person:

            # Remove adult flagged for being removed.
            remove_adult(application_id, remove_person)
            log.debug('Adult ' + str(remove_person) + ' removed')

        # Rearrange adults to remove empty spaces in adult list.
        rearrange_adults(num_adults, application_id)
        log.debug('Adults rearranged')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        application_id = get_id(self.request)
        num_adults = int(self.request.GET.get('adults'))
        PITH_status = get_application(application_id, 'people_in_home_status')

        remove_person = int(self.request.GET.get('remove'))

        # If no adults exist, initialise one instance of the form by setting to var to 1.
        num_adults = 1 if num_adults == 0 else num_adults

        # Disable the remove button if number_of_adults is 1.
        show_remove_button = not num_adults == 1

        email_list = self.get_email_list(num_adults)
        log.debug('List of adult emails retrieved: ' + email_list)

        form_list = [self.create_form_instance(application_id, index, email_list) for index in range(1, num_adults + 1)]
        log.debug('List of forms retrieved')

        context = {
            'form': None,
            'form_list': form_list,
            'application_id': application_id,
            'number_of_adults': num_adults,
            'add_adult': num_adults + 1,
            'remove_adult': num_adults - 1,
            'remove_button': show_remove_button,
            'people_in_home_status': PITH_status
        }

        return context

    def create_form_instance(self, app_id, adult_index, email_list):

        form_class = self.get_form_class()

        new_form = form_class(id=app_id,
                              adult=adult_index,
                              prefix=adult_index,
                              email_list=email_list)
        new_form.check_flag()
        log.debug('Form instance created for adult ' + str(adult_index))

        return new_form

    def get_email_list(self, num_adults):

        return ['' for index in range(1, num_adults + 1)]

    def form_valid(self, form):

        context = {
            'id': get_id(self.request),
            'adults': 0,
            'remove': 0
        }

        return HttpResponseRedirect(self.get_success_url(get=context))



