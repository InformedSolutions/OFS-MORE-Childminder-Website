import re
from datetime import date

from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from application.customfields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (AdultInHome,
                                Application,
                                ChildInHome)
from application.utils import date_formatter


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
