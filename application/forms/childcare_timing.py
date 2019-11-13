from django import forms
from govuk_forms.widgets import CheckboxSelectMultiple, InlineRadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ChildcareTiming)


class TimingOfChildcareGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Type of childcare: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class TimingOfChildcareGroupsForm(ChildminderForms):
    """
    GOV.UK form for the Timing of childcare task
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    CHILDCARE_TIMING_CHOICES = (
        ('weekday_before_school', 'Weekday (before school)'),
        ('weekday_after_school', 'Weekday (after school)'),
        ('weekday_am', 'Weekday (morning)'),
        ('weekday_pm', 'Weekday (afternoon)'),
        ('weekday_all_day', 'Weekday (all day)'),
        ('weekend_am', 'Weekend (morning'),
        ('weekend_pm', 'Weekend (afternoon'),
        ('weekend_all_day', 'Weekend (all day)')
    )

    time_of_childcare = forms.MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple,
        choices=CHILDCARE_TIMING_CHOICES,
        label='What time will the childcare occur?',
        help_text='Tick all that apply'
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of childcare form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(TimingOfChildcareGroupsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildcareTiming.objects.filter(application_id=self.application_id_local).count() > 0:
            childcare_record_list = ChildcareTiming.get_field_names(self)
            bools = []
            for j in childcare_record_list:
                if j:
                    bools.append(j)
            self.fields['time_of_childcare'].initial = bools
        self.fields['time_of_childcare'].error_messages = {
            'required': 'Please select at least one timing group'}


