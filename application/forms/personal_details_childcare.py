import re

from django import forms

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ApplicantHomeAddress,
                                ApplicantPersonalDetails)


class PersonalDetailsChildcareAddressForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               childcare_address='True').postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsChildcareAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_name_and_number = forms.CharField(label='Address line 1',
                                             error_messages={'required': 'Please enter the first line of the address'})
    street_name_and_number2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter the postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsChildcareAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               childcare_address='True').count() > 0:
            childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                 childcare_address='True')
            self.fields['street_name_and_number'].initial = childcare_address.street_line1
            self.fields['street_name_and_number2'].initial = childcare_address.street_line2
            self.fields['town'].initial = childcare_address.town
            self.fields['county'].initial = childcare_address.county
            self.fields['postcode'].initial = childcare_address.postcode
            self.pk = childcare_address.child_id
            self.field_list = ['street_name_and_number', 'street_name_and_number2', 'town', 'county', 'postcode']

    def clean_street_name_and_number(self):
        """
        Street name and number validation
        :return: string
        """
        street_name_and_number = self.cleaned_data['street_name_and_number']
        if len(street_name_and_number) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_name_and_number

    def clean_street_name_and_number2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_name_and_number2 = self.cleaned_data['street_name_and_number2']
        if len(street_name_and_number2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
        return street_name_and_number2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match("^[A-Za-z- ]+$", town) is None:
            raise forms.ValidationError('Please spell out the the name of the town or city using letters')
        if len(town) > 50:
            raise forms.ValidationError('The name of the town or city must be under 50 characters long')
        return town

    def clean_county(self):
        """
        County validation
        :return: string
        """
        county = self.cleaned_data['county']
        if county != '':
            if re.match("^[A-Za-z- ]+$", county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 100:
                raise forms.ValidationError('The name of the county must be under 50 characters long')
        return county

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match("^[A-Z]{1,2}[0-9]{1,2}[A-Z]?[0-9][A-Z][A-Z]$", postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsChildcareAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select the address from the list'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: childcare address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsChildcareAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class PersonalDetailsSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
