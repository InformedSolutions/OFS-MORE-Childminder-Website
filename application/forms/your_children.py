import re
from datetime import date

from django import forms
from govuk_forms.widgets import CheckboxSelectMultiple

from ..forms import ChildminderForms
from django.conf import settings

from ..customfields import CustomSplitDateFieldDOB
from ..forms_helper import full_stop_stripper
from ..models import ChildInHome, Child
from ..utils import date_formatter


class YourChildrenGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Your Children: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class YourChildrenDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Your children: details of your children page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with the details'

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': "Please enter their first name"})
    middle_names = forms.CharField(label='Middle names (if they have any)', required=False)
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': "Please enter their last name"})
    date_of_birth = CustomSplitDateFieldDOB(label='Date of birth', help_text='For example, 31 03 1980', error_messages={
        'required': "Please enter the full date, including the day, month and year"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the People in your home: adult details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        super(YourChildrenDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Child.objects.filter(application_id=self.application_id_local, child=self.child).count() > 0:
            child_record = Child.objects.get(application_id=self.application_id_local, child=self.child)

            birth_day, birth_month, birth_year = date_formatter(child_record.birth_day,
                                                                child_record.birth_month,
                                                                child_record.birth_year)

            self.fields['first_name'].initial = child_record.first_name
            self.fields['middle_names'].initial = child_record.middle_names
            self.fields['last_name'].initial = child_record.last_name
            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]
            self.pk = child_record.child_id
            self.field_list = ['first_name', 'middle_names', 'last_name', 'date_of_birth']

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
        if age > 16:
            raise forms.ValidationError('Please only use this page for children aged under 16')
        if len(str(birth_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return birth_day, birth_month, birth_year


class YourChildrenLivingWithYouForm(ChildminderForms):
    """
    GOV.UK form for the Your children: details of your children page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with the details'

    children_living_with_childminder_selection = forms.MultipleChoiceField(label='Which of your children live with you?',
        widget=CheckboxSelectMultiple, required=True, error_messages={
                     'required': 'Please say if any of your children live with you'}, help_text="Tick all that apply")

    def __init__(self, *args, **kwargs):
        """
        Customer constructor implementation which loads child names from the data tier and sets any previous responses
        """

        # Pop id
        self.application_id_local = kwargs.pop('id')

        # Instantiate django form
        super(YourChildrenLivingWithYouForm, self).__init__(*args, **kwargs)

        # Fetch selection options ordering by the sequence children were added
        children = \
            Child.objects.filter(application_id=self.application_id_local).order_by('child')

        # Create outer tuple (to hold tuple of tuples containing children names and child int representation values)
        select_options = ()

        previous_selections = []

        # Iterate child option and push to tuple of tuples
        for child in children:
            if child.lives_with_childminder:
                previous_selections.append(str(child.child))

            select_options += ((str(child.child), child.get_full_name()),)

        # Add none selection as last entry (post-for-loop)
        select_options += (('none', 'None'),)

        self.fields['children_living_with_childminder_selection'].choices = select_options
        self.fields['children_living_with_childminder_selection'].initial = previous_selections

    def clean_children_living_with_childminder_selection(self):
        """
        Validator method to ensure options selected are permissible.
        If for example, names have been chosen as well as 'none' an error should be raised
        """
        selections = self.cleaned_data['children_living_with_childminder_selection']
        
        if len(selections) > 1 and 'none' in selections:
            raise forms.ValidationError('Error tbc')

        return selections


class YourChildrenSummaryForm(ChildminderForms):
    """
    GOV.UK form for the People in your home: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
