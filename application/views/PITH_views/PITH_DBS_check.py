from application.utils import get_id
from application.models import AdultInHome
from application.views.PITH_views.base_views.PITH_multi_radio_view import PITHMultiRadioView
from application.forms.PITH_forms.PITH_DBS_check_form import PITHDBSCheckForm


class PITHDBSCheckView(PITHMultiRadioView):
    template_name = 'PITH_templates/PITH_DBS_check.html'
    form_class = PITHDBSCheckForm
    success_url = ('PITH-Post-View', 'PITH-Apply-View', 'PITH-Children-Check-View')
    capita_field = 'capita'
    dbs_field = 'dbs_certificate_number'
    on_update_field = 'on_update'

    def get_form_kwargs(self, adult=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        application_id = get_id(self.request)

        context = {
            'id': application_id,
            'adult': adult,
            'capita_field': self.capita_field,
            'dbs_field': self.dbs_field,
            'on_update_field': self.on_update_field
        }

        return super().get_form_kwargs(context)

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

        initial_context = {}
        for adult in adults:
            initial_context.update({
                self.capita_field + str(adult.pk): adult.capita,
                self.dbs_field + str(adult.pk): adult.dbs_certificate_number,
                self.on_update_field + str(adult.pk): adult.on_update,
                self.dbs_field + "_no_update" + str(adult.pk): adult.dbs_certificate_number
            })

        return initial_context

    def get_choice_url(self, app_id):
        adults = AdultInHome.objects.filter(application_id=app_id)

        yes_choice, no_yes_choice, no_no_choice = self.success_url

        if any(adult.on_update for adult in adults):
            return yes_choice
        else:
            if any(not adult.capita and not adult.on_update for adult in adults):
                return no_yes_choice
            else:
                return no_no_choice
