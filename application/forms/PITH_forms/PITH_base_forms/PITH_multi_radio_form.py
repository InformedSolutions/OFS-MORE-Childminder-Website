from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter
from application.business_logic import get_application


class PITHMultiRadioForm(PITHChildminderFormAdapter):
    """
    GOV.UK form for the People in the Home: generic radio button form
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'PITH_templates/PITH_error_summary.html'
    auto_replace_widgets = True

    choice_field_name = 'generic_choice_field_name'

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in the Home radio pages.
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')
        self.adult = kwargs.pop('adult')

        if 'PITH_field_name' in kwargs:
            self.PITH_field_name = kwargs.pop('PITH_field_name')
            self.pk = self.adult.pk

            super().__init__(*args, **kwargs)

            self.set_fields(self.PITH_field_name)

        elif 'application_field_name' in kwargs:
            self.application_field_name = kwargs.pop('application_field_name')
            self.pk = get_application(self.application_id, 'pk')

            super().__init__(*args, **kwargs)

            self.set_fields(self.application_field_name)

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

    def set_fields(self, field_name):
        self.fields[field_name+str(self.adult.pk)] = self.get_choice_field_data()