from application.forms.childminder import ChildminderForms


class HealthIntroForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True


class HealthBookletForm(ChildminderForms):
    """
    GOV.UK form for the Your health: intro page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

