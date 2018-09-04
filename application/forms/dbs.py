from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput
from django.core.validators import RegexValidator

from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import CriminalRecordCheck, Application

from ..business_logic import childminder_dbs_number_duplication_check, childminder_dbs_duplicates_household_member_check


class DBSRadioForm(ChildminderForms):
    """
    GOV.UK form for the Criminal record check: generic radio button form
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choice_field_name = 'generic_choice_field_name'
    dbs_field_name = None

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')
        self.dbs_field_name = kwargs.pop('dbs_field_name')
        super().__init__(*args, **kwargs)

        self.fields[self.dbs_field_name] = self.get_choice_field_data()
        self.field_list = [*self.fields]

        if CriminalRecordCheck.objects.filter(application_id=self.application_id).exists():
            CRC_record = CriminalRecordCheck.objects.get(application_id=self.application_id)
            self.pk = CRC_record.pk

    def get_options(self):
        options = (
            ('True', 'Yes'),
            ('False', 'No')
        )
        return options

    def get_choice_field_data(self):
        raise NotImplementedError("No choice field was inherited.")


class DBSLivedAbroadForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: lived abroad page
    """
    choice_field_name = 'lived_abroad'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Have you lived outside of the UK in the last 5 years?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={'required': 'Please say if you have lived outside of the UK in the last 5 years'})


class DBSMilitaryForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: military page
    """
    choice_field_name = 'military_base'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Have you lived or worked on a British military base outside of the UK in the last 5 years?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={'required': 'Please say if you have lived in a British military base outside of the UK in the last 5 years'})

class DBSTypeForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: type page
    """
    choice_field_name = 'capita'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Do you have an Ofsted DBS Check?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={
                                     'required': 'Please say if you have an Ofsted DBS check'})

class DBSUpdateForm(DBSRadioForm):
    """
    GOV.UK form for the Criminal record check: update page
    """
    choice_field_name = 'on_update'

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Are you on the DBS update service?',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={
                                     'required': 'Please say if you are on the DBS update service'})


class DBSCheckDetailsForm(DBSRadioForm):
    """
    GOV.UK form for generic check details forms
    """
    dbs_certificate_number_widget = NumberInput()
    dbs_certificate_number_widget.input_classes = 'form-control form-control-1-4'

    dbs_certificate_number = forms.IntegerField(label='DBS certificate number',
                                                help_text='12-digit number on your certificate',
                                                required=True,
                                                error_messages={'required': 'Please enter the DBS certificate number'},
                                                widget=dbs_certificate_number_widget)
    choice_field_name = 'cautions_convictions'

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')
        self.dbs_field_name = kwargs.pop('dbs_field_name')
        self.show_cautions_convictions = kwargs.pop('show_cautions_convictions')
        super(ChildminderForms, self).__init__(*args, **kwargs)

        if self.show_cautions_convictions is None:
            raise AttributeError('show_cautions_convictions cannot be None, it has not been inherited.')
        elif self.show_cautions_convictions:
            self.fields[self.choice_field_name] = self.get_choice_field_data()

        self.field_list = [*self.fields]

        if CriminalRecordCheck.objects.filter(application_id=self.application_id).exists():
            CRC_record = CriminalRecordCheck.objects.get(application_id=self.application_id)
            self.pk = CRC_record.pk

    def clean_dbs_certificate_number(self):
        """
        DBS certificate number validation
        :return: integer
        """
        # is_valid() call strips leading 0(s) required by DBS number. Use raw str input from user instead of cleaned_data.
        dbs_certificate_number = self.data['dbs_certificate_number']
        if len(str(dbs_certificate_number)) > 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')
        if len(str(dbs_certificate_number)) < 12:
            raise forms.ValidationError('The certificate number should be 12 digits long')

        application = Application.objects.get(pk=self.application_id)

        if childminder_dbs_duplicates_household_member_check(application, dbs_certificate_number):
            raise forms.ValidationError('Please enter a different DBS number. '
                                        'You entered this number for someone in your childcare location')

        return dbs_certificate_number


class DBSCheckCapitaForm(DBSCheckDetailsForm):
    """
    GOV.UK form for the Criminal record check: Capita page
    """

    def get_choice_field_data(self):
        return forms.ChoiceField(label='Do you have any criminal cautions or convictions?',
                                 help_text='Include any information recorded on your certificate',
                                 choices=self.get_options(),
                                 widget=InlineRadioSelect,
                                 required=True,
                                 error_messages={
                                     'required': 'Please say if you have any cautions or convictions'})

class DBSCheckNoCapitaForm(DBSCheckDetailsForm):
    """
    GOV.UK form for the Criminal record check: No capita page
    """
    # This form is blank as the inherited form will provide all function.
    # This form is kept to be consistent with each FormView having it's own form class
    pass
