from django import forms
from govuk_forms.widgets import InlineRadioSelect, RadioSelect, SeparatedRadioSelect

from application.forms import ChildminderForms
from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect


class LocalAuthorities(ChildminderForms):
    """
    Form to record names, births, and addresses of known children to the local authority
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    auto_replace_widgets = True
    reveal_conditionally = {'known_to_council': {True: 'children_details'}}


    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    known_to_council = forms.ChoiceField(choices=choices, widget=ConditionalPostInlineRadioSelect, required=True,
                                      label='Are you known to your council in regards to your own children?',
                                      error_messages={'required': 'Please answer yes or no'})

    children_details = forms.CharField(label='Enter the names, birth dates and addresses of your children',
                                      widget=forms.Textarea(), required=True,
                                      error_messages={'required': 'Please give the names, birth dates and addresses of your children'})

    def clean(self):
        cleaned_data = super().clean()
        known_to_council = cleaned_data.get('known_to_council')
        children_details = cleaned_data.get('children_details')

        if known_to_council == 'True':
            if children_details is '':
                self.add_error('children_details', 'Please give the names, birth dates and addresses of your children')

        return cleaned_data
