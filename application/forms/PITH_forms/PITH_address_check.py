from django import forms
from govuk_forms.widgets import InlineRadioSelect

from application.forms.PITH_forms.PITH_base_forms.PITH_multi_radio_form import PITHMultiRadioForm

class PITHAddressDetailsCheckForm(PITHMultiRadioForm):

    choice_field_name = 'adult_in_home_address'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Is this where they live?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={'required': 'Please say if this is where they live'})

