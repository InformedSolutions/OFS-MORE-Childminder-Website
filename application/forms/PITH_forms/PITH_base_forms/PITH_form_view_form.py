from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter
from application.business_logic import get_adult_in_home, get_application


class PITHRadioForm(PITHChildminderFormAdapter):
    """
    GOV.UK form for the Criminal record check: generic radio button form
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choice_field_name = 'generic_choice_field_name'

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in the Home radio pages.
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')

        if 'PITH_field_name' in kwargs:
            self.PITH_field_name = kwargs.pop('PITH_field_name')
            self.pk = get_adult_in_home(self.application_id, 'pk')

            super().__init__(*args, **kwargs)

            self.fields[self.PITH_field_name] = self.get_choice_field_data()

        elif 'application_field_name' in kwargs:
            self.application_field_name = kwargs.pop('application_field_name')
            self.pk = get_application(self.application_id, 'pk')

            super().__init__(*args, **kwargs)

            self.fields[self.application_field_name] = self.get_choice_field_data()

        else:
            raise ValueError('No x_field_name kwarg could be found.')

        self.field_list = [*self.fields]

    def get_options(self):
        options = (
            ('True', 'Yes'),
            ('False', 'No')
        )
        return options

    def get_choice_field_data(self):
        raise NotImplementedError("No choice field was inherited.")