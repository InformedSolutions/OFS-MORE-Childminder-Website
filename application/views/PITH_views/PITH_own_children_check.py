import logging

from django.http import HttpResponseRedirect

from application.business_logic import get_application, update_application, awaiting_pith_dbs_action_from_user, \
    find_dbs_status
from application.forms.PITH_forms.PITH_base_forms.PITH_own_children_check_form import PITHOwnChildrenCheckForm
from application.models import AdultInHome, Child
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView

# Initiate logging
log = logging.getLogger('')


class PITHOwnChildrenCheckView(PITHRadioView):
    template_name = 'PITH_templates/PITH_own_children_check.html'
    form_class = PITHOwnChildrenCheckForm
    success_url = ('PITH-Own-Children-Details-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'own_children_not_in_home'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for caching info obtained from dbs lookup
        self.is_awaiting_user_pith_dbs_action = None

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

        yes_choice, no_yes_choice, no_no_choice = self.success_url
        choice_bool = get_application(app_id, self.application_field_name)

        if choice_bool:

            log.debug('There are own children not living in the home')

            return yes_choice

        else:

            # Does user still need to take action wrt PITH DBS checks?
            if self.get_awaiting_user_pith_dbs_action(app_id):

                log.debug('There are own children not living in the home and adults with neither an Ofsted DBS check '
                          'nor a number on the DBS update service')

                return no_yes_choice

            else:

                log.debug('There are own children not living in the home and adults with either an Ofsted DBS check '
                          'or a number on the DBS update service')

                return no_no_choice

    def __clear_children_not_in_home(self, app_id):

        children = Child.objects.filter(application_id=app_id)

        for child in children:

            child.delete()
            log.debug('Removed child ' + str(child.pk))

    def get_awaiting_user_pith_dbs_action(self, application_id):

        if self.is_awaiting_user_pith_dbs_action is not None:
            return self.is_awaiting_user_pith_dbs_action

        result = awaiting_pith_dbs_action_from_user(
            find_dbs_status(adult.dbs_certificate_number, adult, adult.capita, adult.on_update)
            for adult in AdultInHome.objects.filter(application_id=application_id))

        self.is_awaiting_user_pith_dbs_action = result
        return result
