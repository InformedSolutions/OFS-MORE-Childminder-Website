from django import forms
from govuk_forms.widgets import InlineRadioSelect

from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper
from application.models import (EYFS)


class EYFSGuidanceForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: guidance page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class EYFSKnowledgeForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: knowledge page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('True', 'Yes'),
        ('False', 'No')
    )
    eyfs_understand = forms.ChoiceField(label='Do you understand the Early Years Foundation Stage?', choices=options,
                                        widget=InlineRadioSelect, required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: knowledge form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSKnowledgeForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_understand'].initial = eyfs_record.eyfs_understand


class EYFSTrainingForm(ChildminderForms):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    eyfs_training_declare = forms.BooleanField(label='I will go on an early years training course', required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: training form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSTrainingForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['eyfs_training_declare'].initial = eyfs_record.eyfs_training_declare


class EYFSQuestionsForm(ChildminderForms):
    """
    GOV.UK form for the EYFS: training page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    share_info_declare = forms.BooleanField(label='I am happy to answer questions about my early years knowledge',
                                            required=True)

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Early Years knowledge: questions form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id_local = kwargs.pop('id')
        super(EYFSQuestionsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)
        # If information was previously entered, display it on the form
        if EYFS.objects.filter(application_id=self.application_id_local).count() > 0:
            eyfs_record = EYFS.objects.get(application_id=self.application_id_local)
            self.fields['share_info_declare'].initial = eyfs_record.share_info_declare


class EYFSSummaryForm(ChildminderForms):
    """
    GOV.UK form for the Early Years knowledge: summary page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
