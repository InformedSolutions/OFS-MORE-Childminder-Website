from django import forms
from govuk_forms.widgets import InlineRadioSelect
from application.forms.PITH_forms.PITH_base_forms.PITH_radio_form import PITHRadioForm


class PITHOwnChildrenCheckForm(PITHRadioForm):
    choice_field_name = 'children_in_home'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Do you have children of your own who are under 16 and do not live with you?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={
                'required': 'Please say if you have children of your own who are under 16 and do not live with you'})