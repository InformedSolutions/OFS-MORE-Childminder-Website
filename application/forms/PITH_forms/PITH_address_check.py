import collections
from datetime import date

from django import forms
from govuk_forms.widgets import InlineRadioSelect
from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets as govuk_widgets

from application.forms.PITH_forms.PITH_base_forms.PITH_multi_radio_form import PITHMultiRadioForm
from application.widgets import ConditionalPostInlineRadioSelect
from application.forms.fields import CustomSplitDateFieldDOB
from application.models import AdultInHome

import logging

log = logging.getLogger('')


class PITHAddressDetailsCheckForm(PITHMultiRadioForm):
    """
        GOV.UK form for the People in the Home: Non generic form for the PITHDBSTypeOfCheckView
        """
    field_label_classes = 'form-label-bold'
    error_summary_title = 'There was a problem on this page'
    error_summary_template_name = 'PITH_templates/PITH_error_summary.html'
    auto_replace_widgets = True

    def __init__(self, *args, **kwargs):
        self.application_id = kwargs.pop('id')
        self.adult = kwargs.pop('adult')
        self.PITH_same_address_field = kwargs.pop('PITH_same_address_field')
        self.PITH_moved_in_date_field = kwargs.pop('PITH_moved_in_date_field')
        self.pk = self.adult.pk

        self.PITH_moved_in_date_field_name = self.PITH_moved_in_date_field + str(self.adult.pk)
        self.PITH_same_address_field_name = self.PITH_same_address_field + str(self.adult.pk)
        self.base_fields = collections.OrderedDict([
            (self.PITH_same_address_field_name, self.get_choice_field_data())
        ])
        self.base_fields[self.PITH_moved_in_date_field_name] = self.get_moved_in_data()
        self.reveal_conditionally = self.get_reveal_conditionally()

        # ============================================================================================================ #
        # The code that follows is identical to that of gov_uk_forms v0.4 GOVUKForm.__init__(*args, **kwargs), barring
        # one exception: self.conditionally_revealed is an OrderedDict(), not a dict().
        # This is to prevent Python3.5 errors when not preserving order in which items are added to a dictionary.
        #
        # Thus we use the code in that __init__() and super back to the __init__() of forms.Form, using
        # super(GOVUKForm, self).__init__(*args, **kwargs),
        # not super(PITHDBSTypeOfCheckForm, self).__init__(*args, **kwargs)

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

    choice_field_name = 'adult_in_home_address'

    def get_options(self):
        return (
            (True, 'Yes'),
            (False, 'No')
        )

    def get_choice_field_data(self):
        return forms.ChoiceField(
            label='Is this where they live?',
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=False)

    def get_moved_in_data(self):
        return CustomSplitDateFieldDOB(
            label='Date they moved in',
            help_text='For example, 31 03 2016',
            required=False
        )

    def clean(self):
        super().clean()

        cleaned_PITH_same_address_field = self.cleaned_data[self.PITH_same_address_field_name] == 'True' \
            if self.cleaned_data.get(self.PITH_same_address_field_name) \
            else None
        cleaned_PITH_moved_in_date_field = self.cleaned_data[self.PITH_moved_in_date_field_name] \
            if self.cleaned_data.get(self.PITH_moved_in_date_field_name) \
            else None

        if cleaned_PITH_same_address_field == True:
            if cleaned_PITH_moved_in_date_field is None:
                if len(self.errors) == 0:
                    self.add_error(self.PITH_moved_in_date_field,
                           'Please enter the full date, including the day, month and year')
        if cleaned_PITH_same_address_field is None:
            self.add_error(self.PITH_same_address_field,
                           'Please say if they live at the same address as you')
        if cleaned_PITH_moved_in_date_field is not None and cleaned_PITH_moved_in_date_field < AdultInHome.objects.get(adult_id=self.adult.adult_id).date_of_birth.date():
            self.add_error(self.PITH_moved_in_date_field,
                        'Please enter a move in date which is after their date of birth')
        return self.cleaned_data

    def get_reveal_conditionally(self):
        return collections.OrderedDict([
            (self.PITH_same_address_field_name, {True: self.PITH_moved_in_date_field_name}),
            ])


