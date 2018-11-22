from django.http import HttpResponseRedirect

from application.utils import build_url, get_id

from django.views.generic import TemplateView


class PITHTemplateView(TemplateView):
    template_name = None
    success_url = None
    condition = None

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)

        return super().get_context_data(application_id=application_id, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = get_id(request)
        redirect_url = build_url(self.success_url, get={'id': application_id})

        return HttpResponseRedirect(redirect_url)
