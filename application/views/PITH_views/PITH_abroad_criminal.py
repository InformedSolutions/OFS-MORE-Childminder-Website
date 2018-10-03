from django.http import HttpResponseRedirect

from application.business_logic import get_childcare_register_type
from application.models import AdultInHome
from application.utils import build_url, get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView


class PITHAbroadCriminalView(PITHTemplateView):
    template_name = 'PITH_templates/PITH_abroad_criminal.html'
    success_url = ('PITH-DBS-Check-View', 'PITH-Military-View')

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)
        lived_abroad_adults = [adult for adult in adults if adult.lived_abroad]

        context = {
            'adult_list': lived_abroad_adults
        }

        return super().get_context_data(**context, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = get_id(request)

        yes_url, no_url = self.success_url

        if self.check_childcare_register_only(application_id):
            redirect_url = build_url(yes_url, get={'id': application_id})
        else:
            redirect_url = build_url(no_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)

    @staticmethod
    def check_childcare_register_only(app_id):
        childcare_register_status, childcare_register_cost = get_childcare_register_type(app_id)

        return 'CR' in childcare_register_status and 'EYR' not in childcare_register_status
