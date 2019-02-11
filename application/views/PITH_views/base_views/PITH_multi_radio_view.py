from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.base import TemplateResponseMixin

from application.utils import build_url, get_id
from application.business_logic import update_application, get_application
from .PITH_multi_form_view import PITHMultiFormView


class PITHMultiRadioView(PITHMultiFormView):

    template_name = None
    form_class = None
    success_url = None
    field_name = None

    def get_success_url(self, get=None):
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)

        if not get:
            return build_url(self.get_choice_url(application_id), get={'id': application_id})
        else:
            return build_url(self.get_choice_url(application_id), get=get)

    def get_choice_url(self, app_id):
        raise ImproperlyConfigured(
            "No URL to redirect to, please implement get_choice_url")