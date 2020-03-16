import collections

from django import forms

from govuk_forms.forms import GOVUKForm
from govuk_forms import widgets as govuk_widgets

from application.forms.PITH_forms.PITH_base_forms.PITH_childminder_form_retrofit import PITHChildminderFormAdapter
from application.widgets import ConditionalPostInlineRadioSelect
from django.utils.safestring import mark_safe


class PITHDBSTypeOfCheckForm(PITHChildminderFormAdapter):
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
        self.ask_if_enhanced_check = kwargs.pop('ask_if_enhanced_check')
        self.enhanced_check_field = kwargs.pop('enhanced_check_field')
        self.on_update_field = kwargs.pop('on_update_field')
        self.pk = self.adult.pk

        self.enhanced_check_field_name = self.enhanced_check_field + str(self.adult.pk)
        self.on_update_field_name = self.on_update_field + str(self.adult.pk)

        self.base_fields = collections.OrderedDict([
            (self.on_update_field_name, self.get_on_update_field_data()),
        ])
        if self.ask_if_enhanced_check:
            self.base_fields[self.enhanced_check_field_name] = self.get_enhanced_check_field_data()

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

    def get_options(self):
        return (
            (True, 'Yes'),
            (False, 'No')
        )

    def get_enhanced_check_field_data(self):
        return forms.ChoiceField(
            label=mark_safe('Is their DBS check:<ul style="list-style-type: disc; padding-left: 50px;"><li>an '
                        'enhanced check with barred lists?</li><li>if they live in the home childcare is taking place '
                        'in, is the check also for a <a '
                        'href="https://www.gov.uk/government/publications/dbs-home-based-positions-guide/home-based'
                        '-position-definition-and-guidance">home-based role</a>?</li></ul>'),
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=False)

    def get_on_update_field_data(self):
        return forms.ChoiceField(
            label='Are they on the DBS Update Service?',
            choices=self.get_options(),
            widget=ConditionalPostInlineRadioSelect,
            required=False)

    def clean(self):
        super().clean()

        cleaned_enhanced_check_field = self.cleaned_data[self.enhanced_check_field_name] == 'True'\
            if self.cleaned_data.get(self.enhanced_check_field_name)\
            else None
        cleaned_on_update_field = self.cleaned_data[self.on_update_field_name] == 'True'\
            if self.cleaned_data[self.on_update_field_name] != ""\
            else None

        if self.ask_if_enhanced_check and cleaned_enhanced_check_field is None:
            self.add_error(self.enhanced_check_field,
                           'Please say if they have an enhanced check for home-based childcare')

        enhanced_yes = cleaned_enhanced_check_field is not None and cleaned_enhanced_check_field

        if (enhanced_yes or not self.ask_if_enhanced_check) and cleaned_on_update_field is None:
            self.add_error(self.on_update_field,
                           'Please say if they are on the DBS Update Service')

        return self.cleaned_data

    def get_reveal_conditionally(self):
        if self.ask_if_enhanced_check:
            return collections.OrderedDict([
                (self.enhanced_check_field_name, {True: self.on_update_field_name})
            ])
        else:
            return collections.OrderedDict()
