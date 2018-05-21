from datetime import date

from django import forms
from govuk_forms.fields import SplitDateField
from govuk_forms.widgets import InlineRadioSelect

from application.customfields import CustomSplitDateField
from application.forms import ChildminderForms


class HospitalAdmissionStart(ChildminderForms):
    """
    Form to record whether the applicant has experienced ANY hospital admissions
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    has_illnesses = forms.ChoiceField(choices=choices, widget=InlineRadioSelect, required=True,
                                      label='Have you been admitted to hospital in the last two years?',
                                      error_messages={'required': 'Please answer yes or no'})


class HospitalAdmission(ChildminderForms):
    """
    Form to record any hospital admission of the applicant
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    illness_details = forms.CharField(label='Tell us why you were admitted',
                                      widget=forms.Textarea(), required=True,
                                      error_messages={'required': 'Tell us why you were admitted'})

    start_date = CustomSplitDateField(label='Date you were admitted', help_text='For example, 31 03 2016', error_messages={
        'required': 'Please enter the full date, including the day, month and year'}, bounds_error='Please check the date of your illness')

    end_date = CustomSplitDateField(label='Date you were discharged', help_text='For example, 31 03 2016', error_messages={
        'required': 'Please enter the full date, including the day, month and year'}, bounds_error='Please check the date of your illness')

    def clean_illness_details(self):

        illness_details = self.cleaned_data['illness_details']
        if len(illness_details) > 150:
            raise forms.ValidationError('The reason for your admission must be less than 150 characters long')

        return illness_details

    def clean_start_date(self):

        start_date = self.cleaned_data['start_date']
        today = date.today()
        date_diff = today-start_date
        # date diff is a timedelta object with a days element, checked against 2 years ago (in days) as in CCN3-1135
        if date_diff.days > 730:
            raise forms.ValidationError('Please enter a date in the last two years')
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
            date_today_diff = today.year - end_date.year - (
                    (today.month, today.day) < (end_date.month, end_date.day))
            date_diff = today - end_date
            # Same as start date
            if date_diff.days > 730:
                raise forms.ValidationError('Please enter a date in the last two years')
            if date_today_diff < 0:
                raise forms.ValidationError('Please check the year')
            if start_date > end_date:
                raise forms.ValidationError('Please check the date of your illness')

        # If there is no 'start_date' in the clean, then just pass the end_date as their will already be an error
        return end_date


class MoreHospitalAdmissions(ChildminderForms):
    """
    Form to ask whether the applicant has any more hospital admissions, this is never saved
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    more_illnesses = forms.ChoiceField(choices=choices, widget=InlineRadioSelect, required=True,
                                       label='Have you been admitted to hospital any other times in the past 2 years?',
                                       error_messages={'required': 'Please answer yes or no'})