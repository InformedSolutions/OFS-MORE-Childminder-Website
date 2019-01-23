import re

from django import forms
from django.conf import settings
from govuk_forms.widgets import InlineRadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ApplicantHomeAddress,
                                ApplicantPersonalDetails,
                                Application)
from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect

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
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError('Please enter a valid postcode')
        return postcode


class PersonalDetailsChildcareAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_line1 = forms.CharField(label='Address line 1',
                                   error_messages={'required': 'Please enter the first line of your address'})
    street_line2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

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
            self.fields['street_line1'].initial = childcare_address.street_line1
            self.fields['street_line2'].initial = childcare_address.street_line2
            self.fields['town'].initial = childcare_address.town
            self.fields['county'].initial = childcare_address.county
            self.fields['postcode'].initial = childcare_address.postcode
            self.pk = childcare_address.home_address_id
            self.field_list = ['street_line', 'street_line2', 'town', 'county', 'postcode']

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


class PersonalDetailsChildcareAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: childcare address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

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


class PersonalDetailsWorkingInOtherChildminderHomeForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: your childcare address details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    working_in_other_childminder_home = forms.ChoiceField(label="Is this another childminder's home?", choices=options,
                                                          widget=InlineRadioSelect, required=True,
                                                          error_messages={
                                                              'required': "Please say if you'll be working in another childminder's home"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: your childcare address details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsWorkingInOtherChildminderHomeForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            application = Application.objects.get(application_id=self.application_id_local)
            self.fields['working_in_other_childminder_home'].initial = application.working_in_other_childminder_home
            self.field_list = ['working_in_other_childminder_home']
            self.pk = application.pk


class PersonalDetailsOwnChildrenForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: your own children page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
    reveal_conditionally = {'own_children': {'True': 'reasons_known_to_social_services'}}

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )



    own_children = forms.ChoiceField(label="Are you known to council social services in regards to your own children?", choices=options,
                                     widget=ConditionalPostInlineRadioSelect, required=True,
                                     error_messages={'required': "Please say if you are known to council social services in regards to your own children"})

    reasons_known_to_social_services = forms.CharField(label="Tell us why",
                                    widget=forms.Textarea, required=True,
                                    error_messages={'required': "You must tell us why"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: your childcare own children form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsOwnChildrenForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            application = Application.objects.get(application_id=self.application_id_local)
            self.fields['own_children'].initial = application.own_children
            self.field_list = ['own_children']
            self.pk = application.pk

    def clean(self):
        cleaned_data = super().clean()
        own_children = cleaned_data.get('own_children')
        reasons_known = cleaned_data.get('reasons_known_to_social_services')

        if own_children == 'True':
            if reasons_known is '':
                self.add_error('reasons_known_to_social_services', 'You must tell us why')

        return cleaned_data

class PersonalDetailsSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
