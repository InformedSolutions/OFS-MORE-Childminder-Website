from django import forms

from application.forms.childminder import ChildminderForms
from application.models import (Application)
from application.forms_helper import full_stop_stripper
from django import forms

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (Application)


class DeclarationIntroForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class DeclarationConfirmationOfUnderstandingForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    background_check_declare = forms.BooleanField(label='carry out background checks', required=True)
    inspect_home_declare = forms.BooleanField(label='inspect my home', required=True)
    interview_declare = forms.BooleanField(label='interview me', required=True)
    share_info_declare = forms.BooleanField(label='share information with other organisations', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConfirmationOfUnderstandingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            background_check_declare = Application.objects.get(
                application_id=self.application_id_local).background_check_declare
            if background_check_declare is True:
                self.fields['background_check_declare'].initial = '1'
            elif background_check_declare is False:
                self.fields['background_check_declare'].initial = '0'
            inspect_home_declare = Application.objects.get(
                application_id=self.application_id_local).inspect_home_declare
            if inspect_home_declare is True:
                self.fields['inspect_home_declare'].initial = '1'
            elif inspect_home_declare is False:
                self.fields['inspect_home_declare'].initial = '0'
            interview_declare = Application.objects.get(
                application_id=self.application_id_local).interview_declare
            if interview_declare is True:
                self.fields['interview_declare'].initial = '1'
            elif interview_declare is False:
                self.fields['interview_declare'].initial = '0'
            share_info_declare = Application.objects.get(
                application_id=self.application_id_local).share_info_declare
            if share_info_declare is True:
                self.fields['share_info_declare'].initial = '1'
            elif share_info_declare is False:
                self.fields['share_info_declare'].initial = '0'


class DeclarationConfirmationOfDeclarationForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    information_correct_declare = forms.BooleanField(label='the information I have given is correct', required=True,
                                                     error_messages={'required': 'You need to confirm this'})
    change_declare = forms.BooleanField(label='I will tell Ofsted if this information changes', required=True,
                                        error_messages={'required': 'You need to confirm this'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConfirmationOfDeclarationForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            information_correct_declare = Application.objects.get(
                application_id=self.application_id_local).information_correct_declare
            if information_correct_declare is True:
                self.fields['information_correct_declare'].initial = '1'
            elif information_correct_declare is False:
                self.fields['information_correct_declare'].initial = '0'
            change_declare = Application.objects.get(application_id=self.application_id_local).change_declare
            if change_declare is True:
                self.fields['change_declare'].initial = '1'
            elif change_declare is False:
                self.fields['change_declare'].initial = '0'


class DeclarationConsentToSharingForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page (optional section about sharing details on web)
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'error-summary.html'
    auto_replace_widgets = True

    display_contact_details_on_web = forms.BooleanField(label='display my name '
                                                              'and contact details '
                                                              'on their website so parents can find me '
                                                              '(optional)', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationConsentToSharingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            display_contact_details_on_web = Application.objects.get(
                application_id=self.application_id_local).display_contact_details_on_web
            if display_contact_details_on_web is True:
                self.fields['display_contact_details_on_web'].initial = '1'
            elif display_contact_details_on_web is False:
                self.fields['display_contact_details_on_web'].initial = '0'


class DeclarationSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Confirm your details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
