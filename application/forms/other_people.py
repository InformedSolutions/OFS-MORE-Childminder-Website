<<<<<<< HEAD
import logging
import re
from datetime import date

from django import forms
from django.conf import settings
from govuk_forms.widgets import InlineRadioSelect, RadioSelect

from ..business_logic import show_resend_and_change_email, TITLE_OPTIONS, get_title_options
from application.forms.fields import CustomSplitDateFieldDOB
from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import (AdultInHome,
                      Application,
                      ChildInHome,
                      UserDetails)
from ..utils import date_formatter

logger = logging.getLogger()


class OtherPeopleGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleAdultDetailsForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with the details'
    reveal_conditionally = {'title': {'Other': 'other_title'}}

    options = get_title_options()

    title = forms.ChoiceField(label='Title', choices=options, required=True, widget=RadioSelect,
                              error_messages={'required': 'Please select a title'})
    other_title = forms.CharField(label='Other', required=False,
                                  error_messages={'required': 'Please enter a title'})

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any on their DBS check) ', required=False)
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})
    relationship = forms.CharField(label='How are they connected to you or your application?',
                                   help_text='For example, husband, daughter, assistant',
                                   required=True,
                                   error_messages={'required': "Please say how the person is related to you"})
    email_address = forms.CharField(label='Email address',
                                    help_text='We need to email them simple questions about their health',
                                    required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in the home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self._all_emails = kwargs.pop('email_list')
        super(OtherPeopleAdultDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).count() > 0:
            adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)

            birth_day, birth_month, birth_year = date_formatter(adult_record.birth_day,
                                                                adult_record.birth_month,
                                                                adult_record.birth_year)
            if adult_record.title in TITLE_OPTIONS:
                self.fields['title'].initial = adult_record.title
            else:
                self.fields['title'].initial = 'Other'
                self.fields['other_title'].initial = adult_record.title
            self.fields['first_name'].initial = adult_record.first_name
            self.fields['middle_names'].initial = adult_record.middle_names
            self.fields['last_name'].initial = adult_record.last_name
            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]
            self.fields['relationship'].initial = adult_record.relationship
            self.fields['email_address'].initial = adult_record.email
            self.pk = adult_record.adult_id
            self.field_list = ['title','first_name', 'middle_names', 'last_name', 'date_of_birth', 'relationship',
                               'email_address']

    def clean_other_title(self):
        """
        Other title validation
        :return: string
        """
        other_title=self.cleaned_data['other_title']
        if self.cleaned_data.get('title') == 'Other':
            if len(other_title) == 0:
                raise forms.ValidationError('Please tell us your title')
            if len(other_title)>100:
                raise forms.ValidationError('Titles must be under 100 characters long')
        return other_title

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

            if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).exists():
                adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
                adult_health_check_status = adult_record.health_check_status
                email_disabled = not show_resend_and_change_email(adult_health_check_status)

                if email_disabled:
                    return self.fields['email_address'].initial

            raise forms.ValidationError('Please enter an email address')


class OtherPeopleChildrenQuestionForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: children question page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem on this page'

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    children_in_home = forms.ChoiceField(label='Do you live with any children under 16?', choices=options,
                                         widget=InlineRadioSelect, required=True, error_messages={
            'required': "Please tell us if you live with any children under 16"})

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
    error_summary_title = 'There was a problem with the details'

    first_name = forms.CharField(label='First name', required=True, error_messages={
        'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True, error_messages={
        'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})
    relationship = forms.CharField(label='How are they related to you?', help_text='For example, son or daughter',
                                   required=True,
                                   error_messages={'required': "Please tell us how you are related to the child"})

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
        if re.match(settings.REGEX['FIRST_NAME'], first_name) is None:
            raise forms.ValidationError('First name can only have letters')
        if len(first_name) > 99:
            raise forms.ValidationError('The first name must be under 100 characters long')
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
                raise forms.ValidationError('The middle names must be under 100 characters long')
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
            raise forms.ValidationError('The last name must be under 100 characters long')
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
            raise forms.ValidationError('Please only use this page for children aged under 16')
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


class OtherPeopleEmailConfirmationForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: email confirmation page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleResendEmailForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: email confirmation page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    def clean(self):
        cleaned_data = super(OtherPeopleResendEmailForm, self).clean()
=======
import logging
import re
from datetime import date

from django import forms
from django.conf import settings
from govuk_forms.widgets import InlineRadioSelect

from ..business_logic import show_resend_and_change_email
from application.forms.fields import CustomSplitDateFieldDOB
from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import (AdultInHome,
                      Application,
                      ChildInHome,
                      UserDetails)
from ..utils import date_formatter

logger = logging.getLogger()


class OtherPeopleGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleAdultDetailsForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: adult details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with the details'

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any on their DBS check) ', required=False)
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})
    relationship = forms.CharField(label='How are they connected to you or your application?',
                                   help_text='For example, husband, daughter, assistant',
                                   required=True,
                                   error_messages={'required': "Please say how the person is related to you"})
    email_address = forms.CharField(label='Email address',
                                    help_text='We need to email them simple questions about their health',
                                    required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in the home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self._all_emails = kwargs.pop('email_list')
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

            if AdultInHome.objects.filter(application_id=self.application_id_local, adult=self.adult).exists():
                adult_record = AdultInHome.objects.get(application_id=self.application_id_local, adult=self.adult)
                adult_health_check_status = adult_record.health_check_status
                email_disabled = not show_resend_and_change_email(adult_health_check_status)

                if email_disabled:
                    return self.fields['email_address'].initial

            raise forms.ValidationError('Please enter an email address')


class OtherPeopleChildrenQuestionForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: children question page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem on this page'

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    children_in_home = forms.ChoiceField(label='Do you live with any children under 16?', choices=options,
                                         widget=InlineRadioSelect, required=True, error_messages={
            'required': "Please tell us if you live with any children under 16"})

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
    error_summary_title = 'There was a problem with the details'

    first_name = forms.CharField(label='First name', required=True, error_messages={
        'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True, error_messages={
        'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})
    relationship = forms.CharField(label='How are they related to you?', help_text='For example, son or daughter',
                                   required=True,
                                   error_messages={'required': "Please tell us how you are related to the child"})

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
        if re.match(settings.REGEX['FIRST_NAME'], first_name) is None:
            raise forms.ValidationError('First name can only have letters')
        if len(first_name) > 99:
            raise forms.ValidationError('The first name must be under 100 characters long')
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
                raise forms.ValidationError('The middle names must be under 100 characters long')
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
            raise forms.ValidationError('The last name must be under 100 characters long')
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
            raise forms.ValidationError('Please only use this page for children aged under 16')
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


class OtherPeopleEmailConfirmationForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: email confirmation page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class OtherPeopleResendEmailForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: email confirmation page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    def clean(self):
        cleaned_data = super(OtherPeopleResendEmailForm, self).clean()
>>>>>>> feat/CCN3-2571/add-title-referees
