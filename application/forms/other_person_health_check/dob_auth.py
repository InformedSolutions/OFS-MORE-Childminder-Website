from datetime import date

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from application.customfields import CustomSplitDateFieldDOB, CustomSplitDateField
from application.forms.childminder import ChildminderForms
from govuk_forms.fields import SplitDateField

from application.models import AdultInHome


class DateOfBirthAuthentication(ChildminderForms):
    """
    GOV.UK form for the health-check/birth-date page
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem with your date of birth'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': 'Please enter the full date, including the day, month and year'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        # Both passed from get_form_kwargs method
        self.valid_dob = kwargs.pop('date_of_birth')
        self.times_wrong = kwargs.pop('times_wrong')

        super(DateOfBirthAuthentication, self).__init__(*args, **kwargs)

    def clean_date_of_birth(self):
        """
        This clean is used to validate the entered date of birth against the date of birth stored against the adult in
        home
        :return: The date of birth (in a date object format) or an error message
        """
        # Standard Clean
        date_of_birth = self.cleaned_data['date_of_birth']
        if date_of_birth != self.valid_dob:
            # See CCN3-1014 for definition on different errors for amount of times entered incorrectly
            if self.times_wrong < 3:
                raise forms.ValidationError('Your date of birth does not match what the applicant gave us')
            else:
                raise forms.ValidationError('Please contact the applicant and ask them to check your DOB')

        today = date.today()
        date_today_diff = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if len(str(date_of_birth.year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        if date_today_diff < 0:
            raise forms.ValidationError('Please check the year')

        return date_of_birth
