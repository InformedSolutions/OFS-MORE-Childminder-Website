from django import forms

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper


class VerifyPhoneForm(ChildminderForms):
    """
    GOV.UK form for the page to verify an SMS code
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    magic_link_sms = forms.IntegerField(label='Security code', required=True, error_messages={'required': 'Please enter the 5 digit code we sent to your mobile'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the SMS code verification form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.magic_link_email = kwargs.pop('id')
        try:
            self.correct_sms_code = kwargs.pop('correct_sms_code')
        except:
            self.correct_sms_code = None
        super(VerifyPhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_magic_link_sms(self):
        """
        SMS code validation
        :return: string
        """
        magic_link_sms = str(self.cleaned_data['magic_link_sms'])

        if len(magic_link_sms)<5:
            raise forms.ValidationError('The code must be 5 digits.  You have entered fewer than 5 digits')
        if len(magic_link_sms)>5:
            raise forms.ValidationError('The code must be 5 digits.  You have entered more than 5 digits')
        if magic_link_sms != self.correct_sms_code:
            raise forms.ValidationError('Invalid code. Check the code we sent to your mobile.')
        return magic_link_sms
