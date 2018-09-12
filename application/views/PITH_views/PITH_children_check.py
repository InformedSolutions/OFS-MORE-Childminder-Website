from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm


class PITHChildrenCheckView(PITHRadioView):
    template_name = 'PITH_children_check.html'
    form_class = PITHChildrenCheckForm
    success_url = ('PITH-Children-Check', 'PITH-Children-Check')
    application_field_name = 'children_in_home'
