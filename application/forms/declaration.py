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


class DeclarationForm(ChildminderForms):
    """
    GOV.UK form for the Declaration: declaration page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    share_info_declare = forms.BooleanField(label='share information with other organisations', required=True,
                                            error_messages={
                                                'required': 'Confirm that you understand Ofsted will share information with other organisations'})
    display_contact_details_on_web = forms.BooleanField(label='display my name '
                                                              'and contact details '
                                                              'on their website so parents can find me '
                                                              '(optional)', required=False)
    suitable_declare = forms.BooleanField(label='I am suitable to look after children', required=True,
                                          error_messages={
                                              'required': 'Confirm that you are suitable to look after children'})
    information_correct_declare = forms.BooleanField(label='the information I have given is correct', required=True,
                                                     error_messages={
                                                         'required': 'Confirm that the information you have given is correct'})
    change_declare = forms.BooleanField(label='I will tell Ofsted if this information changes', required=True,
                                        error_messages={
                                            'required': 'Confirm that you will tell Ofsted if this information changes'})

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(DeclarationForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            share_info_declare = Application.objects.get(
                application_id=self.application_id_local).share_info_declare
            if share_info_declare is True:
                self.fields['share_info_declare'].initial = '1'
            elif share_info_declare is False:
                self.fields['share_info_declare'].initial = '0'

            display_contact_details_on_web = Application.objects.get(
                application_id=self.application_id_local).display_contact_details_on_web
            if display_contact_details_on_web is True:
                self.fields['display_contact_details_on_web'].initial = '1'
            elif display_contact_details_on_web is False:
                self.fields['display_contact_details_on_web'].initial = '0'

            suitable_declare = Application.objects.get(application_id=self.application_id_local).suitable_declare

            if suitable_declare is True:
                self.fields['suitable_declare'].initial = '1'
            elif suitable_declare is False:
                self.fields['suitable_declare'].initial = '0'

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


class PublishingYourDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Confirm your details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    publish_details = forms.BooleanField(label='I do not want my details published', required=False)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Declaration: declaration form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(PublishingYourDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if Application.objects.filter(application_id=self.application_id_local).count() > 0:
            publish_details = Application.objects.get(
                application_id=self.application_id_local).publish_details
            if publish_details is True:
                self.fields['publish_details'].initial = None
            elif publish_details is False:
                self.fields['publish_details'].initial = '1'


class DeclarationSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Confirm your details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
