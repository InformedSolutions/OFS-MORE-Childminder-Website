from django.views.generic import FormView

from application.forms import form
from application.forms.PITH_forms.PITH_declaration_form import PITHDeclarationForm
from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseTemplateView


class Declaration(FormView):
    """
    Template view to render the declaration template and navigate the user to the thank you page
    """
    template_name = 'other_people_health_check/declaration.html'
    success_url_name = 'Health-Check-Declaration'
    success_url = 'Health-Check-Thank-You'
    form_class = PITHDeclarationForm

    def form_valid(self, form):

        return super(Declaration, self).form_valid(form)

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

    def get_success_url(self):
        person_id = self.request.GET.get('person_id')
        return build_url('Health-Check-Thank-You', get={'person_id': person_id})


