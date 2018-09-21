from django.http import HttpResponseRedirect

from application.business_logic import get_application
from application.models import AdultInHome

from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_adult_check_form import PITHAdultCheckForm
from application.utils import get_id


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

        return HttpResponseRedirect(self.get_success_url(get=context))


