from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView
from application.utils import build_url
from django.http import HttpResponseRedirect


class PITHPostView(PITHTemplateView):
    template_name = 'PITH_abroad_criminal.html'
    success_url = ('PITH-DBS-Check-View', 'PITH-Military-View')

    def post(self, request, *args, **kwargs):
        application_id = get_id(request)

        yes_url, no_url = self.success_url

        if self.condition():
            redirect_url = build_url(yes_url, get={'id': application_id})
        else:
            redirect_url = build_url(no_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)

    def condition(self):
        #Temp
        return True