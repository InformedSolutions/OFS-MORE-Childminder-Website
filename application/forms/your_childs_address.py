import re

from django import forms
from django.conf import settings

from ..forms.childminder import ChildminderForms
from ..forms_helper import full_stop_stripper
from ..models import ChildAddress


class ChildAddressForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        super(ChildAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        if ChildAddress.objects.filter(application_id=self.application_id_local, child=self.child).count() > 0:
            self.fields['postcode'].initial = ChildAddress.objects.get(application_id=self.application_id_local,
                                                                       child=self.child).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class YourChildManualAddressForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_line1 = forms.CharField(label='Address line 1', required=True, error_messages={
        'required': 'Please enter the first line of your address'})
    street_line2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city', required=True,
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', required=True,
                               error_messages={'required': 'Please enter your postcode'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.child = kwargs.pop('child')
        super(YourChildManualAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if ChildAddress.objects.filter(application_id=self.application_id_local,
                                       child=self.child).count() > 0:
            child_home_address = ChildAddress.objects.get(application_id=self.application_id_local,
                                                          child=self.child)
            self.fields['street_line1'].initial = child_home_address.street_line1
            self.fields['street_line2'].initial = child_home_address.street_line2
            self.fields['town'].initial = child_home_address.town
            self.fields['county'].initial = child_home_address.county
            self.fields['postcode'].initial = child_home_address.postcode
            self.pk = child_home_address.child_address_id
            self.field_list = ['street_line1', 'street_line2', 'town', 'county', 'postcode']

    def clean_street_line1(self):
        """
        Street name and number validation
        :return: string
        """
        street_line1 = self.cleaned_data['street_line1']
        if len(street_line1) > 50:
            raise forms.ValidationError('The first line of your address must be under 50 characters long')
        return street_line1

    def clean_street_line2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_line2 = self.cleaned_data['street_line2']
        if len(street_line2) > 50:
            raise forms.ValidationError('The second line of your address must be under 50 characters long')
        return street_line2

    def clean_town(self):
        """
        Town validation
        :return: string
        """
        town = self.cleaned_data['town']
        if re.match(settings.REGEX['TOWN'], town) is None:
            raise forms.ValidationError('Please spell out the name of the town or city using letters')
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
            if re.match(settings.REGEX['COUNTY'], county) is None:
                raise forms.ValidationError('Please spell out the name of the county using letters')
            if len(county) > 50:
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
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class YourChildrenAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(YourChildrenAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices
