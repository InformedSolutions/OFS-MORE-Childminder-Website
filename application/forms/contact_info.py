import re

from django import forms

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (Application,
                                UserDetails)


class ContactEmailForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem with your email'
    auto_replace_widgets = True
    email_address = forms.EmailField(required=True, error_messages={'required': "Please enter an email address"})

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        # RegEx for valid e-mail addresses
        if re.match("^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        return email_address


class ContactPhoneForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: phone page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title ='There was a problem with your phone number'

    mobile_number = forms.CharField(label='Mobile phone number')
    add_phone_number = forms.CharField(label='Additional phone number (optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ContactPhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = UserDetails.objects.get(application_id=self.application_id_local)
            login_id = this_user.login_id
            self.fields['mobile_number'].initial = UserDetails.objects.get(login_id=login_id).mobile_number
            self.fields['add_phone_number'].initial = UserDetails.objects.get(login_id=login_id).add_phone_number
            self.pk = login_id
            self.field_list = ['mobile_number', 'add_phone_number']

    def clean_mobile_number(self):
        """
        Mobile number validation
        :return: string
        """
        mobile_number = self.cleaned_data['mobile_number']
        no_space_mobile_number = mobile_number.replace(' ', '')
        if re.match("^(07\d{8,12}|447\d{7,11})$", no_space_mobile_number) is None:
            raise forms.ValidationError('Please enter a valid mobile number')
        if len(no_space_mobile_number) > 11:
            raise forms.ValidationError('Please enter a valid mobile number')
        return mobile_number

    def clean_add_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        add_phone_number = self.cleaned_data['add_phone_number']
        no_space_add_phone_number = add_phone_number.replace(' ', '')
        if add_phone_number != '':
            if re.match("^(0\d{8,12}|447\d{7,11})$", no_space_add_phone_number) is None:
                raise forms.ValidationError('Please enter a valid phone number')
            if len(no_space_add_phone_number) > 11:
                raise forms.ValidationError('Please enter a valid phone number')
        return add_phone_number


class ContactSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
