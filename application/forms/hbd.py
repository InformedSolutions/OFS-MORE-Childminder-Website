from django import forms

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (HealthDeclarationBooklet)


class HealthIntroForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class HealthBookletForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    send_hdb_declare = forms.BooleanField(label='I will send the completed booklet to Ofsted', required=True,
                                          error_messages={'required': 'You must agree to send your booklet to Ofsted'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your health: booklet form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(HealthBookletForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if HealthDeclarationBooklet.objects.filter(application_id=self.application_id_local).count() > 0:
            hdb_declare = HealthDeclarationBooklet.objects.get(
                application_id=self.application_id_local).send_hdb_declare
            if hdb_declare is True:
                self.fields['send_hdb_declare'].initial = '1'
            elif hdb_declare is False:
                self.fields['send_hdb_declare'].initial = '0'
