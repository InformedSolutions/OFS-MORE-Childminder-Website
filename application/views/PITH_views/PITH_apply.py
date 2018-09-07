from application.views.PITH_views.base_views.PITH_template_view import PITHTemplateView


class PITHApplyView(PITHTemplateView):
    template_name = 'PITH_apply.html'
    success_url = 'PITH-Children-Question-View'