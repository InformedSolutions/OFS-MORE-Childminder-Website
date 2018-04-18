"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

import re

from datetime import date
from django import forms
from django.conf import settings
from govuk_forms.forms import GOVUKForm
from govuk_forms.widgets import CheckboxSelectMultiple, InlineRadioSelect, RadioSelect, NumberInput
from govuk_forms.fields import SplitDateField

from application.customfields import TimeKnownField, SelectDateWidget, ExpirySplitDateField, CustomSplitDateFieldDOB, \
    CustomSplitDateField, ExpirySplitDateWidget
from application.forms.childminder import ChildminderForms
from application.models import (AdultInHome,
                                ApplicantHomeAddress,
                                ApplicantName,
                                ApplicantPersonalDetails,
                                Application,
                                ChildcareType,
                                ChildInHome,
                                CriminalRecordCheck,
                                EYFS,
                                FirstAidTraining,
                                HealthDeclarationBooklet,
                                Reference,
                                UserDetails)
from application.forms_helper import full_stop_stripper
from application.utils import date_formatter


class AccountForm(ChildminderForms):
    """
    GOV.UK form for the Account selection page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class ContactEmailForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    email_address = forms.EmailField()

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        # RegEx for valid e-mail addresses
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email_address) == 0:
            raise forms.ValidationError('Please enter an email address')
        return email_address


class ContactPhoneForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: phone page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    mobile_number = forms.CharField(label='Mobile phone number')
    add_phone_number = forms.CharField(label='Additional phone number (optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ContactPhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = UserDetails.objects.get(application_id=self.application_id_local)
            login_id = this_user.login_id
            self.fields['mobile_number'].initial = UserDetails.objects.get(login_id=login_id).mobile_number
            self.fields['add_phone_number'].initial = UserDetails.objects.get(login_id=login_id).add_phone_number
            self.pk = login_id
            self.field_list = ['mobile_number', 'add_phone_number']

    def clean_mobile_number(self):
        """
        Mobile number validation
        :return: string
        """
        mobile_number = self.cleaned_data['mobile_number']
        no_space_mobile_number = mobile_number.replace(' ', '')
        if re.match("^(07\d{8,12}|447\d{7,11})$", no_space_mobile_number) is None:
            raise forms.ValidationError('TBC')
        if len(no_space_mobile_number) > 11:
            raise forms.ValidationError('TBC')
        return mobile_number

    def clean_add_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        add_phone_number = self.cleaned_data['add_phone_number']
        no_space_add_phone_number = add_phone_number.replace(' ', '')
        if add_phone_number != '':
            if re.match("^(0\d{8,12}|447\d{7,11})$", no_space_add_phone_number) is None:
                raise forms.ValidationError('TBC')
            if len(no_space_add_phone_number) > 11:
                raise forms.ValidationError('TBC')
        return add_phone_number



class ContactSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TypeOfChildcareGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TypeOfChildcareAgeGroupsForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare task
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    CHILDCARE_AGE_CHOICES = (
        ('0-5', '0 to 5 year olds'),
        ('5-8', '5 to 7 year olds'),
        ('8over', '8 years or older'),
    )
    type_of_childcare = forms.MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple,
        choices=CHILDCARE_AGE_CHOICES,
        label='What age groups will you be caring for?',
        help_text='Tick all that apply'
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of childcare form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareAgeGroupsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildcareType.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record = ChildcareType.objects.get(application_id=self.application_id_local)
            zero_to_five_status = childcare_record.zero_to_five
            five_to_eight_status = childcare_record.five_to_eight
            eight_plus_status = childcare_record.eight_plus
            if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5', '5-8']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['0-5', '8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['5-8', '8over']
            elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['0-5']
            elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = ['5-8']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
                self.fields['type_of_childcare'].initial = ['8over']
            elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is False):
                self.fields['type_of_childcare'].initial = []
        self.fields['type_of_childcare'].error_messages = {
            'required': 'You must select at least one age group to continue with your application'}


class TypeOfChildcareRegisterForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare: register page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TypeOfChildcareOvernightCareForm(ChildminderForms):
    """
    GOV.UK form for the Type of Childcare: Overnight care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )

    overnight_care = forms.ChoiceField(label='Will you be looking after children overnight?', choices=options,
                                       widget=InlineRadioSelect, required=True,
                                       error_messages={'required': 'TBC'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of Childcare: Overnight form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareOvernightCareForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

        # If information was previously entered, display it on the form
        if ChildcareType.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record = ChildcareType.objects.get(application_id=self.application_id_local)
            self.fields['overnight_care'].initial = childcare_record.overnight_care
            self.field_list = ['overnight_care']


class EmailLoginForm(ChildminderForms):
    """
    GOV.UK form for the page to log back into an application
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    email_address = forms.EmailField()

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid e-mail address')
        return email_address


class VerifyPhoneForm(ChildminderForms):
    """
    GOV.UK form for the page to verify an SMS code
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    magic_link_sms = forms.IntegerField(label='Security code', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the SMS code verification form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.magic_link_email = kwargs.pop('id')
        super(VerifyPhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_magic_link_sms(self):
        """
        SMS code validation
        :return: string
        """
        magic_link_sms = str(self.cleaned_data['magic_link_sms']).zfill(5)

        if len(magic_link_sms)<5:
            raise forms.ValidationError('The code must be 5 digits.  You have entered fewer than 5 digits')
        if len(magic_link_sms)>5:
            raise forms.ValidationError('The code must be 5 digits.  You have entered more than 5 digits')
        if len(magic_link_sms)==0:
            raise forms.ValidationError('Please enter the 5 digit code we sent to your mobile')
        return magic_link_sms


class SecurityQuestionForm(ChildminderForms):
    """
    GOV.UK form for the page to verify an SMS code
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    answer = None
    security_answer = forms.CharField(label='')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the SMS code verification form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.answer = kwargs.pop('answer')
        super(SecurityQuestionForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_security_answer(self):
        security_answer = self.cleaned_data['security_answer']
        if len(security_answer) == 0:
            self.error = 'empty'
            raise forms.ValidationError('empty')
        elif self.answer.replace(' ','') != security_answer.replace(' ',''):
            self.error = 'wrong'
            raise forms.ValidationError('wrong')



        return security_answer


class SecurityDateForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: date of birth page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    auto_replace_widgets = True

    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980')

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: date of birth form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.day = kwargs.pop('day')
        self.month = kwargs.pop('month')
        self.year = kwargs.pop('year')
        super(SecurityDateForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_security_answer(self):
        """
        Date of birth validation (calculate if age is less than 18)
        :return: birth day, birth month, birth year
        """
        birth_day = str(self.cleaned_data['date_of_birth'].day)
        birth_month = str(self.cleaned_data['date_of_birth'].month)
        birth_year = str(self.cleaned_data['date_of_birth'].year)
        if self.day != birth_day or self.month != birth_month or self.year != birth_year:
            self.error = 'wrong'
            raise forms.ValidationError('wrong')

        if len(birth_year) == 0 or len(birth_day) == 0 or len(birth_month) == 0:
            self.error = 'empty'
            raise forms.ValidationError('empty')



        return birth_day, birth_month, birth_year


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
    middle_names = forms.CharField(label='Middle names (if you have any)', required=False)
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


class PersonalDetailsHomeAddressForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsHomeAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               current_address=True).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsHomeAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_name_and_number = forms.CharField(label='Address line 1', error_messages={
        'required': 'Please enter the first line of your address'})
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsHomeAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               current_address=True).count() > 0:
            applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)
            self.fields['street_name_and_number'].initial = applicant_home_address.street_line1
            self.fields['street_name_and_number2'].initial = applicant_home_address.street_line2
            self.fields['town'].initial = applicant_home_address.town
            self.fields['county'].initial = applicant_home_address.county
            self.fields['postcode'].initial = applicant_home_address.postcode
            self.pk = applicant_home_address.home_address_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode']

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of your address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of your address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsHomeAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsHomeAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class PersonalDetailsLocationOfCareForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: location of care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    location_of_care = forms.ChoiceField(label='Is this where you will be looking after the children?', choices=options,
                                         widget=InlineRadioSelect, required=True,
                                         error_messages={'required': 'Please answer yes or no'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: location of care form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsLocationOfCareForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            self.fields['location_of_care'].initial = ApplicantHomeAddress.objects.get(
                personal_detail_id=personal_detail_id, current_address=True).childcare_address


class PersonalDetailsChildcareAddressForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               childcare_address='True').postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsChildcareAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_name_and_number = forms.CharField(label='Address line 1',
                                             error_messages={'required': 'Please enter the first line of the address'})
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter the postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                 childcare_address='True')
            self.fields['street_name_and_number'].initial = childcare_address.street_line1
            self.fields['street_name_and_number2'].initial = childcare_address.street_line2
            self.fields['town'].initial = childcare_address.town
            self.fields['county'].initial = childcare_address.county
            self.fields['postcode'].initial = childcare_address.postcode
            self.pk = childcare_address.child_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode']

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('Please spell out the the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 100:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsChildcareAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select the address from the list'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsChildcareAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class PersonalDetailsSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class FirstAidTrainingGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class FirstAidTrainingDetailsForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_aid_training_organisation = forms.CharField(label='First aid training organisation', error_messages={
        'required': 'Please enter the title of your course'})
    title_of_training_course = forms.CharField(label='Title of training course', error_messages={
        'required': 'Please enter the title of the course'})
    course_date = CustomSplitDateFieldDOB(label='Date you completed course', help_text='For example, 31 03 2016',
                                       error_messages={
                                           'required': 'Please enter the full date, including the day, month and year'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the First aid training: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstAidTrainingDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form        
        if FirstAidTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            first_aid_record = FirstAidTraining.objects.get(application_id=self.application_id_local)

            course_day, course_month, course_year = date_formatter(first_aid_record.course_day,
                                                                   first_aid_record.course_month,
                                                                   first_aid_record.course_year)

            self.fields['first_aid_training_organisation'].initial = first_aid_record.training_organisation
            self.fields['title_of_training_course'].initial = first_aid_record.course_title
            self.fields['course_date'].initial = [course_day, course_month, course_year]
            self.pk = first_aid_record.first_aid_id
            self.field_list = ['first_aid_training_organisation', 'title_of_training_course', 'course_date']

    def clean_first_aid_training_organisation(self):
        """
        First aid training organisation validation
        :return: first aid training organisation
        """
        first_aid_training_organisation = self.cleaned_data['first_aid_training_organisation']
        if len(first_aid_training_organisation) > 50:
            raise forms.ValidationError('The title of the course must be under 50 characters')
        return first_aid_training_organisation

    def clean_title_of_training_course(self):
        """
        Title of training course validation
        :return: title of training course
        """
        title_of_training_course = self.cleaned_data['title_of_training_course']
        if len(title_of_training_course) > 50:
            raise forms.ValidationError('The title of the course must be under 50 characters long')
        return title_of_training_course

    def clean_course_date(self):
        """
        Course date validation (calculate date is in the future)
        :return: course day, course month, course year
        """
        course_day = self.cleaned_data['course_date'].day
        course_month = self.cleaned_data['course_date'].month
        course_year = self.cleaned_data['course_date'].year
        course_date = date(course_year, course_month, course_day)
        today = date.today()
        date_today_diff = today.year - course_date.year - (
                (today.month, today.day) < (course_date.month, course_date.day))
        if date_today_diff < 0:
            raise forms.ValidationError('Please enter a past date')
        if len(str(course_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return course_day, course_month, course_year


class FirstAidTrainingDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration = forms.BooleanField(label='I will show my first aid certificate to the inspector', required=True,
                                     error_messages={
                                         'required': 'You must agree to show your certificate to the inspector'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the First aid training: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstAidTrainingDeclarationForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if FirstAidTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            first_aid_record = FirstAidTraining.objects.get(application_id=self.application_id_local)
            self.fields['declaration'].initial = first_aid_record.show_certificate


class FirstAidTrainingRenewForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: renew page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    renew = forms.BooleanField(label='I will renew my first aid certificate in the next few months', required=True,
                               error_messages={'required': 'You must agree to renew your first aid certificate'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the First aid training: renew form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstAidTrainingRenewForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if FirstAidTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            first_aid_record = FirstAidTraining.objects.get(application_id=self.application_id_local)
            self.fields['renew'].initial = first_aid_record.renew_certificate


class FirstAidTrainingTrainingForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: training page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class FirstAidTrainingSummaryForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class EYFSGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class EYFSKnowledgeForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: knowledge page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    eyfs_understand = forms.ChoiceField(label='Do you understand the Early Years Foundation Stage?', choices=options,
                                        widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: knowledge form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSKnowledgeForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_understand'].initial = eyfs_record.eyfs_understand


class EYFSTrainingForm(ChildminderForms):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    eyfs_training_declare = forms.BooleanField(label='I will go on an early years training course', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: training form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSTrainingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_training_declare'].initial = eyfs_record.eyfs_training_declare


class EYFSQuestionsForm(ChildminderForms):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    share_info_declare = forms.BooleanField(label='I am happy to answer questions about my early years knowledge',
                                            required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: questions form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSQuestionsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['share_info_declare'].initial = eyfs_record.share_info_declare


class EYFSSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DBSCheckGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DBSCheckDBSDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    # Overrides standard NumberInput widget too give wider field
    widget_instance = NumberInput()
    widget_instance.input_classes = 'form-control form-control-1-4'

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on your certificate',
                                                required=True,
                                                error_messages={'required': 'Please enter your DBS certificate number'},
                                                widget=widget_instance)

    convictions = forms.ChoiceField(label='Do you have any cautions or convictions?',
                                    help_text='Include any information recorded on your certificate',
                                    choices=options, widget=InlineRadioSelect,
                                    required=True,
                                    error_messages={'required': 'Please say if you have any cautions or convictions'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckDBSDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form 
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record = CriminalRecordCheck.objects.get(application_id=self.application_id_local)
            self.fields['dbs_certificate_number'].initial = dbs_record.dbs_certificate_number
            self.fields['convictions'].initial = dbs_record.cautions_convictions
            self.pk = dbs_record.criminal_record_id
            self.field_list = ['dbs_certificate_number']

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        dbs_certificate_number = self.cleaned_data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('Check your certificate: the number should be 12 digits long')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('Check your certificate: the number should be 12 digits long')
        return dbs_certificate_number


class DBSCheckUploadDBSForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: upload DBS page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration = forms.BooleanField(label='I will send my original DBS certificate to Ofsted', required=True,
                                     error_messages={'required': 'You must agree to send us your DBS certificate'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: upload DBS form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckUploadDBSForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record_declare = CriminalRecordCheck.objects.get(
                application_id=self.application_id_local).send_certificate_declare
            if dbs_record_declare is True:
                self.fields['declaration'].initial = '1'
            elif dbs_record_declare is False:
                self.fields['declaration'].initial = '0'


class DBSCheckSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'generic-error-summary.html'
    auto_replace_widgets = True

    arc_errors = forms.CharField()


class HealthIntroForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class HealthBookletForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    send_hdb_declare = forms.BooleanField(label='I will send the completed booklet to Ofsted', required=True,
                                          error_messages={'required': 'You must agree to send your booklet to Ofsted'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your health: booklet form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(HealthBookletForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if HealthDeclarationBooklet.objects.filter(application_id=self.application_id_local).count() > 0:
            hdb_declare = HealthDeclarationBooklet.objects.get(
                application_id=self.application_id_local).send_hdb_declare
            if hdb_declare is True:
                self.fields['send_hdb_declare'].initial = '1'
            elif hdb_declare is False:
                self.fields['send_hdb_declare'].initial = '0'


class ReferenceIntroForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class FirstReferenceForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': 'Please enter the first name of the referee'})
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': 'Please enter the last name of the referee'})
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True,
                                   error_messages={'required': 'Please tell us how the referee knows you'})
    time_known = TimeKnownField(label='How long have they known you?', required=True,
                                error_messages={'required': 'Please tell us how long you have known the referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstReferenceForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form        
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]
            self.pk = reference_record.reference_id
            self.field_list = ['first_name', 'last_name', 'relationship', 'time_known']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if len(first_name) > 100:
            raise forms.ValidationError("Referee's first name must be under 100 characters long")
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if len(last_name) > 100:
            raise forms.ValidationError("Referee's last name must be under 100 characters long")
        return last_name

    def clean_relationship(self):
        """
        Relationship validation
        :return: string
        """
        relationship = self.cleaned_data['relationship']
        if len(relationship) > 100:
            raise forms.ValidationError("Please enter 100 characters or less.")
        return relationship

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        if months_known != 0:
            reference_known_time = years_known + (months_known / 12)
        elif months_known == 0:
            reference_known_time = years_known
        if reference_known_time < 1:
            raise forms.ValidationError('You must have known the referee for at least 1 year')
        return years_known, months_known


class ReferenceFirstReferenceAddressForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=1).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Enter a valid UK postcode or enter the address manually')
        return postcode


class ReferenceFirstReferenceAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_name_and_number = forms.CharField(label='Address line 1', error_messages={
        'required': "Please enter the first line of the referee's address"})
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': "Please enter the name of the town or city"})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})
    country = forms.CharField(label='Country (optional)', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['street_name_and_number'].initial = reference_record.street_line1
            self.fields['street_name_and_number2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country
            self.pk = reference_record.reference_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode',
                               'country']

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match("^[A-Za-z- ]+$", country) is None:
                raise forms.ValidationError('Please spell out the name of the country using letters')
            if len(country) > 50:
                raise forms.ValidationError('The name of the country must be under 50 characters long')
        return country


class ReferenceFirstReferenceAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': "Please select the referee's address"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceFirstReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class ReferenceFirstReferenceContactForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference contact details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    phone_number = forms.CharField(label='Phone number',
                                   error_messages={'required': 'Please give a phone number for your first referee'})
    email_address = forms.CharField(label='Email address',
                                    error_messages={'required': 'Please give an email address for your first referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference contact details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceContactForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local,
                                                     reference=1)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if len(no_space_phone_number) > 14:
                raise forms.ValidationError('Please enter a valid phone number')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        return email_address


class SecondReferenceForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': 'Please enter the first name of the referee'})
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': 'Please enter the name of the referee'})
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True,
                                   error_messages={'required': 'Please tell us how the referee knows you'})
    time_known = TimeKnownField(label='How long have they known you?', required=True,
                                error_messages={'required': 'Please tell us how long you have known the referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(SecondReferenceForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]
            self.pk = reference_record.reference_id
            self.field_list = ['first_name', 'last_name', 'relationship', 'time_known']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if len(first_name) > 100:
            raise forms.ValidationError("Referee's first name must be under 100 characters long")
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if len(last_name) > 100:
            raise forms.ValidationError("Referee's last name must be under 100 characters long")
        return last_name

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        if months_known != 0:
            reference_known_time = years_known + (months_known / 12)
        elif months_known == 0:
            reference_known_time = years_known
        if reference_known_time < 1:
            raise forms.ValidationError('You must have known the referee for at least 1 year')
        return years_known, months_known


class ReferenceSecondReferenceAddressForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=2).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Enter a valid UK postcode or enter the address manually')
        return postcode


class ReferenceSecondReferenceAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_name_and_number = forms.CharField(label='Address line 1', error_messages={
        'required': "Please enter the first line of the referee's address"})
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': "Please enter the name of the town or city"})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})
    country = forms.CharField(label='Country (optional)', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['street_name_and_number'].initial = reference_record.street_line1
            self.fields['street_name_and_number2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country
            self.pk = reference_record.reference_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode',
                               'country']

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match("^[A-Za-z- ]+$", country) is None:
                raise forms.ValidationError('Please spell out the name of the country using letters')
            if len(country) > 50:
                raise forms.ValidationError('The name of the country must be under 50 characters long')
        return country


class ReferenceSecondReferenceAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': "Please select the referee's address"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceSecondReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class ReferenceSecondReferenceContactForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference contact details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    phone_number = forms.CharField(label='Phone number',
                                   error_messages={'required': 'Please give a phone number for your second referee'})
    email_address = forms.CharField(label='Email address', error_messages={
        'required': 'Please give an email address for your second referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference contct details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceContactForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email
            self.pk = reference_record.reference_id
            self.field_list = ['phone_number', 'email_address']

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if len(no_space_phone_number) > 14:
                raise forms.ValidationError('Please enter a valid phone number')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        return email_address


class ReferenceSummaryForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleAdultQuestionForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult question page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    adults_in_home = forms.ChoiceField(label='Does anyone aged 16 or over live or work in your home?', choices=options,
                                       widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult question form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(OtherPeopleAdultQuestionForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        self.fields['adults_in_home'].initial = Application.objects.get(
            application_id=self.application_id_local).adults_in_home
        self.pk = self.application_id_local
        self.field_list = ['adults_in_home']

class OtherPeopleAdultDetailsForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True)
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True)
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980')
    relationship = forms.CharField(label='How are they related to you?', help_text='For instance, husband or daughter',
                                   required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        super(OtherPeopleAdultDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
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
            self.pk = adult_record.adult_id
            self.field_list = ['first_name', 'middle_names', 'last_name', 'date_of_birth', 'relationship']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match("^[A-zÀ-ÿ- ]+$", middle_names) is None:
                raise forms.ValidationError('TBC')
            if len(middle_names) > 100:
                raise forms.ValidationError('Please enter 100 characters or less')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
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
            raise forms.ValidationError('TBC')
        if len(str(birth_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return birth_day, birth_month, birth_year


class OtherPeopleAdultDBSForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult DBS page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    widget_instance = NumberInput()
    widget_instance.input_classes = 'form-control form-control-1-4'

    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on their certificate',
                                                required=True,
                                                widget=widget_instance)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult DBS form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.name = kwargs.pop('name')
        super(OtherPeopleAdultDBSForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
            self.fields['dbs_certificate_number'].initial = adult_record.dbs_certificate_number
            self.pk = adult_record.adult_id
            self.field_list = ['dbs_certificate_number']

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        dbs_certificate_number = self.cleaned_data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('TBC')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('TBC')
        return dbs_certificate_number


class OtherPeopleAdultPermissionForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult permission page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    permission_declare = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult permission form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        super(OtherPeopleAdultPermissionForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        adult = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
        first_name = adult.first_name
        middle_names = adult.middle_names
        last_name = adult.last_name
        if middle_names != '':
            self.fields['permission_declare'].label = first_name + ' ' + middle_names + ' ' + last_name
        elif middle_names == '':
            self.fields['permission_declare'].label = first_name + ' ' + last_name
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
            self.fields['permission_declare'].initial = adult_record.permission_declare


class OtherPeopleChildrenQuestionForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: children question page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    children_in_home = forms.ChoiceField(label='Do you live with any children under 16?', choices=options,
                                         widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: children question form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(OtherPeopleChildrenQuestionForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        self.fields['children_in_home'].initial = Application.objects.get(
            application_id=self.application_id_local).children_in_home
        self.pk = self.application_id_local
        self.field_list = ['children_in_home']


class OtherPeopleChildrenDetailsForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: children details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True)
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True)
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980')
    relationship = forms.CharField(label='How are they related to you?', help_text='For instance, son or daughter',
                                   required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: children details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        super(OtherPeopleChildrenDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildInHome.objects.filter(application_id=self.application_id_local, child=self.child).count() > 0:
            child_record = ChildInHome.objects.get(application_id=self.application_id_local, child=self.child)

            birth_day, birth_month, birth_year = date_formatter(child_record.birth_day,
                                                                child_record.birth_month,
                                                                child_record.birth_year)

            self.fields['first_name'].initial = child_record.first_name
            self.fields['middle_names'].initial = child_record.middle_names
            self.fields['last_name'].initial = child_record.last_name
            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]
            self.fields['relationship'].initial = child_record.relationship
            self.pk = child_record.child_id
            self.field_list = ['first_name', 'middle_names', 'last_name', 'date_of_birth', 'relationship']

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match("^[A-zÀ-ÿ- ]+$", first_name) is None:
            raise forms.ValidationError('TBC')
        if len(first_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        return first_name

    def clean_middle_names(self):
        """
        Middle names validation
        :return: string
        """
        middle_names = self.cleaned_data['middle_names']
        if middle_names != '':
            if re.match("^[A-zÀ-ÿ- ]+$", middle_names) is None:
                raise forms.ValidationError('TBC')
            if len(middle_names) > 100:
                raise forms.ValidationError('Please enter 100 characters or less')
        return middle_names

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match("^[A-zÀ-ÿ- ]+$", last_name) is None:
            raise forms.ValidationError('TBC')
        if len(last_name) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        return last_name

    def clean_date_of_birth(self):
        """
        Date of birth validation (calculate if age is more than 16)
        :return: string
        """
        birth_day = self.cleaned_data['date_of_birth'].day
        birth_month = self.cleaned_data['date_of_birth'].month
        birth_year = self.cleaned_data['date_of_birth'].year
        applicant_dob = date(birth_year, birth_month, birth_day)
        today = date.today()
        age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
        if age >= 16:
            raise forms.ValidationError('TBC')
        if len(str(birth_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return birth_day, birth_month, birth_year


class OtherPeopleApproaching16Form(ChildminderForms):
    """
    GOV.UK form for the People in your home: approaching 16 page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleNumberOfChildrenForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: number of children page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleSummaryForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DeclarationIntroForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DeclarationConfirmationOfUnderstandingForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    background_check_declare = forms.BooleanField(label='carry out background checks', required=True)
    inspect_home_declare = forms.BooleanField(label='inspect my home', required=True)
    interview_declare = forms.BooleanField(label='interview me', required=True)
    share_info_declare = forms.BooleanField(label='share information with other organisations', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConfirmationOfUnderstandingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            background_check_declare = Application.objects.get(
                application_id=self.application_id_local).background_check_declare
            if background_check_declare is True:
                self.fields['background_check_declare'].initial = '1'
            elif background_check_declare is False:
                self.fields['background_check_declare'].initial = '0'
            inspect_home_declare = Application.objects.get(
                application_id=self.application_id_local).inspect_home_declare
            if inspect_home_declare is True:
                self.fields['inspect_home_declare'].initial = '1'
            elif inspect_home_declare is False:
                self.fields['inspect_home_declare'].initial = '0'
            interview_declare = Application.objects.get(
                application_id=self.application_id_local).interview_declare
            if interview_declare is True:
                self.fields['interview_declare'].initial = '1'
            elif interview_declare is False:
                self.fields['interview_declare'].initial = '0'
            share_info_declare = Application.objects.get(
                application_id=self.application_id_local).share_info_declare
            if share_info_declare is True:
                self.fields['share_info_declare'].initial = '1'
            elif share_info_declare is False:
                self.fields['share_info_declare'].initial = '0'


class DeclarationConfirmationOfDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    information_correct_declare = forms.BooleanField(label='the information I have given is correct', required=True,
                                                     error_messages={'required': 'You need to confirm this'})
    change_declare = forms.BooleanField(label='I will tell Ofsted if this information changes', required=True,
                                        error_messages={'required': 'You need to confirm this'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConfirmationOfDeclarationForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            information_correct_declare = Application.objects.get(
                application_id=self.application_id_local).information_correct_declare
            if information_correct_declare is True:
                self.fields['information_correct_declare'].initial = '1'
            elif information_correct_declare is False:
                self.fields['information_correct_declare'].initial = '0'
            change_declare = Application.objects.get(application_id=self.application_id_local).change_declare
            if change_declare is True:
                self.fields['change_declare'].initial = '1'
            elif change_declare is False:
                self.fields['change_declare'].initial = '0'


class DeclarationConsentToSharingForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page (optional section about sharing details on web)
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    auto_replace_widgets = True

    display_contact_details_on_web = forms.BooleanField(label='display my name '
                                                              'and contact details '
                                                              'on their website so parents can find me '
                                                              '(optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConsentToSharingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            display_contact_details_on_web = Application.objects.get(
                application_id=self.application_id_local).display_contact_details_on_web
            if display_contact_details_on_web is True:
                self.fields['display_contact_details_on_web'].initial = '1'
            elif display_contact_details_on_web is False:
                self.fields['display_contact_details_on_web'].initial = '0'


class DeclarationSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Confirm your details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class PaymentForm(ChildminderForms):
    """
    GOV.UK form for the Payment selection page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('Credit', 'Credit or debit card'),
        ('PayPal', 'PayPal')
    )
    payment_method = forms.ChoiceField(label='How would you like to pay?', choices=options,
                                       widget=RadioSelect, required=True,
                                       error_messages={'required': 'Please select how you would like to pay'})


class PaymentDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Payment details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('a', 'Alpha'),
        ('b', 'Beta')
    )
    grouped_options = (
        ('First', options),
        ('Second', (('c', 'Gamma'), ('d', 'Delta'))),
    )
    card_type_options = (
        (None, '(Please select)'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('american_express', 'American Express'),
        ('maestro', 'Maestro')
    )
    card_type = forms.ChoiceField(label='Card type', choices=card_type_options, required=True,
                                  error_messages={'required': 'Please select the type of card'})
    card_number = forms.CharField(label='Card number', required=True,
                                  error_messages={'required': 'Please enter the number on your card'})
    expiry_date = ExpirySplitDateField(label='Expiry date', required=True, widget=ExpirySplitDateWidget,
                                       help_text='For example, 10/20',
                                       error_messages={'required': 'Please enter the expiry date on the card'})
    cardholders_name = forms.CharField(label="Cardholder's name", required=True,
                                       error_messages={'required': 'Please enter the name of the cardholder'})
    card_security_code = forms.IntegerField(label='Card security code',
                                            help_text='3 or 4 digit number on back of card', required=True,
                                            error_messages={
                                                'required': 'Please enter the 3 or 4 digit card security code'})

    def __init__(self, *args, **kwargs):
        super(PaymentDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_card_type(self):
        card_type = self.cleaned_data['card_type']
        if not card_type:
            raise forms.ValidationError('Please select the type of card')

    def clean_card_number(self):
        """
        Card number validation
        :return: string
        """
        card_type = self.data['card_type']
        card_number = self.cleaned_data['card_number']
        card_number = re.sub('[ -]+', '', card_number)
        # noinspection PyPep8
        try:
            int(card_number)
        except:
            # At the moment this is a catch all error, in the case of there being multiple error
            # types this must be revisited
            raise forms.ValidationError('Please check the number on your card')
        if settings.VISA_VALIDATION:
            if card_type == 'visa':
                if re.match("^4[0-9]{12}(?:[0-9]{3})?$", card_number) is None:
                    raise forms.ValidationError('Please check the number on your card')
        if card_type == 'mastercard':
            if re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                        card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        elif card_type == 'american_express':
            if re.match("^3[47][0-9]{13}$", card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        elif card_type == 'maestro':
            if re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        return card_number

    def clean_expiry_date(self):
        """
        Expiry date validation
        :return: expiry date
        """
        expiry_date = self.cleaned_data['expiry_date']
        year = expiry_date[0]
        month = expiry_date[1]
        today_month = date.today().month
        today_year = date.today().year
        expiry_date_object = date(year, month, 1)
        today_date = date(today_year, today_month, 1)
        date_difference = expiry_date_object - today_date
        if date_difference.days < 0:
            raise forms.ValidationError('Check the expiry date or use a new card')

    def clean_cardholders_name(self):
        """
        Cardholder's name validation
        :return: string
        """
        cardholders_name = self.cleaned_data['cardholders_name']
        if len(cardholders_name) > 50:
            raise forms.ValidationError('Please enter 50 characters or less')

    def clean_card_security_code(self):
        """
        Card security code validation
        :return: string
        """
        card_security_code = str(self.cleaned_data['card_security_code'])
        if re.match("^[0-9]{3,4}$", card_security_code) is None:
            raise forms.ValidationError('The code should be 3 or 4 digits long')


class DocumentsNeededForm(ChildminderForms):
    """
    GOV.UK form for the Documents you need for the visit page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class HomeReadyForm(ChildminderForms):
    """
    GOV.UK form for the Get your home ready page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class PrepareForInterviewForm(ChildminderForms):
    """
    GOV.UK form for the Get your home ready page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class ApplicationSavedForm(ChildminderForms):
    """
    GOV.UK form for the Application saved page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
