from django import forms
from govuk_forms.widgets import InlineRadioSelect, RadioSelect, SeparatedRadioSelect

from application.forms import ChildminderForms
from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect


class CurrentIllness(ChildminderForms):
    """
    Form to record current illnesses being experience by the user
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    auto_replace_widgets = True
    reveal_conditionally = {'currently_ill': {True: 'illness_details'}}


    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    currently_ill = forms.ChoiceField(choices=choices, widget=ConditionalPostInlineRadioSelect, required=True,
                                      label='Are you currently being treated by your GP, another doctor or a hospital?',
                                      error_messages={'required': 'Please answer yes or no'})

    illness_details = forms.CharField(label='Give details of your condition or illness',
                                      widget=forms.Textarea(), required=True,
                                      error_messages={'required': 'Please give details of your condition or illness'})

    def clean(self):
        cleaned_data = super().clean()
        currently_ill = cleaned_data.get('currently_ill')
        illness_details = cleaned_data.get('illness_details')

        if currently_ill == 'True':
            if illness_details is '':
                self.add_error('illness_details', 'Please give details of your condition or illness')

        return cleaned_data
