from datetime import date

from django import forms
from govuk_forms.fields import SplitDateField
from govuk_forms.widgets import InlineRadioSelect

from application.customfields import CustomSplitDateFieldDOB, CustomSplitDateField
from application.forms import ChildminderForms
from application.models import AdultInHome


class SeriousIllness(ChildminderForms):
    """
    Form to record any serious illnesses experienced by the applicant
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem on this page'
    auto_replace_widgets = True

    choices = (
        (False, 'No'),
        (True, 'Yes')
    )

    description = forms.CharField(label='Illness',
                                  widget=forms.Textarea(), required=True,
                                  error_messages={'required': 'Please enter the name of the illness'})

    start_date = CustomSplitDateField(label='Start date', help_text='For example, 31 03 2016', error_messages={
        'required': 'Please enter the full date, including the day, month and year'}, bounds_error='Please check the date of your illness',
                                      min_value=0)

    end_date = CustomSplitDateField(label='End date', help_text='For example, 31 03 2016', error_messages={
        'required': 'Please enter the full date, including the day, month and year'}, bounds_error='Please check the date of your illness',
                                    min_value=0)

    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop('adult')
        super(SeriousIllness, self).__init__(*args, **kwargs)

    def clean_start_date(self):

        start_date = self.cleaned_data['start_date']
        today = date.today()
        date_diff = start_date - self.person.date_of_birth.date()
        if date_diff.days < 0:
            raise forms.ValidationError('Please enter a date after your date of birth')
        if len(str(start_date.year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')

        return start_date

    def clean_end_date(self):

        end_date = self.cleaned_data['end_date']

        # End dates validation uses the result from start dates clean, this is empty if an error is raised in the
        # start date view, therefore it must be searched for
        if 'start_date' in self.cleaned_data:
            start_date = self.cleaned_data['start_date']
            end_date = self.cleaned_data['end_date']
            today = date.today()
            date_diff = today - end_date
            if date_diff.days > 1825:
                raise forms.ValidationError('Please enter a date in the last five years')
            date_today_diff = today.year - end_date.year - (
                    (today.month, today.day) < (end_date.month, end_date.day))
            if len(str(end_date.year)) < 4:
                raise forms.ValidationError('Please enter the whole year (4 digits)')
            if date_today_diff < 0:
                raise forms.ValidationError('Please check the year')
            if start_date > end_date:
                raise forms.ValidationError('Please check the date of your illness')

        # If there is no 'start_date' in the clean, then just pass the end_date as their will already be an error
        return end_date


class SeriousIllnessStart(ChildminderForms):
    """
    Form to record whether the applicant has experience ANY serious illnesses, this is only asked initially
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choices = (
        (True, 'Yes'),
        (False, 'No'),

    )

    has_illnesses = forms.ChoiceField(choices=choices, widget=InlineRadioSelect, required=True,
                                      label='Have you had any serious illnesses in the past 5 years?',
                                      error_messages={'required': 'Please answer yes or no'})


class MoreSeriousIllnesses(ChildminderForms):
    """
    Form to record any more serious illnesses, asked after the start form and a successful entry of details
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choices = (
        (True, 'Yes'),
        (False, 'No')
    )

    more_illnesses = forms.ChoiceField(choices=choices, widget=InlineRadioSelect, required=True,
                                      label='Have you had any other serious illnesses in the past 5 years?',
                                      error_messages={'required': 'Please answer yes or no'})
