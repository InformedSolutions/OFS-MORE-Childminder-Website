import logging

from django.http import HttpResponseRedirect

from application.models import AdultInHome
from application.utils import build_url, get_id
from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView

# Initiate logging
log = logging.getLogger('')


class PITHMinistryView(PITHTemplateView):

    template_name = 'PITH_templates/PITH_ministry.html'
    success_url = 'PITH-DBS-Check-View'

    def get_context_data(self, **kwargs):

        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)
        military_base_adults = [adult for adult in adults if adult.military_base]

        context = {
            'adult_list': military_base_adults
        }

        log.debug('Retrieve context data')

        return super().get_context_data(**context, **kwargs)

    def post(self, request, *args, **kwargs):

        application_id = get_id(request)
        redirect_url = build_url(self.success_url, get={'id': application_id})

        log.debug('Build URL for application: ' + application_id)

        return HttpResponseRedirect(redirect_url)
