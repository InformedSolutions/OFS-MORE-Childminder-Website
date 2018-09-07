from application.forms import ChildminderForms
from application.models import AdultInHome


class PITHRadioForm(ChildminderForms):
    """
    GOV.UK form for the Criminal record check: generic radio button form
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    choice_field_name = 'generic_choice_field_name'
    field_name = None

    def __init__(self, *args, **kwargs):
        """
        Method to configure the initialisation of the Your criminal record (DBS) check: details form
        :param args: arguments passed to the form
        :param kwargs: keyword arguments passed to the form, e.g. application ID
        """
        self.application_id = kwargs.pop('id')
        self.field_name = kwargs.pop('field_name')
        super().__init__(*args, **kwargs)

        self.fields[self.field_name] = self.get_choice_field_data()
        self.field_list = [*self.fields]

        if AdultInHome.objects.filter(application_id=self.application_id).exists():
            PITH_record = AdultInHome.objects.get(application_id=self.application_id)
            self.pk = PITH_record.pk

    def get_options(self):
        options = (
            ('True', 'Yes'),
            ('False', 'No')
        )
        return options

    def get_choice_field_data(self):
        raise NotImplementedError("No choice field was inherited.")