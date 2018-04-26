"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- forms.py --

@author: Informed Solutions
"""

from application.forms.childminder import ChildminderForms


class DocumentsNeededForm(ChildminderForms):
    """
    GOV.UK form for the Documents you need for the visit page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class HomeReadyForm(ChildminderForms):
    """
    GOV.UK form for the Get your home ready page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class PrepareForInterviewForm(ChildminderForms):
    """
    GOV.UK form for the Get your home ready page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class ApplicationSavedForm(ChildminderForms):
    """
    GOV.UK form for the Application saved page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True
