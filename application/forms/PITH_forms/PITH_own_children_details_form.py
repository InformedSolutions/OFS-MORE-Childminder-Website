from django import forms

from application.customfields import CustomSplitDateFieldDOB
from application.forms import ChildminderForms, re, settings, date, date_formatter, Child


class PITHOwnChildrenDetailsForm(ChildminderForms):
    choice_field_name = 'children_in_home'

    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with your security code'

    def __init__(self, *args, **kwargs):
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        self.prefix = kwargs.pop('prefix')

        self.base_fields = {
            'first_name': self.get_first_name_field(),
            'middle_names': self.get_middle_name_field(),
            'last_name': self.get_last_name_field(),
            'date_of_birth': self.get_date_of_birth_field()
        }

        super().__init__(*args, **kwargs)

        if Child.objects.filter(application_id=self.application_id_local, child=self.child).exists():
            child_record = Child.objects.get(application_id=self.application_id_local, child=self.child)
            birth_day, birth_month, birth_year = date_formatter(child_record.birth_day,
                                                                child_record.birth_month,
                                                                child_record.birth_year)

            self.pk = child_record.child_id
            self.fields['first_name'].initial = child_record.first_name
            self.fields['middle_names'].initial = child_record.middle_names
            self.fields['last_name'].initial = child_record.last_name
            self.fields['date_of_birth'].initial = [birth_day, birth_month, birth_year]

        self.field_list = [*self.fields]

    def get_first_name_field(self):
        return forms.CharField(label='First name',
                               required=True,
                               error_messages={
                                   'required': "Please enter their first name"})

    def get_middle_name_field(self):
        return forms.CharField(label='Middle names (if they have any)',
                               required=False)

    def get_last_name_field(self):
        return forms.CharField(label='Last name',
                               required=True,
                               error_messages={
                                   'required': "Please enter their last name"})

    def get_date_of_birth_field(self):
        return CustomSplitDateFieldDOB(label='Date of birth',
                                       help_text='For example, 31 03 1980',
                                       error_messages={
                                           'required': "Please enter the full date, including the day, month and year"})

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