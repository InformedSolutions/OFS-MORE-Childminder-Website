from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView
from application.utils import build_url
from django.http import HttpResponseRedirect


class PITHMinistryView(PITHTemplateView):
    template_name = 'PITH_ministry.html'
    success_url = 'PITH-DBS-Check-View'