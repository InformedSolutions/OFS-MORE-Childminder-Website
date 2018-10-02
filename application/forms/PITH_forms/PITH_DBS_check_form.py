import collections

from django import forms

from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets as govuk_widgets
from govuk_forms.widgets import NumberInput

from application.forms import childminder_dbs_duplicates_household_member_check
from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter

from application.models import Application

from application.widgets.ConditionalPostChoiceWidget import ConditionalPostInlineRadioSelect
from application.business_logic import update_adult_in_home


class PITHDBSCheckForm(PITHChildminderFormAdapter):
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
        self.dbs_field_no_update_name = self.dbs_field +'_no_update'+str(self.adult.pk)

        self.base_fields = collections.OrderedDict([
            (self.dbs_field_name, self.get_dbs_field_data()),
            (self.on_update_field_name, self.get_on_update_field_data()),
            (self.capita_field_name, self.get_capita_field_data()),
            (self.dbs_field_no_update_name, self.get_dbs_field_data())
        ])

        self.reveal_conditionally = self.get_reveal_conditionally()

        # ============================================================================================================ #
        # The code that follows is identical to that of gov_uk_forms v0.4 GOVUKForm.__init__(*args, **kwargs), barring
        # one exception: self.conditionally_revealed is an OrderedDict(), not a dict().
        # This is to prevent Python3.5 errors when not preserving order in which items are added to a dictionary.
        #
        # Thus we use the code in that __init__() and super back to the __init__() of forms.Form, using
        # super(GOVUKForm, self).__init__(*args, **kwargs), not super(PITHDBSCheckForm, self).__init__(*args, **kwargs)

        kwargs.setdefault('label_suffix', '')
        super(GOVUKForm, self).__init__(*args, **kwargs)

        if self.auto_replace_widgets:
            widget_replacements = govuk_widgets.widget_replacements
            if hasattr(self, 'widget_replacements'):
                widget_replacements = widget_replacements.copy().update(self.widget_replacements)
            for field in self.fields.values():
                field.widget = govuk_widgets.replace_widget(field.widget, widget_replacements)

        # XXX: This is an OrderedDict(), not a dict()
        self.conditionally_revealed = collections.OrderedDict([])

        for target_fields in self.reveal_conditionally.values():
            for target_field in target_fields.values():
                field = self.fields[target_field]
                self.conditionally_revealed[target_field] = {
                    'required': field.required,
                }
                field.required = False

        # ============================================================================================================ #

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
            required=False)

    def get_dbs_field_data(self):
        dbs_certificate_number_widget = NumberInput()
        dbs_certificate_number_widget.input_classes = 'inline form-control form-control-1-4'

        return forms.IntegerField(label='DBS certificate number',
                                  help_text='12-digit number on their certificate',
                                  required=False,
                                  error_messages={'required': 'Please enter their DBS certificate number'},
                                  widget=dbs_certificate_number_widget)

    def get_on_update_field_data(self):
        return forms.ChoiceField(
            label='Are they on the DBS update service?',
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=False,
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
        cleaned_dbs_field = self.data[self.dbs_field_name]\
            if self.data[self.dbs_field_name] != ""\
            else None
        cleaned_dbs_field_no_update = self.data[self.dbs_field_no_update_name] \
            if self.data[self.dbs_field_no_update_name] != "" \
            else None
        cleaned_on_update_field = self.cleaned_data[self.on_update_field_name] == 'True'\
            if self.cleaned_data[self.on_update_field_name] != ""\
            else None
        application = Application.objects.get(application_id=self.application_id)

        if cleaned_capita_field is not None:
            if cleaned_capita_field:
                self.clean_dbs(cleaned_dbs_field, self.dbs_field_name, application, cleaned_capita_field, cleaned_on_update_field)
            else:
                if cleaned_on_update_field is None:
                    self.add_error(self.on_update_field_name[:-36], 'Please say if this person is on the DBS update service')
                elif cleaned_on_update_field:
                    self.clean_dbs(cleaned_dbs_field_no_update, self.dbs_field_no_update_name, application, cleaned_capita_field, cleaned_on_update_field)
                else:
                    self.update_adult_in_home_fields(cleaned_capita_field, cleaned_on_update_field, '')
        else:
            self.add_error(self.capita_field_name[:-36], 'Please say if this person has an Ofsted DBS check')

        return self.cleaned_data

    def get_reveal_conditionally(self):
        return collections.OrderedDict([
            (self.on_update_field_name, {True: self.dbs_field_no_update_name}),
            (self.capita_field_name, {True: self.dbs_field_name,
                                      False: self.on_update_field_name})
        ])

    def clean_dbs(self, cleaned_dbs_value, field_name, application, cleaned_capita_value, cleaned_on_update_value):
        if cleaned_dbs_value is None:
            self.add_error(field_name[:-36], 'Please enter their DBS certificate number')
        elif len(str(cleaned_dbs_value)) != 12:
            self.add_error(field_name[:-36],
                           'Check the certificate: the number should be 12 digits long')
        elif childminder_dbs_duplicates_household_member_check(application, cleaned_dbs_value, self.adult):
            self.add_error(field_name[:-36], 'Please enter a different DBS number. '
                                       'You entered this number for someone in your childcare location')
        else:
            # TODO Move this code to more appropriate place (e.g form_valid)
            if '_no_update' in field_name:
                self.update_adult_in_home_fields(cleaned_capita_value, cleaned_on_update_value, cleaned_dbs_value)
            else:
                self.update_adult_in_home_fields(cleaned_capita_value, None, cleaned_dbs_value)

    def update_adult_in_home_fields(self, capita_value, on_update_value, dbs_value):
        update_adult_in_home(self.adult.pk, 'capita', capita_value)
        update_adult_in_home(self.adult.pk, 'on_update', on_update_value)
        update_adult_in_home(self.adult.pk, 'dbs_certificate_number', dbs_value)

    def check_flag(self):
        """
        Custom check_flag method for the PITHDBSCheckForm.

        This will:
            - Implement the parent class check_flag method.
            - Then see if the 'dbs_certificate_number' is flagged.
            - If it is flagged AND on_update is True (that is to say, that the person in the home has a
              non-capita/non-Ofsted DBS), then the flag is moved from the dbs_certificate_number field to the
              'dbs_certificate_number_no_update' field.

        This is required because:
            - There is a single database table for the dbs_certificate_number in the database.
            - The ARC flag is stored against a field with the name 'dbs_certificate_number', not against one named
              'dbs_certificate_number_no_update'.
            - So the parent class check_flag() method will add the flag against the 'dbs_certificate_number' field, even
              if the person in the home has a non-catpita/non-Ofsted DBS.

        Doing this here rather than in ARC means that ARC is consistent, whilst all bespoke PITH logic remains grouped
        together.

        :return: None
        """
        super(PITHDBSCheckForm, self).check_flag()
        if self.dbs_field_name in self.errors and not self.initial[self.capita_field_name]:
            error = self.errors.pop(self.dbs_field_name)
            self.add_error(self.dbs_field_no_update_name[:-36], error)  # index to remove uuid. add_error will append it
