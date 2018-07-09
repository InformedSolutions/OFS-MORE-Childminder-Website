from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import CriminalRecordCheck, Application
from ..business_logic import new_dbs_numbers_is_valid


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
                                                error_messages={'required': 'Please enter the DBS certificate number'},
                                                widget=widget_instance)

    cautions_convictions = forms.ChoiceField(label='Do you have any criminal cautions or convictions?',
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
            self.fields['cautions_convictions'].initial = dbs_record.cautions_convictions
            self.pk = dbs_record.criminal_record_id
            self.field_list = ['dbs_certificate_number', 'cautions_convictions']

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        # is_valid() call strips leading 0 required by DBS number. Use raw str input from user instead of cleaned_data.
        dbs_certificate_number = self.data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')

        application_id = self.data['id']
        application = Application.objects.get(pk=application_id)

        unique_dbs_check_result = new_dbs_numbers_is_valid(application, dbs_certificate_number)

        if unique_dbs_check_result.dbs_numbers_unique:
            return dbs_certificate_number

        # If this is simply an update by the childminder to their own DBS (i.e. resubmission of page)
        # let pass
        if unique_dbs_check_result.duplicates_childminder_dbs:
            return dbs_certificate_number

        if unique_dbs_check_result.duplicates_household_member_dbs:
            raise forms.ValidationError('This DBS number has already been provided for another household member')

        return dbs_certificate_number


class DBSCheckUploadDBSForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: upload DBS page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DBSCheckSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'generic-error-summary.html'
    auto_replace_widgets = True

    arc_errors = forms.CharField()
