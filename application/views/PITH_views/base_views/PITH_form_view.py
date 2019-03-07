from django.views.generic import FormView

from application.utils import get_id, build_url


class PITHFormView(FormView):

    template_name = None
    form_class = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        return super().get_context_data(id=application_id, application_id=application_id, **kwargs)

    def get_success_url(self, base_url=None):
        base_url = base_url or self.success_url
        application_id = get_id(self.request)
        return build_url(base_url, get={'id': application_id})