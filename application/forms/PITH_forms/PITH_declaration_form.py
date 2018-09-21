from django import forms
from application.forms import ChildminderForms


class PITHDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the Other people health check: Declaration check box.
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    declaration_confirmation = forms.BooleanField(label='I confirm', required=True,
                                                  error_messages={
                                                      'required': 'You must confirm everything on this page to continue'})

    def clean_declaration_confirmation(self):
        """

        :return:
        """
        declaration_confirmation = self.cleaned_data['declaration_confirmation']
        if not declaration_confirmation:
            raise forms.ValidationError('You must confirm everything on this page to continue')
        return declaration_confirmation
