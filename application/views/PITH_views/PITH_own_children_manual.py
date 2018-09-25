from django.http import HttpResponseRedirect

from application.business_logic import get_application
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_radio_view import PITHRadioView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm


class PITHOwnChildrenManualView(PITHRadioView):
    template_name = 'PITH_templates/PITH_children_check.html'
    form_class = PITHChildrenCheckForm
    success_url = ('PITH-Children-Details-View', 'PITH-Own-Children-Check-View', 'Task-List-View', 'PITH-Summary-View')
    application_field_name = 'children_in_home'