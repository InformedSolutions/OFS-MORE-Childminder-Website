import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

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
    success_url = ('PITH-Summary-View', 'Task-List-View')
    application_known_field = 'known_to_social_services_pith'
    application_reasons_known_field = 'reasons_known_to_social_services_pith'

    def get(self, request, *args, **kwargs):
        form = self.get_form_class()(id=get_id(self.request), initial=self.get_initial())
        return render(request, self.template_name, context={'form': form})

    def get_initial(self):
        application_id = get_id(self.request)
        initial = {}

        application_known_field = get_application(application_id, self.application_known_field)
        initial[self.application_known_field] = application_known_field

        application_reasons_known_field = get_application(application_id, self.application_reasons_known_field)
        initial[self.application_reasons_known_field] = application_reasons_known_field

        return initial

    def post(self, request, *args, **kwargs):
        application_id = get_id(self.request)
        form_submission = PITHOwnChildrenCheckForm(data=request.POST, id=application_id)

        if form_submission.is_valid():
            return self.form_valid(form_submission)
        else:
            return render(request, self.template_name, context={'form': form_submission})

    def form_valid(self, form):
        log.debug('Checking if form is valid')

        application_id = get_id(self.request)

        self.update_db(application_id)

        context = {
            'id': get_id(self.request)
        }

        return HttpResponseRedirect(self.get_success_url(get=context))

    def get_choice_url(self, app_id):

        valid_DBS, invalid_DBS = self.success_url
        choice_bool = get_application(app_id, self.application_known_field)

        if choice_bool:

            # Does user still need to take action wrt PITH DBS checks?
            if self.get_awaiting_user_pith_dbs_action(app_id):

                log.debug('Known to social service in regards to children and invalid DBS')

                return invalid_DBS

            else:
                log.debug(
                    'Known to social service in regards to children and valid DBS')

                return valid_DBS

        else:

            # Does user still need to take action wrt PITH DBS checks?
            if self.get_awaiting_user_pith_dbs_action(app_id):

                log.debug(
                    'Not known to social service in regards to children and all invalid DBS')

                return invalid_DBS

            else:
                log.debug(
                    'Known to social service in regards to children and valid DBS')

                return valid_DBS

    def update_db(self, app_id):
        # Update the task status to 'IN_PROGRESS' if task status not 'DONE', 'FLAGGED' or 'WAITING'.
        application_id = get_id(self.request)
        people_in_home_status = get_application(application_id, 'people_in_home_status')

        if people_in_home_status not in ['COMPLETED', 'WAITING']:
            update_application(app_id, 'people_in_home_status', 'IN_PROGRESS')

        update_bool = self.request.POST.get(self.application_known_field) == 'True'
        update_application(app_id, self.application_known_field, update_bool)

        application_reasons_known = self.request.POST.get(self.application_reasons_known_field)
        update_application(app_id, self.application_reasons_known_field, application_reasons_known)

    def get_awaiting_user_pith_dbs_action(self, application_id):

        result = awaiting_pith_dbs_action_from_user(
            find_dbs_status(adult, adult)
            for adult in AdultInHome.objects.filter(application_id=application_id))

        return result
