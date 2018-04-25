from django import forms
from govuk_forms.widgets import InlineRadioSelect, RadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ChildcareType)


class AccountSelection(ChildminderForms):
    """
    GOV.UK form for the Type of Childcare: Overnight care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    auto_replace_widgets = True

    options = (
        ('new', 'Start a new application'),
        ('existing', 'Go back to your application')
    )

    acc_selection = forms.ChoiceField(label='', choices=options,
                                       widget=RadioSelect, required=True,
                                       error_messages={'required': 'Please select one'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of Childcare: Overnight form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        super(AccountSelection, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
