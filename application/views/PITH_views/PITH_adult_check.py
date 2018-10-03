from django.http import HttpResponseRedirect

from application.business_logic import get_application
from application.forms.PITH_forms.PITH_adult_check_form import PITHAdultCheckForm
from application.models import AdultInHome
from application.utils import get_id
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView


class PITHAdultCheckView(PITHRadioView):
    template_name = 'PITH_templates/PITH_adult_check.html'
    form_class = PITHAdultCheckForm
    success_url = ('PITH-Adult-Details-View', 'PITH-Children-Check-View')
    application_field_name = 'adults_in_home'

    def form_valid(self, form):
        application_id = get_id(self.request)

        super().update_db(application_id)

        choice_bool = get_application(application_id, self.application_field_name)

        context = {
            'id': get_id(self.request)
        }

        if choice_bool:
            num_adults = len(AdultInHome.objects.filter(application_id=application_id))

            adults_context = {
                'adults': num_adults,
                'remove': 0
            }
            context.update(adults_context)
        else:
            self.__clear_adults(application_id)

        return HttpResponseRedirect(self.get_success_url(get=context))

    def __clear_adults(self, app_id):
        adults = AdultInHome.objects.filter(application_id=app_id)

        for adult in adults:
            adult.delete()
