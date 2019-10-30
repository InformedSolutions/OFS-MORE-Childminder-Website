from django import forms
from govuk_forms.widgets import InlineRadioSelect

#from application.forms.PITH_forms.PITH_base_forms.PITH_multi_radio_form import PITHMultiRadioForm

from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter

class PITHAddressDetailsCheckForm(PITHChildminderFormAdapter):
    #choice_field_name = 'adult_in_home_address'

    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'PITH_templates/PITH_error_summary.html'
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):
        self.application_id = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.street_line1 = kwargs.pop('street_line1')
        self.street_line2 = kwargs.pop('street_line2')
        self.town = kwargs.pop('town')
        self.county = kwargs.pop('county')
        self.postcode = kwargs.pop('postcode')
        self.adult_in_home_address = kwargs.pop('PITH_field_name')


        super().__init__(*args, **kwargs)

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Is this where they live?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={'required': 'Please say if this is where they live'})

