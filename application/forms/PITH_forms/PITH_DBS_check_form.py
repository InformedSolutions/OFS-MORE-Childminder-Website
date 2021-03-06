import collections
import logging

from django import forms
from govuk_forms.widgets import NumberInput

from application.business_logic import dbs_matches_childminder_dbs, find_dbs_status, DBSStatus
from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter
from application.models import Application

log = logging.getLogger(__name__)


class PITHDBSCheckForm(PITHChildminderFormAdapter):
    """
    GOV.UK form for the People in the Home: Non generic form for the DBSCheckView.
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'PITH_templates/PITH_error_summary.html'
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):

        self.application_id = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.dbs_field = kwargs.pop('dbs_field')
        self.pk = self.adult.pk

        self.dbs_field_name = self.dbs_field + str(self.adult.pk)

        self.base_fields = collections.OrderedDict([
            (self.dbs_field_name, self.get_dbs_field_data()),
        ])

        super().__init__(*args, **kwargs)

        self.field_list = [*self.fields]

    def get_dbs_field_data(self):
        dbs_certificate_number_widget = NumberInput()
        dbs_certificate_number_widget.input_classes = 'inline form-control form-control-1-4'

        return forms.IntegerField(label='DBS certificate number',
                                  help_text='12-digit number on their certificate',
                                  required=False,
                                  error_messages={'required': 'Please enter their DBS certificate number'},
                                  widget=dbs_certificate_number_widget)

    def clean(self):
        """
        Nullify fields
        DBS field validation
        Fetch DBS record from capita list
        :return: cleaned data
        """
        super().clean()

        cleaned_dbs_field = self.data[self.dbs_field_name] \
            if self.data[self.dbs_field_name] != "" \
            else None
        application = Application.objects.get(application_id=self.application_id)

        self.clean_dbs(cleaned_dbs_field, self.dbs_field, application)

        log.debug(self.errors.get(self.dbs_field_name, ()))
        # if dbs number looks ok, fetch dbs record for further checking
        if len(self.errors.get(self.dbs_field_name, ())) == 0:

            # find status will perform dbs lookup and store result
            dbs_status = find_dbs_status(self.adult, self.adult, dbs_certificate_number=cleaned_dbs_field)

            if dbs_status == DBSStatus.DOB_MISMATCH:
                self.add_error(self.dbs_field,
                               """
                               Check your DBS certificate. The number you entered does not match your number held by DBS.
                               """)

        return self.cleaned_data

    def clean_dbs(self, cleaned_dbs_value, field_name, application):

        if cleaned_dbs_value is None:
            self.add_error(field_name, 'Please enter their DBS certificate number')
        elif len(str(cleaned_dbs_value)) != 12:
            self.add_error(field_name, 'Check the certificate: the number should be 12 digits long')
        elif dbs_matches_childminder_dbs(application, cleaned_dbs_value):
            self.add_error(field_name, 'Please enter a different DBS number. '
                                       'You entered this number for someone in your childcare location')
        # check for duplicate dbs numbers amongst adults in home is done in the view's validate_form_list function
