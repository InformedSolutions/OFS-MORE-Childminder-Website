from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm


class PITHOwnChildrenManualView(PITHRadioView):
    template_name = 'PITH_templates/PITH_children_check.html'
    form_class = PITHChildrenCheckForm
    success_url = ('PITH-Children-Details-View', 'PITH-Own-Children-Check-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'children_in_home'