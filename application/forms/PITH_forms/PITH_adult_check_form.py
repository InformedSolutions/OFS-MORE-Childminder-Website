from django import forms
from govuk_forms.widgets import InlineRadioSelect
from application.forms.PITH_forms.PITH_base_forms.PITH_radio_form import PITHRadioForm


class PITHAdultCheckForm(PITHRadioForm):
    choice_field_name = 'adults_in_home'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Does anyone aged 16 or over live or work in the home?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={'required': 'Please tell us if anyone aged 16 or over lives or works in the home'})