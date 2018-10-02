from django.http import HttpResponseRedirect

from application.business_logic import get_application, update_application
from application.forms.PITH_forms.PITH_base_forms.PITH_own_children_check_form import PITHOwnChildrenCheckForm
from application.models import AdultInHome, Child
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView


class PITHOwnChildrenCheckView(PITHRadioView):
    template_name = 'PITH_templates/PITH_own_children_check.html'
    form_class = PITHOwnChildrenCheckForm
    success_url = ('PITH-Own-Children-Details-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'own_children_not_in_home'

    def form_valid(self, form):
        application_id = get_id(self.request)

        super().update_db(application_id)

        choice_bool = get_application(application_id, self.application_field_name)

        context = {
            'id': get_id(self.request)
        }

        if choice_bool:
            num_children = len(Child.objects.filter(application_id=application_id))

            adults_context = {
                'children': num_children,
                'remove': 0
            }
            context.update(adults_context)
        else:
            # Remove any existing children not in the home.
            self.__clear_children_not_in_home(application_id)

        return HttpResponseRedirect(self.get_success_url(get=context))

    def get_choice_url(self, app_id):
        yes_choice, no_yes_choice, no_no_choice = self.success_url
        choice_bool = get_application(app_id, self.application_field_name)
        adults = AdultInHome.objects.filter(application_id=app_id)

        if choice_bool:
            return yes_choice
        else:
            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                return no_yes_choice
            else:
                return no_no_choice

    def __clear_children_not_in_home(self, app_id):
        children = Child.objects.filter(application_id=app_id)

        for child in children:
            child.delete()
