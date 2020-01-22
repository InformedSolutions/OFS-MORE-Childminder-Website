from django import forms

from application.forms import ChildminderForms
from application.widgets import ConditionalPostInlineRadioSelect


class LocalAuthorities(ChildminderForms):
    """
    Form to record names, births, and addresses of known children to the local authority
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    auto_replace_widgets = True
    reveal_conditionally = {'known_to_council': {True: 'reasons_known_to_council_health_check'}}

    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    known_to_council = forms.ChoiceField(
        choices=choices,
        widget=ConditionalPostInlineRadioSelect,
        required=True,
        label='Are you known to council social services in regards to your own children?',
        error_messages={'required': 'Please say if you are known to council social services '
                                    'in regards to your own children'}
    )

    reasons_known_to_council_health_check = forms.CharField(
        label='Tell us why',
        widget=forms.Textarea(),
        required=True,
        error_messages={'required': 'You must tell us why'}
    )

    def clean(self):
        cleaned_data = super().clean()
        known_to_council = cleaned_data.get('known_to_council')
        reasons_known_to_council_health_check = cleaned_data.get('reasons_known_to_council_health_check')

        if known_to_council == 'True':
            if reasons_known_to_council_health_check is '':
                self.add_error('reasons_known_to_council_health_check',
                               'Are you known to council social services in regards to your own children?')

        return cleaned_data
