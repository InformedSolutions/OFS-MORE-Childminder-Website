from django.views.generic import FormView

from application.utils import get_id, build_url


class PITHFormView(FormView):
    template_name = None
    form_class = None
    success_url = None

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)

        return super().get_context_data(id=application_id, application_id=application_id, **kwargs)

    def post(self, request, *args, **kwargs):
        application_id = request.GET.get('id')
        redirect_url = build_url(self.success_url, get={'id': application_id})

        return super().post(request, *args, **kwargs)