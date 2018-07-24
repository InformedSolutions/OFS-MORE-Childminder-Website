import re
from datetime import datetime, timedelta

from django import forms
from django.conf import settings

from application.customfields import TimeKnownField
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (Reference, ApplicantPersonalDetails)

from ..models import Application, UserDetails
from ..business_logic import childminder_references_and_user_email_duplication_check


def datetime_from_time_known(_years_known, _months_known):
    """
    Inner function to return datetime object using time known
    :param _years_known: number of years passed by user
    :param _months_known: number of months passed by user
    :return: datetime object
    """
    current_dt = datetime.now()
    if _years_known > current_dt.year-2:
        _years_known = current_dt.year-2
    if _months_known >= current_dt.month:
        _years_known += 1
        _months_known = 12 - abs(current_dt.month - _months_known)
    else:
        _months_known = current_dt.month - _months_known
    return current_dt.replace(year=current_dt.year - _years_known).replace(month=_months_known)


class ReferenceIntroForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class FirstReferenceForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': 'Please enter the first name of the referee'})
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': 'Please enter the last name of the referee'})
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True,
                                   error_messages={'required': 'Please tell us how the referee knows you'})
    time_known = TimeKnownField(label='How long have they known you?', required=True,
                                error_messages={'required': 'Please tell us how long you have known the referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(FirstReferenceForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]
            self.pk = reference_record.reference_id
            self.field_list = ['first_name', 'last_name', 'relationship', 'time_known']
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            obj = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)
            self.birth_time = (obj.birth_year, obj.birth_month, obj.birth_day)

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match(settings.REGEX['FIRST_NAME'], first_name) is None:
            raise forms.ValidationError('First name can only have letters')
        if len(first_name) > 100:
            raise forms.ValidationError("Referee's first name must be under 100 characters long")
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match(settings.REGEX['LAST_NAME'], last_name) is None:
            raise forms.ValidationError('Last name can only have letters')
        if len(last_name) > 100:
            raise forms.ValidationError("Referee's last name must be under 100 characters long")
        return last_name

    def clean_relationship(self):
        """
        Relationship validation
        :return: string
        """
        relationship = self.cleaned_data['relationship']
        if len(relationship) > 100:
            raise forms.ValidationError("Please enter 100 characters or less.")
        return relationship

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        birth_dt = datetime(year=self.birth_time[0], month=self.birth_time[1], day=self.birth_time[2])
        known_dt = datetime_from_time_known(years_known, months_known)
        d_now = datetime.now()
        if known_dt > d_now.replace(year=d_now.year-1):
            raise forms.ValidationError('You must have known the referee for at least 1 year')
        elif known_dt <= birth_dt:
            raise forms.ValidationError('Check the number of years and months you have entered')
        return years_known, months_known


class ReferenceFirstReferenceAddressForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=1).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError('Enter a valid UK postcode or enter the address manually')
        return postcode


class ReferenceFirstReferenceAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_line1 = forms.CharField(label='Address line 1', error_messages={
        'required': "Please enter the first line of the referee's address"})
    street_line2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': "Please enter the name of the town or city"})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})
    country = forms.CharField(label='Country', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=1)
            self.fields['street_line1'].initial = reference_record.street_line1
            self.fields['street_line2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country
            self.pk = reference_record.reference_id
            self.field_list = ['street_line1', 'street_line2', 'town', 'county', 'postcode',
                               'country']

    def clean_street_line1(self):
        """
        Street name and number validation
        :return: string
        """
        street_line1 = self.cleaned_data['street_line1']
        if len(street_line1) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_line1

    def clean_street_line2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_line2 = self.cleaned_data['street_line2']
        if len(street_line2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
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

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match(settings.REGEX['COUNTRY'],country) is None:
                raise forms.ValidationError('Please spell out the name of the country using letters')
            if len(country) > 50:
                raise forms.ValidationError('The name of the country must be under 50 characters long')
        return country


class ReferenceFirstReferenceAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': "Please select the referee's address"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceFirstReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class ReferenceFirstReferenceContactForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: first reference contact details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    phone_number = forms.CharField(label='Phone number',
                                   error_messages={'required': 'Please give a phone number for your first referee'})
    email_address = forms.CharField(label='Email address',
                                    error_messages={'required': 'Please give an email address for your first referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: first reference contact details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceFirstReferenceContactForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local,
                                                     reference=1)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if re.match(settings.REGEX['INTERNATIONAL_PHONE'], no_space_phone_number) is None:
                raise forms.ValidationError('Please enter a valid phone number')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        user_details_entry = UserDetails.objects.get(application_id=self.application_id_local)
        user_details_email = user_details_entry.email
        ref1_email = email_address
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            ref2 = Reference.objects.get(application_id=self.application_id_local, reference=2)
            ref2_email = ref2.email
        else:
            ref2_email = None

        if re.match(settings.REGEX['EMAIL'], email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        if not childminder_references_and_user_email_duplication_check(ref1_email, ref2_email):
            raise forms.ValidationError('Please enter a different email for each reference')
        if not childminder_references_and_user_email_duplication_check(user_details_email, ref1_email):
            raise forms.ValidationError('Please enter an email that is different to your own')
        return email_address


class SecondReferenceForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    first_name = forms.CharField(label='First name', required=True,
                                 error_messages={'required': 'Please enter the first name of the referee'})
    last_name = forms.CharField(label='Last name', required=True,
                                error_messages={'required': 'Please enter the name of the referee'})
    relationship = forms.CharField(label='How do they know you?', help_text='For instance, friend or neighbour',
                                   required=True,
                                   error_messages={'required': 'Please tell us how the referee knows you'})
    time_known = TimeKnownField(label='How long have they known you?', required=True,
                                error_messages={'required': 'Please tell us how long you have known the referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(SecondReferenceForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['first_name'].initial = reference_record.first_name
            self.fields['last_name'].initial = reference_record.last_name
            self.fields['relationship'].initial = reference_record.relationship
            self.fields['time_known'].initial = [reference_record.years_known, reference_record.months_known]
            self.pk = reference_record.reference_id
            self.field_list = ['first_name', 'last_name', 'relationship', 'time_known']
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            obj = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)
            self.birth_time = (obj.birth_year, obj.birth_month, obj.birth_day)

    def clean_first_name(self):
        """
        First name validation
        :return: string
        """
        first_name = self.cleaned_data['first_name']
        if re.match(settings.REGEX['FIRST_NAME'], first_name) is None:
            raise forms.ValidationError('First name can only have letters')
        if len(first_name) > 100:
            raise forms.ValidationError("Referee's first name must be under 100 characters long")
        return first_name

    def clean_last_name(self):
        """
        Last name validation
        :return: string
        """
        last_name = self.cleaned_data['last_name']
        if re.match(settings.REGEX['LAST_NAME'], last_name) is None:
            raise forms.ValidationError('Last name can only have letters')
        if len(last_name) > 100:
            raise forms.ValidationError("Referee's last name must be under 100 characters long")
        return last_name

    def clean_time_known(self):
        """
        Time known validation: reference must be known for 1 year or more
        :return: integer, integer
        """
        years_known = self.cleaned_data['time_known'][1]
        months_known = self.cleaned_data['time_known'][0]
        birth_dt = datetime(year=self.birth_time[0], month=self.birth_time[1], day=self.birth_time[2])
        known_dt = datetime_from_time_known(years_known, months_known)
        d_now = datetime.now()
        if known_dt > d_now.replace(year=d_now.year-1):
            raise forms.ValidationError('You must have known the referee for at least 1 year')
        elif known_dt <= birth_dt:
            raise forms.ValidationError('Check the number of years and months you have entered')
        return years_known, months_known


class ReferenceSecondReferenceAddressForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            self.fields['postcode'].initial = Reference.objects.get(application_id=self.application_id_local,
                                                                    reference=2).postcode

    def clean_postcode(self):
        """
        Postcode validation
        :return: string
        """
        postcode = self.cleaned_data['postcode']
        postcode_no_space = postcode.replace(" ", "")
        postcode_uppercase = postcode_no_space.upper()
        if re.match(settings.REGEX['POSTCODE_UPPERCASE'], postcode_uppercase) is None:
            raise forms.ValidationError('Enter a valid UK postcode or enter the address manually')
        return postcode


class ReferenceSecondReferenceAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_line1 = forms.CharField(label='Address line 1', error_messages={
        'required': "Please enter the first line of the referee's address"})
    street_line2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': "Please enter the name of the town or city"})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': "Please enter the referee's postcode"})
    country = forms.CharField(label='Country', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['street_line1'].initial = reference_record.street_line1
            self.fields['street_line2'].initial = reference_record.street_line2
            self.fields['town'].initial = reference_record.town
            self.fields['county'].initial = reference_record.county
            self.fields['postcode'].initial = reference_record.postcode
            self.fields['country'].initial = reference_record.country
            self.pk = reference_record.reference_id
            self.field_list = ['street_line1', 'street_line2', 'town', 'county', 'postcode',
                               'country']

    def clean_street_line1(self):
        """
        Street name and number validation
        :return: string
        """
        street_line1 = self.cleaned_data['street_line1']
        if len(street_line1) > 50:
            raise forms.ValidationError('The first line of the address must be under 50 characters long')
        return street_line1

    def clean_street_line2(self):
        """
        Street name and number line 2 validation
        :return: string
        """
        street_line2 = self.cleaned_data['street_line2']
        if len(street_line2) > 50:
            raise forms.ValidationError('The second line of the address must be under 50 characters long')
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

    def clean_country(self):
        """
        Country validation
        :return: string
        """
        country = self.cleaned_data['country']
        if country != '':
            if re.match(settings.REGEX['COUNTRY'],country) is None:
                raise forms.ValidationError('Please spell out the name of the country using letters')
            if len(country) > 50:
                raise forms.ValidationError('The name of the country must be under 50 characters long')
        return country


class ReferenceSecondReferenceAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': "Please select the referee's address"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(ReferenceSecondReferenceAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        self.fields['address'].choices = self.choices


class ReferenceSecondReferenceContactForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: second reference contact details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    phone_number = forms.CharField(label='Phone number',
                                   error_messages={'required': 'Please give a phone number for your second referee'})
    email_address = forms.CharField(label='Email address', error_messages={
        'required': 'Please give an email address for your second referee'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the 2 references: second reference contct details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(ReferenceSecondReferenceContactForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Reference.objects.filter(application_id=self.application_id_local, reference=2).count() > 0:
            reference_record = Reference.objects.get(application_id=self.application_id_local, reference=2)
            self.fields['phone_number'].initial = reference_record.phone_number
            self.fields['email_address'].initial = reference_record.email
            self.pk = reference_record.reference_id
            self.field_list = ['phone_number', 'email_address']

    def clean_phone_number(self):
        """
        Phone number validation
        :return: string
        """
        phone_number = self.cleaned_data['phone_number']
        no_space_phone_number = phone_number.replace(' ', '')
        if phone_number != '':
            if re.match(settings.REGEX['INTERNATIONAL_PHONE'], no_space_phone_number) is None:
                raise forms.ValidationError('Please enter a valid phone number')
        return phone_number

    def clean_email_address(self):
        """
        Email validation
        :return: string
        """
        email_address = self.cleaned_data['email_address']
        user_details_entry = UserDetails.objects.get(application_id=self.application_id_local)
        user_details_email = user_details_entry.email
        ref2_email = email_address
        if Reference.objects.filter(application_id=self.application_id_local, reference=1).count() > 0:
            ref1 = Reference.objects.get(application_id=self.application_id_local, reference=1)
            ref1_email = ref1.email
        else:
            ref1_email = None

        if re.match(settings.REGEX['EMAIL'], email_address) is None:
            raise forms.ValidationError('Please enter a valid email address')
        if len(email_address) > 100:
            raise forms.ValidationError('Please enter 100 characters or less')
        if not childminder_references_and_user_email_duplication_check(ref1_email, ref2_email):
            raise forms.ValidationError('Please enter a different email for each reference')
        if not childminder_references_and_user_email_duplication_check(user_details_email, ref2_email):
                raise forms.ValidationError('Please enter an email that is different to your own')
        return email_address


class ReferenceSummaryForm(ChildminderForms):
    """
    GOV.UK form for the 2 references: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
