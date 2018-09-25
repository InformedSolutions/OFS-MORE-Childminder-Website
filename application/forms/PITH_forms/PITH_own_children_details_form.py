from django import forms
from govuk_forms.widgets import InlineRadioSelect
from application.forms.PITH_forms.PITH_base_forms.PITH_radio_form import PITHRadioForm


class PITHChildrenCheckForm(PITHFormView):
    choice_field_name = 'children_in_home'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Do children under 16 live in the home?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={
                'required': 'Please tell us if children under 16 live in the home?'})