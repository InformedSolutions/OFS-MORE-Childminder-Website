import logging

from django.http import HttpResponseRedirect

from application.business_logic import get_application, update_application
from application.forms.PITH_forms.PITH_base_forms.PITH_own_children_check_form import PITHOwnChildrenCheckForm
from application.models import AdultInHome, Child
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView

# Initiate logging
log = logging.getLogger('')


class PITHOwnChildrenCheckView(PITHRadioView):
    template_name = 'PITH_templates/PITH_own_children_check.html'
    form_class = PITHOwnChildrenCheckForm
    success_url = ('PITH-Summary-View', 'Task-List-View')
    application_field_name = 'own_children_not_in_home'

    def form_valid(self, form):

        log.debug('Checking if form is valid')

        application_id = get_id(self.request)

        super().update_db(application_id)

        choice_bool = get_application(application_id, self.application_field_name)

        context = {
            'id': get_id(self.request)
        }

        if choice_bool:

            log.debug('There are own children not living in the home')

            num_children = len(Child.objects.filter(application_id=application_id))

            log.debug('Get numer of children: ' + str(num_children))

            adults_context = {
                'children': num_children,
                'remove': 0
            }

            context.update(adults_context)

        else:

            log.debug('There are no own children not living in the home')

            # Remove any existing children not in the home.
            self.__clear_children_not_in_home(application_id)
            log.debug('Remove children not in home')

        return HttpResponseRedirect(self.get_success_url(get=context))

    def get_choice_url(self, app_id):

        valid_DBS, invalid_DBS = self.success_url
        choice_bool = get_application(app_id, self.application_field_name)
        adults = AdultInHome.objects.filter(application_id=app_id)


        if choice_bool:

            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                log.debug('Known to social service in regards to children and invalid DBS')

                return invalid_DBS

            else:
                log.debug(
                    'Known to social service in regards to children and valid DBS')

                return valid_DBS

        else:

            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):

                log.debug(
                    'Not known to social service in regards to children and all invalid DBS')

                return invalid_DBS

            else:
                log.debug(
                    'Known to social service in regards to children and valid DBS')

                return valid_DBS

    def __clear_children_not_in_home(self, app_id):

        children = Child.objects.filter(application_id=app_id)

        for child in children:

            child.delete()
            log.debug('Removed child ' + str(child.pk))
