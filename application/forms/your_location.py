from django import forms
from govuk_forms.widgets import RadioSelect

from application.forms import ChildminderForms


class YourLocationForm(ChildminderForms):
    """
    Class to handle the form for selecting service within the sign in task
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem'

    options = (
        ('True', 'Yes - register as a childminder with our new GOV.UK pilot service'),
        ('False', 'No - apply with Ofsted Online')
    )

    your_location = forms.ChoiceField(label='Do you live in Greater London?', choices=options,
                                      widget=RadioSelect, required=True,
                                      error_messages={'required': 'Please say if you live in Greater London'})

