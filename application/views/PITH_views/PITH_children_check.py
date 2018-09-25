from django.http import HttpResponseRedirect

from application.business_logic import get_application
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm


class PITHChildrenCheckView(PITHRadioView):
    template_name = 'PITH_templates/PITH_children_check.html'
    form_class = PITHChildrenCheckForm
    success_url = ('PITH-Children-Details-View', 'PITH-Own-Children-Check-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'children_in_home'

    def form_valid(self, form):
        application_id = get_id(self.request)

        super().update_db(application_id)

        choice_bool = get_application(application_id, self.application_field_name)

        context = {
            'id': get_id(self.request)
        }

        if choice_bool:
            num_children = len(ChildInHome.objects.filter(application_id=application_id))

            adults_context = {
                'children': num_children,
                'remove': 0
            }
            context.update(adults_context)

        return HttpResponseRedirect(self.get_success_url(get=context))

    def get_choice_url(self, app_id):
        yes_choice, no_yes_choice, no_no_yes_choice, no_no_no_choice = self.success_url
        choice_bool = get_application(app_id, self.application_field_name)
        care_in_home = ApplicantHomeAddress(app_id, 'childcare_address')
        adults = AdultInHome.objects.filter(application_id=app_id)

        if choice_bool:
            return yes_choice
        else:
            if care_in_home:
                return no_yes_choice
            else:
                if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                    return no_no_yes_choice
                else:
                    return no_no_no_choice
