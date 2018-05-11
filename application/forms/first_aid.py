from datetime import date

from django import forms

from application.customfields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (FirstAidTraining)
from application.utils import date_formatter


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

    first_aid_training_organisation = forms.CharField(label='Training organisation', error_messages={
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


class FirstAidTrainingRenewForm(ChildminderForms):
    """
    GOV.UK form for the First aid training: renew page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


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
