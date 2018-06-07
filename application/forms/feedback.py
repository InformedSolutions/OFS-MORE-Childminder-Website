import re

from django import forms

from django.conf import settings

from application.forms.childminder import ChildminderForms


class FeedbackForm(ChildminderForms):
    """
    GOV.UK form for the feedback page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    feedback = forms.CharField(widget=forms.Textarea(), label='Tell us what you think of our online service',
                               error_messages={'required': 'Please give us feedback before submitting'})
    email_address = forms.CharField(
        label='Leave us your email address. We may have more questions about your feedback. (Optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Feedback form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        super(FeedbackForm, self).__init__(*args, **kwargs)

    def clean_feedback(self):
        """
        Feedback validation
        :return: string
        """
        feedback = self.cleaned_data['feedback']
        if len(feedback) > 1000:
            raise forms.ValidationError('Feedback can only be up to 1000 characters long')
        return feedback

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        # RegEx for valid e-mail addresses
        if re.match(settings.REGEX['EMAIL'], email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        return email_address
