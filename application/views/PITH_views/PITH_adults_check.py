from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_adult_check_form import PITHAdultCheckForm


class PITHAdultCheckView(PITHRadioView):
    template_name = 'PITH_adults_check.html'
    form_class = PITHAdultCheckForm
    success_url = ('PITH-Adult-Details', 'PITH-Children-Check')
    application_field_name = 'adults_in_home'
