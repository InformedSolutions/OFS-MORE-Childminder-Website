import re
from datetime import date

from django import forms
from django.conf import settings

from ...customfields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from ...models import (AdultInHome, Application, UserDetails)
from ...utils import date_formatter
from ...business_logic import show_resend_and_change_email


class PITHAdultDetailsForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with the details'

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any on their DBS check)', required=False)
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})
    relationship = forms.CharField(label='How are they related to you?', help_text='For instance, husband or daughter',
                                   required=True,
                                   error_messages={'required': "Please say how the person is related to you"})
    email_address = forms.CharField(label='Email address',
                                    help_text='They need to answer simple questions about their health', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self._all_emails = kwargs.pop('email_list')
        super().__init__(*args, **kwargs)

        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)

            birth_day, birth_month, birth_year = date_formatter(adult_record.birth_day,
                                                                adult_record.birth_month,
                                                                adult_record.birth_year)

            self.fields['first_name'].initial = adult_record.first_name
            self.fields['middle_names'].initial = adult_record.middle_names
            self.fields['last_name'].initial = adult_record.last_name
            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]
            self.fields['relationship'].initial = adult_record.relationship
            self.fields['email_address'].initial = adult_record.email
            self.pk = adult_record.adult_id
            self.field_list = ['first_name', 'middle_names', 'last_name', 'date_of_birth', 'relationship',
                               'email_address']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match(settings.REGEX['FIRST_NAME'], first_name) is None:
            raise forms.ValidationError('First name can only have letters')
        if len(first_name) > 99:
            raise forms.ValidationError('First name must be under 100 characters long')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match(settings.REGEX['MIDDLE_NAME'], middle_names) is None:
                raise forms.ValidationError('Middle names can only have letters')
            if len(middle_names) > 99:
                raise forms.ValidationError('Middle names must be under 100 characters long')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match(settings.REGEX['LAST_NAME'], last_name) is None:
            raise forms.ValidationError('Last name can only have letters')
        if len(last_name) > 99:
            raise forms.ValidationError('Last name must be under 100 characters long')
        return last_name

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is less than 16)
        :return: string
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age < 16:
            raise forms.ValidationError('Only include details of anyone aged 16 or over on this page')
        if len(str(birth_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return birth_day, birth_month, birth_year

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        if self.cleaned_data['email_address']:
            email_address = self.cleaned_data['email_address']
            applicant_email = UserDetails.objects.get(application_id=self.application_id_local).email
            # RegEx for valid e-mail addresses
            if email_address is None or email_address == '':
                raise forms.ValidationError('Please enter an email address')
            if re.match(settings.REGEX['EMAIL'], email_address) is None:
                raise forms.ValidationError('Please enter a valid email address')
            if email_address == applicant_email:
                raise forms.ValidationError('Their email address cannot be the same as your email address')
            if self._all_emails.count(email_address) > 1:  # This is 1 because one of them is itself
                raise forms.ValidationError('Their email address cannot be the same as another person in your home')
            return email_address
        else:
            application = Application.objects.get(application_id=self.application_id_local)

            if application.application_status == 'FURTHER_INFORMATION':
                is_review = True
            else:
                is_review = False

            if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).exists():
                adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
                adult_health_check_status = adult_record.health_check_status
                if not show_resend_and_change_email(adult_health_check_status, is_review):
                    email_disabled = True
                else:
                    email_disabled = False

            if not email_disabled:
                raise forms.ValidationError('Please enter an email address')
            else:
                return self.fields['email_address'].initial