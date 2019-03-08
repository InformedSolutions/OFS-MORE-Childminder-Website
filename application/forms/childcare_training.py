from datetime import date

from django import forms

from govuk_forms.widgets import CheckboxSelectMultiple

from application.fields import CustomSplitDateField
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import ChildcareTraining
from application.utils import date_formatter


class EYFSDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Early Years details: details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    eyfs_course_name = forms.CharField(label='Title of training course',
                                       error_messages={'required': 'Please enter the title of the course'})
    eyfs_course_date = CustomSplitDateField(label='Date you completed course', help_text='For example, 31 03 2016',
                                            error_messages={'required': 'Please enter the full date, including the day, month and year'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years details: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildcareTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = ChildcareTraining.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_course_name'].initial = eyfs_record.eyfs_course_name
            course_day, course_month, course_year = date_formatter(eyfs_record.eyfs_course_date_day,
                                                                eyfs_record.eyfs_course_date_month,
                                                                eyfs_record.eyfs_course_date_year)
            self.fields['eyfs_course_date'].initial = [course_day, course_month, course_year]
            self.pk = eyfs_record.eyfs_id
            self.field_list = ['eyfs_course_name','eyfs_course_date']

    def clean_eyfs_course_name(self):
        """
        Course name validation
        :return: string
        """
        course_name = self.cleaned_data['eyfs_course_name']
        if len(course_name) > 50:
            raise forms.ValidationError('The title of the course must be under 50 characters long')
        return course_name

    def clean_eyfs_course_date(self):
        """
        Course date validation is handled by custom date object it instantiates (CustomSplitDateField)
        :return: birth day, birth month, birth year
        """
        course_date_day = self.cleaned_data['eyfs_course_date'].day
        course_date_month = self.cleaned_data['eyfs_course_date'].month
        course_date_year = self.cleaned_data['eyfs_course_date'].year
        course_date = date(course_date_year, course_date_month, course_date_day)
        return course_date


class TypeOfChildcareTrainingForm(ChildminderForms):
    """
    GOV.UK form for 'Type-Of-Course' page.
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    error_summary_title = 'There was a problem'
    auto_replace_widgets = True

    options = (
        ('eyfs_training', 'Training that covers the EYFS'),
        ('common_core_training', 'Training in common core skills'),
        ('no_training', 'None')
    )

    childcare_training = forms.MultipleChoiceField(label='', choices=options,
                                                   widget=CheckboxSelectMultiple, required=True,
                                                   error_messages={'required': 'Please select the types of childcare courses you have completed'},
                                                   help_text="Tick all that apply")

    def clean_childcare_training(self):
        data = self.cleaned_data['childcare_training']

        if 'no_training' in data and len(data) >= 2:
            raise forms.ValidationError('Please select types of courses or none')
        return data

    def __init__(self, *args, **kwargs):
        self.application_id_local = kwargs.pop('id')
        super(TypeOfChildcareTrainingForm, self).__init__(*args, **kwargs)
        # If information was previously entered, display it on the form
        if ChildcareTraining.objects.filter(application_id=self.application_id_local).count() > 0:
            training_record = ChildcareTraining.objects.get(application_id=self.application_id_local)

            initial_vals = [option[0] for option in self.options if getattr(training_record, option[0])]
            self.fields['childcare_training'].initial = initial_vals
            self.pk = training_record.eyfs_id
            self.field_list = ['childcare_training']
