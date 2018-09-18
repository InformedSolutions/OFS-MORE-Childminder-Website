from django import forms
from govuk_forms.widgets import InlineRadioSelect

from application.forms.PITH_forms.PITH_base_forms.PITH_multi_radio_form import PITHMultiRadioForm


class PITHMilitaryForm(PITHMultiRadioForm):
    choice_field_name = 'military_base'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Have they lived or worked on a British military base outside of the UK in the last 5 years?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={'required': 'Please say if this person has lived or worked on a British military base outside of the UK in the last 5 years'})
