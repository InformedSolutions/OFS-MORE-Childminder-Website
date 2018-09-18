from django import forms
from govuk_forms.widgets import InlineRadioSelect, NumberInput

from application.forms import ChildminderForms, childminder_dbs_duplicates_household_member_check
from application.models import Application

from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect
from application.business_logic import update_adult_in_home


class PITHDBSCheckForm(ChildminderForms):
    """
    GOV.UK form for the People in the Home: Non generic form for the DBSCheckView.
    """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem with your DBS details'
    error_summary_template_name = 'PITH_templates/PITH_error_summary.html'
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):
        self.application_id = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.capita_field = kwargs.pop('capita_field')
        self.dbs_field = kwargs.pop('dbs_field')
        self.on_update_field = kwargs.pop('on_update_field')
        self.pk = self.adult.pk

        self.capita_field_name = self.capita_field + str(self.adult.pk)
        self.dbs_field_name = self.dbs_field + str(self.adult.pk)
        self.on_update_field_name = self.on_update_field + str(self.adult.pk)

        self.base_fields = {
            self.dbs_field_name: self.get_dbs_field_data(),
            self.on_update_field_name: self.get_on_update_field_data(),
            self.capita_field_name: self.get_capita_field_data()
        }

        self.reveal_conditionally = self.get_reveal_conditionally()

        super().__init__(*args, **kwargs)

        self.field_list = [*self.fields]

    def get_options(self):
        return (
            (True, 'Yes'),
            (False, 'No')
        )

    def get_capita_field_data(self):
        return forms.ChoiceField(
            label='Do they have an Ofsted DBS check?',
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=True,
            error_messages={'required': 'Please say if this person has an Ofsted DBS check'})

    def get_dbs_field_data(self):
        dbs_certificate_number_widget = NumberInput()
        dbs_certificate_number_widget.input_classes = 'inline form-control form-control-1-4'

        return forms.IntegerField(label='DBS certificate number',
                                  help_text='12-digit number on their certificate',
                                  required=True,
                                  error_messages={'required': 'Please enter their DBS certificate number'},
                                  widget=dbs_certificate_number_widget)

    def get_on_update_field_data(self):
        return forms.ChoiceField(
            label='Are they on the DBS update service?',
            choices=self.get_options(),
            widget=InlineRadioSelect,
            required=True,
            error_messages={'required': 'Please say if this person is on the DBS update service'})

    def clean(self):
        """
        Nullify fields
        DBS field validation
        :return: DBS field string
        """
        super().clean()

        cleaned_capita_field = self.cleaned_data[self.capita_field_name] == 'True'\
            if self.cleaned_data.get(self.capita_field_name)\
            else None
        cleaned_dbs_field = self.cleaned_data[self.dbs_field_name]\
            if self.cleaned_data[self.dbs_field_name] != ""\
            else None
        cleaned_on_update_field = self.cleaned_data[self.on_update_field_name] == 'True'\
            if self.cleaned_data[self.on_update_field_name] != ""\
            else None
        application = Application.objects.get(application_id=self.application_id)

        if cleaned_capita_field is not None:
            if cleaned_capita_field:
                if cleaned_dbs_field is None:
                    self.add_error(self.dbs_field_name, 'Please say if this person has an Ofsted DBS check')
                elif len(str(cleaned_dbs_field)) != 12:
                    self.add_error(self.dbs_field_name, 'Check the certificate: the number should be 12 digits long')
                elif childminder_dbs_duplicates_household_member_check(application, cleaned_dbs_field):
                    self.add_error(self.dbs_field_name, 'Please enter a different DBS number. '
                                                        'You entered this number for someone in your childcare location')
                else:
                    #TODO Move this code to more appropriate place (e.g form_valid)
                    update_adult_in_home(self.adult.pk, 'capita', cleaned_capita_field)
                    update_adult_in_home(self.adult.pk, 'on_update', None)
                    update_adult_in_home(self.adult.pk, 'dbs_certificate_number', cleaned_dbs_field)

            elif not cleaned_capita_field:
                if cleaned_on_update_field is None:
                    self.add_error(self.on_update_field_name, 'Please say if this person is on the DBS update service')
                else:
                    update_adult_in_home(self.adult.pk, 'capita', cleaned_capita_field)
                    update_adult_in_home(self.adult.pk, 'on_update', cleaned_on_update_field)
                    update_adult_in_home(self.adult.pk, 'dbs_certificate_number', '')

        return self.cleaned_data

    def get_reveal_conditionally(self):
        return {self.capita_field_name: {True: self.dbs_field_name,
                                         False: self.on_update_field_name}}