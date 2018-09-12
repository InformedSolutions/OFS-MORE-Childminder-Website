from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView


class PITHGuidanceView(PITHTemplateView):
    template_name = 'PITH_templates/PITH_guidance.html'
    success_url = 'PITH-Adult-Check-View'
