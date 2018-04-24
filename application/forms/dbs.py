from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (CriminalRecordCheck)


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
                                                error_messages={'required': 'Please enter your DBS certificate number'},
                                                widget=widget_instance)

    convictions = forms.ChoiceField(label='Do you have any cautions or convictions?',
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
            self.fields['convictions'].initial = dbs_record.cautions_convictions
            self.pk = dbs_record.criminal_record_id
            self.field_list = ['dbs_certificate_number']

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        dbs_certificate_number = self.cleaned_data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('Check your certificate: the number should be 12 digits long')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('Check your certificate: the number should be 12 digits long')
        return dbs_certificate_number


class DBSCheckUploadDBSForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: upload DBS page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration = forms.BooleanField(label='I will send my original DBS certificate to Ofsted', required=True,
                                     error_messages={'required': 'You must agree to send us your DBS certificate'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: upload DBS form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DBSCheckUploadDBSForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if CriminalRecordCheck.objects.filter(application_id=self.application_id_local).count() > 0:
            dbs_record_declare = CriminalRecordCheck.objects.get(
                application_id=self.application_id_local).send_certificate_declare
            if dbs_record_declare is True:
                self.fields['declaration'].initial = '1'
            elif dbs_record_declare is False:
                self.fields['declaration'].initial = '0'


class DBSCheckSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your criminal record (DBS) check: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'generic-error-summary.html'
    auto_replace_widgets = True

    arc_errors = forms.CharField()
