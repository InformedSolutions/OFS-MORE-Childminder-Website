from django.http import HttpResponseRedirect

from application.business_logic import get_application
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_form_view import PITHFormView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm
from application.views.your_children import your_children_address_selection


def PITHOwnChildrenPostcodeView(request):
    return your_children_address_selection(request)