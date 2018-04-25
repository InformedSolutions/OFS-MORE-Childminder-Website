from django import forms

from application.customfields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper


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
        elif self.answer.replace(' ', '') != security_answer.replace(' ', ''):
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