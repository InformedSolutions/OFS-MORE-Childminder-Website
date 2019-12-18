import re
from datetime import date

from django import forms
from django.conf import settings
from govuk_forms.widgets import InlineRadioSelect

from application.forms.fields import CustomSplitDateFieldDOB
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (ApplicantHomeAddress,
                                ApplicantPersonalDetails)
from application.utils import date_formatter


class PersonalDetailsHomeAddressForm(ChildminderForms):
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
        super(PersonalDetailsHomeAddressForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            self.fields['postcode'].initial = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                               current_address=True).postcode
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


class PersonalDetailsHomeAddressManualForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for manual entry
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    street_line1 = forms.CharField(label='Address line 1', error_messages={
        'required': 'Please enter the first line of your address'})
    street_line2 = forms.CharField(label='Address line 2', required=False)
    town = forms.CharField(label='Town or city',
                           error_messages={'required': 'Please enter the name of the town or city'})
    county = forms.CharField(label='County (optional)', required=False)
    postcode = forms.CharField(label='Postcode', error_messages={'required': 'Please enter your postcode'})

    moved_in_date = CustomSplitDateFieldDOB(
        label='Date you moved in',
        help_text='For example, 31 03 2016',
        error_messages={'required': 'Please enter the full date, including the day, month and year'}
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for manual entry
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsHomeAddressManualForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                               current_address=True).count() > 0:
            applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)
            self.fields['street_line1'].initial = applicant_home_address.street_line1
            self.fields['street_line2'].initial = applicant_home_address.street_line2
            self.fields['town'].initial = applicant_home_address.town
            self.fields['county'].initial = applicant_home_address.county
            self.fields['postcode'].initial = applicant_home_address.postcode
            self.pk = applicant_home_address.home_address_id
            self.field_list = ['street_line1', 'street_line2', 'town', 'county', 'postcode']
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            personal_details_record = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)

            moved_in_day, moved_in_month, moved_in_year = date_formatter(personal_details_record.moved_in_day,
                                                                   personal_details_record.moved_in_month,
                                                                   personal_details_record.moved_in_year)
            self.fields['moved_in_date'].initial = [moved_in_day, moved_in_month, moved_in_year]
            self.pk = personal_details_record.personal_detail_id
            self.field_list = ['course_date']

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

    def clean_moved_in_date(self):
        """
        Course date validation (calculate date is in the future)
        :return: course day, course month, course year
        """
        moved_in_day = self.cleaned_data['moved_in_date'].day
        moved_in_month = self.cleaned_data['moved_in_date'].month
        moved_in_year = self.cleaned_data['moved_in_date'].year
        moved_in_date = date(moved_in_year, moved_in_month, moved_in_day)
        today = date.today()
        date_today_diff = today.year - moved_in_date.year - (
                (today.month, today.day) < (moved_in_date.month, moved_in_date.day))
        if date_today_diff < 0:
            raise forms.ValidationError('Please enter a past date')
        if len(str(moved_in_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return moved_in_day, moved_in_month, moved_in_year


class PersonalDetailsHomeAddressLookupForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: home address page for postcode search results
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    address = forms.ChoiceField(label='Select address', required=True,
                                error_messages={'required': 'Please select your address'})

    moved_in_date = CustomSplitDateFieldDOB(
        label='Date you moved in',
        help_text='For example, 31 03 2016',
        error_messages={'required': 'Please enter the full date, including the day, month and year'}
    )

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: home address form for postcode search
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        self.choices = kwargs.pop('choices')
        super(PersonalDetailsHomeAddressLookupForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        if ApplicantPersonalDetails.objects.filter(application_id=self.application_id_local).count() > 0:
            personal_details_record = ApplicantPersonalDetails.objects.get(application_id=self.application_id_local)

            moved_in_day, moved_in_month, moved_in_year = date_formatter(personal_details_record.moved_in_day,
                                                                   personal_details_record.moved_in_month,
                                                                   personal_details_record.moved_in_year)
            self.fields['moved_in_date'].initial = [moved_in_day, moved_in_month, moved_in_year]
            self.pk = personal_details_record.personal_detail_id
            self.field_list = ['course_date']
        self.fields['address'].choices = self.choices

    def clean_moved_in_date(self):
        """
        Course date validation (calculate date is in the future)
        :return: course day, course month, course year
        """
        moved_in_day = self.cleaned_data['moved_in_date'].day
        moved_in_month = self.cleaned_data['moved_in_date'].month
        moved_in_year = self.cleaned_data['moved_in_date'].year
        moved_in_date = date(moved_in_year, moved_in_month, moved_in_day)
        today = date.today()
        date_today_diff = today.year - moved_in_date.year - (
                (today.month, today.day) < (moved_in_date.month, moved_in_date.day))
        if date_today_diff < 0:
            raise forms.ValidationError('Please enter a past date')
        if len(str(moved_in_year)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        return moved_in_day, moved_in_month, moved_in_year

class PersonalDetailsLocationOfCareForm(ChildminderForms):
    """
    GOV.UK form for the Your personal details: location of care page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    childcare_location = forms.ChoiceField(label='Is this where you will be looking after the children?',
                                           choices=options,
                                           widget=InlineRadioSelect, required=True,
                                           error_messages={
                                               'required': "Please say if this is where you'll be looking after the children"})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your personal details: location of care form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PersonalDetailsLocationOfCareForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=self.application_id_local).personal_detail_id
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).count() > 0:
            address = ApplicantHomeAddress.objects.get(
                personal_detail_id=personal_detail_id, current_address=True)
            self.fields['childcare_location'].initial = address.childcare_address
            self.field_list = ['childcare_location']
            self.pk = address.pk
