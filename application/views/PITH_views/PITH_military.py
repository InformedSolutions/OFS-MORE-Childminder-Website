from django.http import HttpResponseRedirect

from application.utils import build_url, get_id
from application.models import AdultInHome
from application.views.PITH_views.base_views.PITH_multi_radio_view import PITHMultiRadioView
from application.forms.PITH_forms.PITH_military_form import PITHMilitaryForm


class PITHMilitaryView(PITHMultiRadioView):
    template_name = 'PITH_templates/PITH_military.html'
    form_class = PITHMilitaryForm
    success_url = ('PITH-Ministry-View', 'PITH-DBS-Check-View')
    PITH_field_name = 'military_base'

    def get_form_kwargs(self, adult=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'PITH_field_name': self.PITH_field_name,
            'adult': adult
        }

        return super().get_form_kwargs(context)

    def get_success_url(self, get=None):
        """
        This view redirects to three potential phases.
        This method is overridden to return those specific three cases.
        :param get:
        :return:
        """
        application_id = get_id(self.request)

        if not get:
            return build_url(self.get_choice_url(application_id), get={'id': application_id})
        else:
            return build_url(self.get_choice_url(application_id), get=get)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        for adult in adults:
            military_base_bool = self.request.POST.get(self.PITH_field_name+str(adult.pk))
            setattr(adult, self.PITH_field_name, military_base_bool)
            adult.save()

        return super().form_valid(form)

    def get_form_list(self):
        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        form_list = [self.form_class(**self.get_form_kwargs(adult=adult))
                     for adult in adults]

        sorted_form_list = \
            sorted(form_list, key=lambda form: form.adult.adult)

        return sorted_form_list

    def get_initial(self):
        application_id = get_id(self.request)

        adults = AdultInHome.objects.filter(application_id=application_id)

        initial_context = {self.PITH_field_name+str(adult.pk): adult.military_base
                           for adult in adults}

        return initial_context

    def get_choice_url(self, app_id):
        adults = AdultInHome.objects.filter(application_id=app_id)
        yes_choice, no_choice = self.success_url

        return yes_choice if any(adult.military_base for adult in adults) else no_choice
