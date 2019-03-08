import datetime

from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from govuk_forms import widgets as gov


class ConditionalPostChoiceWidget(gov.ChoiceWidget):
    template_name = 'widgets/multiple-select-post-conditional.html'
    option_template_name = 'widgets/multiple-select-option-post-conditional.html'


class ConditionalPostInlineRadioSelect(ConditionalPostChoiceWidget, gov.RadioSelect):
    field_group_classes = 'inline'
    pass


class ExpirySplitDateWidget(gov.MultiWidget):
    """
    This is an implementation of the Multiwidget class used to ask for an expiry date of a credit card, this takes base
    code from the default SplitDateWidget class in govuk-template-forms
    """
    template_name = 'govuk_forms/widgets/split-date.html'
    subwidget_group_classes = ('form-group form-group-month',
                               'form-group form-group-year')
    subwidget_label_classes = ('form-label', 'form-label')  # or form-label-bold
    subwidget_labels = (_('Month'), _('Year'))

    def __init__(self, attrs=None):
        """
        Initialisation of the class which defines the two date widgets (month and year) that will be used in the widget
        :param attrs: Any attributes to be passed to the individual widget definitions
        """
        date_widgets = (widgets.NumberInput(attrs=attrs),
                        widgets.NumberInput(attrs=attrs),)
        super().__init__(date_widgets, attrs)

    def decompress(self, value):
        """
        Cleaning/Decompressing this class will result in this method being called, this will return the two entry parts
        should they exist, will returned nothing if called with empty parameters
        :param value: The object that contains the value of both the expiry month and the expiry year
        :return:
        """
        if value:
            return [value.month, value.year]
        return [None, None]


class TimeKnownSplitDateWidget(gov.MultiWidget):
    """
    A class to define the overall split date widget for implementing the time known date type and validation
    """
    template_name = 'govuk_forms/widgets/split-date.html'
    subwidget_group_classes = ('form-group form-group-year',
                               'form-group form-group-month',)
    subwidget_label_classes = ('form-hint', 'form-hint')
    subwidget_labels = (_('Years'), _('Months'))

    def __init__(self, attrs=None):
        """
        Constructor defines both the field types to be used in the two dates
        :param attrs: Any attributes to be passed into the individual widget creation
        """
        date_widgets = (widgets.NumberInput(attrs=attrs),
                        widgets.NumberInput(attrs=attrs),)
        super().__init__(date_widgets, attrs)

    def decompress(self, value):
        """
        Parses out each field from the resultant value object from the form
        :param value: The object to be parsed
        :return: Returns a list of the parsed values
        """
        if value:
            return [value[0], value[1]]
        return [None, None]


class SelectDateWidget(gov.MultiWidget):
    template_name = 'govuk_forms/widgets/split-date.html'
    select_widget = widgets.Select
    none_value = (0, _('Not set'))
    subwidget_group_classes = ('form-group form-group-month-select',
                               'form-group form-group-year-select')
    subwidget_label_classes = ('form-label', 'form-label')  # or form-label-bold
    subwidget_labels = (_('Month'), _('Year'))

    def __init__(self, attrs=None, years=None, months=None, empty_label=None):
        this_year = datetime.date.today().year
        self.years = []
        year_gen = ((i, i) for i in years or range(this_year, this_year + 10))
        self.years.append((None, 'YYYY'))
        for year in year_gen:
            self.years.append(year)
        self.months = []
        month_gen = ((i, i) for i in months or range(1, 13))
        self.months.append((None, 'MM'))
        for month in month_gen:
            self.months.append(month)

        if isinstance(empty_label, (list, tuple)):
            self.year_none_value = (0, empty_label[0])
            self.month_none_value = (0, empty_label[1])
        else:
            none_value = (0, empty_label) if empty_label is not None else self.none_value
            self.year_none_value = none_value
            self.month_none_value = none_value

        date_widgets = (self.select_widget(attrs=attrs, choices=self.months),
                        self.select_widget(attrs=attrs, choices=self.years))
        super().__init__(date_widgets, attrs=attrs)

    def get_context(self, name, value, attrs):
        iterators = zip(
            self.widgets,
            (self.months, self.years),
            (self.month_none_value, self.year_none_value)
        )
        for widget, choices, none_value in iterators:
            widget.is_required = self.is_required
            widget.choices = choices if self.is_required else [none_value] + choices
        return super().get_context(name, value, attrs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]