from django import forms
from application.forms import ChildminderForms


class PITHDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the People in the Home: Declaration check box.
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration_confirmation = forms.BooleanField(label='I confirm', required=True,
                                                  error_messages={
                                                      'required': 'You must confirm everything on this page to continue'})
