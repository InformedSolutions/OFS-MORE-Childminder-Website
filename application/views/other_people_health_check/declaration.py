from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseTemplateView


class Declaration(BaseTemplateView):
    """
    Template view to render the declaration template and navigate the user to the thank you page
    """

    template_name = 'other_people_health_check/declaration.html'
    success_url_name = 'Health-Check-Declaration'

    def get_context_data(self, **kwargs):
        """
        Returns the person id and the success url for the template
        :param kwargs:
        :return:
        """
        context = super().get_context_data()

        context['person_id'] = self.request.GET.get('person_id')
        context['thank_you_url'] = build_url('Health-Check-Thank-You', get={'person_id': context['person_id']})

        return context