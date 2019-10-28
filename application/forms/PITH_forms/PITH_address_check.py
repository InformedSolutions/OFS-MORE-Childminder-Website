import re

from django import forms
from django.conf import settings
from govuk_forms.widgets import InlineRadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ApplicantHomeAddress,
                                ApplicantPersonalDetails)

class PersonalDetailsLocationOfPITH(ChildminderForms):
    """
    GOV.UK form for the Your personal details: location of care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    childcare_location = forms.ChoiceField(label='Is this where they live??',
                                           choices=options,
                                           widget=InlineRadioSelect, required=True,
                                           error_messages={
                                               'required': "Please say if this is where they live"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: location of care form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsLocationOfPITH, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            address = ApplicantHomeAddress.objects.get(
                personal_detail_id=personal_detail_id, current_address=True)
            self.fields['childcare_location'].initial = address.childcare_address
            self.field_list = ['childcare_location']
            self.pk = address.pk
