from django import forms
from govuk_forms.widgets import InlineRadioSelect, RadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper


class AnalyticsCookieSelection(ChildminderForms):
    """
    GOV.UK form for opting in or out of cookies: Cookie Policy page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    error_summary_title = 'There was a problem on this page'
    auto_replace_widgets = True

    options = (
        ('opted_in', 'On'),
        ('opted_out', 'Off')
    )

    # ToDo - Confirm wording of below
    cookie_selection = forms.ChoiceField(label='', choices=options,
                                         widget=RadioSelect, required=True,
                                         error_messages={
                                             'required': 'Select if you want to allow us to use GA (confirm wording)'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Type of Childcare: Overnight form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        super(AnalyticsCookieSelection, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
