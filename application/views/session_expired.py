from django.views.generic import TemplateView


class SessionExpiredView(TemplateView):
    template_name = 'session-expired.html'
