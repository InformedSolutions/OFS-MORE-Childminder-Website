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

    CHILDCARE_TYPE_CHOICES = (
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
        choices=CHILDCARE_TYPE_CHOICES,
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
            childcare_record = ChildcareTiming.objects.get(application_id=self.application_id_local)
            childcare_record_list = ChildcareTiming._meta._get_all_field_names()
            childcare_record_tuple = ChildcareTiming.timelog_fields()
            bools = []
            for j in childcare_record_list:
                i = 2
                if childcare_record_list[i]:
                    bools.append(j)
                i += 1
            self.fields['type_of_childcare'].initial = bools
            # zero_to_five_status = childcare_record.zero_to_five
            # five_to_eight_status = childcare_record.five_to_eight
            # eight_plus_status = childcare_record.eight_plus
            # if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
            #     self.fields['type_of_childcare'].initial = ['0-5', '5-8', '8over']
            # elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
            #     self.fields['type_of_childcare'].initial = ['0-5', '5-8']
            # elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
            #     self.fields['type_of_childcare'].initial = ['0-5', '8over']
            # elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
            #     self.fields['type_of_childcare'].initial = ['5-8', '8over']
            # elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
            #     self.fields['type_of_childcare'].initial = ['0-5']
            # elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
            #     self.fields['type_of_childcare'].initial = ['5-8']
            # elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
            #     self.fields['type_of_childcare'].initial = ['8over']
            # elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is False):
            #     self.fields['type_of_childcare'].initial = []
        self.fields['type_of_childcare'].error_messages = {
            'required': 'Please select at least one age group'}


