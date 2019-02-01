from django import forms
from govuk_forms.widgets import InlineRadioSelect
from application.forms.PITH_forms.PITH_base_forms.PITH_radio_form import PITHRadioForm
from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect


class PITHOwnChildrenCheckForm(PITHRadioForm):
    choice_field_name = 'children_in_home'

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Are you known to council social services in regards to your own children?',
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=True,
            error_messages={
                'required': 'Please say if you are known to council social services in regards to your own children'})

    reveal_conditionally = {'own_children_not_in_home': {'True': 'reasons_known_to_social_services'}}

    def __init__(self, *args, **kwargs):

        self.base_fields['reasons_known_to_social_services'] = forms.CharField(
            label='Tell us why',
            widget=forms.Textarea,
            required=True,
            error_messages={
                'required': 'You must tell us why'})

        super().__init__(*args, **kwargs)
