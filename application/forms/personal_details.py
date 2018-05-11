from datetime import date

from django import forms

from application.customfields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ApplicantName,
                                ApplicantPersonalDetails)
from application.utils import date_formatter


class PersonalDetailsGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class PersonalDetailsNameForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: name page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', error_messages={'required': 'Please enter your first name'})
    middle_names = forms.CharField(label='Middle names (if you have any on your DBS check)', required=False)
    last_name = forms.CharField(label='Last name', error_messages={'required': 'Please enter your last name'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: name form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsNameForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            personal_detail_id = ApplicantPersonalDetails.objects.get(
                application_id=self.application_id_local).personal_detail_id
            applicant_name_record = ApplicantName.objects.get(personal_detail_id=personal_detail_id)
            self.fields['first_name'].initial = applicant_name_record.first_name
            self.fields['middle_names'].initial = applicant_name_record.middle_names
            self.fields['last_name'].initial = applicant_name_record.last_name
            self.pk = applicant_name_record.name_id
            self.field_list = ['first_name', 'middle_names', 'last_name']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if len(first_name) > 100:
            raise forms.ValidationError('First name must be under 100 characters long')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if len(middle_names) > 100:
                raise forms.ValidationError('Middle names must be under 100 characters long')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if len(last_name) > 100:
            raise forms.ValidationError('Last name must be under 100 characters long')
        return last_name


class PersonalDetailsDOBForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: date of birth page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': 'Please enter the full date, including the day, month and year'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: date of birth form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsDOBForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).exists():
            personal_details_record = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)

            birth_day, birth_month, birth_year = date_formatter(personal_details_record.birth_day,
                                                                personal_details_record.birth_month,
                                                                personal_details_record.birth_year)

            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]
            self.pk = personal_details_record.personal_detail_id
            self.field_list = ['date_of_birth']

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is less than 18)
        :return: birth day, birth month, birth year
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age < 18:
            raise forms.ValidationError('You must be 18 or older to be a childminder')
        date_today_diff = today.year - applicant_dob.year - (
                (today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if len(str(birth_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        if date_today_diff < 0:
            raise forms.ValidationError('Please check the year')

        return birth_day, birth_month, birth_year
