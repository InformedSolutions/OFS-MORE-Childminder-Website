import logging

from django.http import HttpResponseRedirect

from application.business_logic import get_application, awaiting_pith_dbs_action_from_user, find_dbs_status
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView

# Initiate logging
log = logging.getLogger('')


class PITHChildrenCheckView(PITHRadioView):

    template_name = 'PITH_templates/PITH_children_check.html'
    form_class = PITHChildrenCheckForm
    success_url = ('PITH-Children-Details-View', 'PITH-Own-Children-Check-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'children_in_home'

    def form_valid(self, form):

        application_id = get_id(self.request)

        super().update_db(application_id)

        choice_bool = get_application(application_id, self.application_field_name)

        log.debug('Set answer to children in the home for application: ' + application_id)

        context = {
            'id': get_id(self.request)
        }

        if choice_bool:

            num_children = len(ChildInHome.objects.filter(application_id=application_id))

            log.debug('Retrieve the number of adults in the home: ' + str(num_children))

            adults_context = {
                'children': num_children,
                'remove': 0
            }

            context.update(adults_context)

        else:

            # Remove any existing children details.
            self.__clear_children(application_id)

            log.debug('Children in the home cleared down for application: ' + application_id)

        return HttpResponseRedirect(self.get_success_url(get=context))

    def get_choice_url(self, app_id):

        yes_choice, no_yes_choice, no_no_yes_choice, no_no_no_choice = self.success_url
        choice_bool = get_application(app_id, self.application_field_name)

        # Assert if the applicant's home address is the same as their childcare address
        home_address = ApplicantHomeAddress.objects.get(application_id=app_id, current_address=True)
        care_in_home = home_address.current_address and home_address.childcare_address

        if choice_bool:

            log.debug('Set children in the home to true for application: ' + app_id)

            return yes_choice

        else:

            if care_in_home:

                log.debug('Set caring at home address to true for application: ' + app_id)

                return no_yes_choice

            else:

                # Does user still need to take action wrt PITH DBS checks?
                if self.get_awaiting_user_pith_dbs_action(app_id):

                    log.debug('Set caring at home address to false and adults in home for application: ' + app_id)

                    return no_no_yes_choice

                else:

                    log.debug('Set caring at home address to false and no adults in home for application: ' + app_id)

                    return no_no_no_choice

    def __clear_children(self, app_id):

        children = ChildInHome.objects.filter(application_id=app_id)

        for child in children:

            child.delete()
            log.debug('Removing child ' + str(child.pk))

    def get_awaiting_user_pith_dbs_action(self, application_id):

        result = awaiting_pith_dbs_action_from_user(
            find_dbs_status(adult, adult)
            for adult in AdultInHome.objects.filter(application_id=application_id))

        return result
