import re

from django import forms
from django.conf import settings

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (Application,
                                UserDetails,
                                Reference)
from ..business_logic import childminder_references_and_user_email_duplication_check
import logging

log = logging.getLogger('')

class ContactEmailForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: email page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    error_summary_title = 'There was a problem with your email'
    auto_replace_widgets = True
    email_address = forms.EmailField(required=True, help_text="Make sure only you can access it", error_messages={'required': "Please enter an email address"})

    def clean_email_address(self):
        """
        Email address validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']

        # RegEx for valid e-mail addresses
        if re.match(settings.REGEX['EMAIL'], email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')

        # Unique references and application emails validation
        if self.application_id_local != None:
            # If changing email:
            if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
                ref1 = Reference.objects.get(application_id=self.application_id_local, reference=1)
                ref1_email = ref1.email
            else:
                ref1_email = None
            if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
                ref2 = Reference.objects.get(application_id=self.application_id_local, reference=2)
                ref2_email = ref2.email
            else:
                ref2_email = None
            #Check if the email is the same as reference 1 or 2.
            if not childminder_references_and_user_email_duplication_check(email_address, ref1_email) or \
                    not childminder_references_and_user_email_duplication_check(email_address, ref2_email):
                raise forms.ValidationError('Please enter a different email. You entered this email for one of your references.')
        return email_address

    def __init__(self, *args, **kwargs):
        #Gets id if the applicant is changing their e-mail, otherwise sets to None.
        try:
            self.application_id_local = kwargs.pop('id')
        except:
            self.application_id_local = None
        super(ContactEmailForm, self).__init__(*args, **kwargs)

        # Remove full stop from error message, if required. N.B. full-stop-stripper won't work here.
        if len(self.errors):
            if self.errors['email_address'].data[0].message == "Enter a valid email address.":
                self.errors['email_address'].data[0].message = "Please enter a valid email address"


class ContactMobilePhoneForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: phone page (mobile number)
    """
    field_label_classes = 'form-label-bold'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with your phone number'

    mobile_number = forms.CharField(label='Your mobile number', required=True,
                                    error_messages={'required': "Please enter a mobile number"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: mobile phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """

        self.application_id_local = kwargs.pop('id')
        super(ContactMobilePhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = UserDetails.objects.get(application_id=self.application_id_local)
            login_id = this_user.login_id
            self.fields['mobile_number'].initial = UserDetails.objects.get(login_id=login_id).mobile_number
            self.pk = login_id
            self.field_list = ['mobile_number']

    def clean_mobile_number(self):
        """
        Mobile number validation
        :return: string
        """
        mobile_number = self.cleaned_data['mobile_number']
        no_space_mobile_number = mobile_number.replace(' ', '')
        if re.match(settings.REGEX['MOBILE'], no_space_mobile_number) is None:
            raise forms.ValidationError('Please enter a valid mobile number')
        return no_space_mobile_number


class ContactAddPhoneForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: phone page (additional phone number)
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    error_summary_title = 'There was a problem with your phone number'

    add_phone_number = forms.CharField(label='Other phone number (optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your login and contact details: additional phone form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ContactAddPhoneForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            this_user = UserDetails.objects.get(application_id=self.application_id_local)
            login_id = this_user.login_id
            self.fields['add_phone_number'].initial = UserDetails.objects.get(login_id=login_id).add_phone_number
            self.pk = login_id
            self.field_list = ['add_phone_number']

    def clean_add_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        add_phone_number = self.cleaned_data['add_phone_number']
        no_space_add_phone_number = add_phone_number.replace(' ', '')
        if add_phone_number != '':
            if re.match(settings.REGEX['PHONE'], no_space_add_phone_number) is None:
                raise forms.ValidationError('Please enter a valid phone number')
        return add_phone_number


class ContactSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your login and contact details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
