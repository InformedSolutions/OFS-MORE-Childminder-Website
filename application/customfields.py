"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- customfields.py --
@author: Informed Solutions
"""

import datetime
from django import forms
from django.forms import widgets
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _
from govuk_forms.widgets import SplitHiddenDateWidget, SplitDateWidget


# Custom creation of an expiry date (month and year) field
# Creating a widget class
class Widget(widgets.Widget):
    """
    Class to define the base widget from which any custom fields can inherit from, contains links to html and css from
    which to build thess widgets. This class shouldnt really be edited and has been taken from the govuk-template-forms
    library
    """
    input_classes = 'form-control'
    input_error_classes = 'form-control-error'

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        A method to define the attributes to build in the widget
        :param base_attrs: The set of attributes is used to build the attrs object which contains the exact css classes
        to use
        :param extra_attrs: Any extra attributes to be used
        :return: Returns the attributes object to be used in rendering of the form
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        css_classes = self.input_classes() if callable(self.input_classes) else self.input_classes
        attrs['class'] = ('%s %s' % (attrs.get('class', ''), css_classes)).strip()
        return attrs


# Creating a base multi-widget class
class MultiWidget(widgets.MultiWidget, Widget):
    """
    A class used to define a base widget that has the ability to contain multiple widgets
    """
    subwidget_group_classes = ()
    subwidget_label_classes = ()
    subwidget_labels = ()

    def get_context(self, name, value, attrs):
        """
        :param name: The name of the widget
        :param value:
        :param attrs: The attrs object from the base widget
        :return: Returns the list of classes for each subwidget
        """
        context = super().get_context(name, value, attrs)
        iterator = zip(context['widget']['subwidgets'],
                       self.subwidget_group_classes,
                       self.subwidget_label_classes,
                       self.subwidget_labels)
        for subwidget, group_classes, label_classes, label in iterator:
            subwidget.update(
                group_classes=group_classes,
                label_classes=label_classes,
                label=label,
            )
        return context

    def decompress(self, value):
        """
        This decompress should never get directly called as specifc widgets need to be implemented
        :param value:Anything that is passed into the Multiwidget class
        :return: NotImplementError specifies this class has not been implemented/inherited
        """
        raise NotImplementedError


class ExpirySplitDateWidget(MultiWidget):
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


class YearField(forms.IntegerField):
    """
    In integer field that accepts years between 1900 and now
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """

    def __init__(self, era_boundary=None, **kwargs):
        """
        When initialised, this field object will create attributes for later validation base of the current time and
        year, error messages and field options are specified here.
        :param era_boundary: If supplied, will limit how far back a user cna enter without raising an error
        :param kwargs: Any other key word arguments passed during the implementation of the class
        """
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        bounds_error = gettext('Check the expiry date or use a new card')
        options = {
            'min_value': self.current_year,
            'error_messages': {
                'min_value': bounds_error,
                'invalid': gettext('Check the expiry date or use a new card'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        """
        This will clean the two year value entered into the field in order to ensure the value entered is in the write
        century, for example, 68 will be changed to 1968 rather the 2068 as the latter has not occured yet
        :param value:The value object obtained from the form
        :return:This returns the cleaned value object (after cleaning specified above
        """
        value = self.to_python(value)
        if len(str(value)) > 2:
            raise forms.ValidationError('Check the expiry date or use a new card')
        if isinstance(value, int) and value < 100:
                value += self.century

        return super().clean(value)


class ExpirySplitDateField(forms.MultiValueField):
    """
    This class defines the validation for the month field and also the overall ordering and organisation for the two
    fields
    """
    widget = ExpirySplitDateWidget
    hidden_widget = SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Check the expiry date or use a new card')
    }

    def __init__(self, *args, **kwargs):
        """
        Standard constructor that defines what the month field should do, and which errors should be raised should
        certain events occur
        :param args: Standard arguments parameter
        :param kwargs: Standard key word arguments parameter
        """
        month_bounds_error = gettext('Check the expiry date or use a new card')

        # Field definition
        self.fields = [
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Check the expiry date or use a new card')
            }),
            # Uses a clean year field defined above
            YearField(),
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Uses compress as there are multiple values (compress is a replacement for clean in these cases
        :param data_list: The object containing each of the values
        :return: Returns the cleaned value object
        """
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return data_list[1], data_list[0]
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        """
        Populates the attributes of the widget with the values defined in the original widget creation
        :param widget: The widget to have its parameters populated
        :return: returns the attributes
        """
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, ExpirySplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class TimeKnownSplitDateWidget(MultiWidget):
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


class TimeKnownField(forms.MultiValueField):
    """
    Class that defines the field type used for both month and years in the TimeKnownWidget
    """
    widget = TimeKnownSplitDateWidget
    hidden_widget = SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Enter a valid date')
    }

    def __init__(self, *args, **kwargs):
        """
        The contructor defines each field for the object, the errors it can raise and the resultant error text should
        an error be returned
        :param args: Standard arguments parameter
        :param kwargs: Standard key word arguments parameter
        """
        month_bounds_error = gettext('Month must be between 1 and 11')
        year_bounds_error = gettext('You must have known the referee for at least 1 year')

        self.fields = [
            forms.IntegerField(min_value=0, error_messages={
                'min_value': year_bounds_error,
                'max_value': year_bounds_error,
                'invalid': gettext('You must have known the referee for at least 1 year')
            }),
            forms.IntegerField(max_value=11, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Month must be between 1 and 11')
            })
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Compresses the resultant data list into a single tuple for returning to wherever the result is called
        :param data_list: The list of field inputs
        :return: Atuple containing the amount of months and years known in the correct order
        """
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return data_list[1], data_list[0]
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        """
        Populates the attributes of the widget with the values defined in the original widget creation
        :param widget: The widget to have its parameters populated
        :return: returns the attributes
        """
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, ExpirySplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class SelectDateWidget(MultiWidget):
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


class CustomSplitDateFieldDOB(forms.MultiValueField):
    widget = SplitDateWidget
    hidden_widget = SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Please enter a valid date')
    }

    def __init__(self, *args, **kwargs):
        day_bounds_error = gettext('Day must be between 1 and 31')
        month_bounds_error = gettext('Month must be between 1 and 12')

        self.fields = [
            forms.IntegerField(min_value=1, max_value=31, error_messages={
                'min_value': day_bounds_error,
                'max_value': day_bounds_error,
                'invalid': gettext('Enter day as a number')
            }),
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Enter month as a number')
            }),
            CustomYearFieldDOB(),
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                return datetime.date(data_list[2], data_list[1], data_list[0])
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, SplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class CustomYearFieldDOB(forms.IntegerField):
    """
    In integer field that accepts years between 1900 and now
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """

    def __init__(self, era_boundary=None, **kwargs):
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # 2-digit dates are a minimum of 10 years ago by default
            era_boundary = self.current_year - self.century - 10
        self.era_boundary = era_boundary
        options = {
            'error_messages': {
                'invalid': gettext('Enter year as a number'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        value = self.to_python(value)
        if len(str(value)) < 4:
            raise forms.ValidationError('Please enter the whole year (4 digits)')
        if value < 1900:
            raise forms.ValidationError('Please check the year')
        if value > now().year:
            raise forms.ValidationError('Please check the year')
        return super().clean(value)


class CustomSplitDateField(forms.MultiValueField):
    widget = SplitDateWidget
    hidden_widget = SplitHiddenDateWidget
    default_error_messages = {
        'invalid': _('Please check the date of the course')
    }

    def __init__(self, bounds_error=None, min_value=2000, *args, **kwargs):
        day_bounds_error = gettext('Day must be between 1 and 31')
        month_bounds_error = gettext('Month must be between 1 and 12')

        self.fields = [
            forms.IntegerField(min_value=1, max_value=31, error_messages={
                'min_value': day_bounds_error,
                'max_value': day_bounds_error,
                'invalid': gettext('Enter day as a number')
            }),
            forms.IntegerField(min_value=1, max_value=12, error_messages={
                'min_value': month_bounds_error,
                'max_value': month_bounds_error,
                'invalid': gettext('Enter month as a number')
            }),
            CustomYearField(bounds_error=bounds_error, min_value=min_value),
        ]

        super().__init__(self.fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            try:
                if any(item in self.empty_values for item in data_list):
                    raise ValueError
                date_compressed = datetime.date(data_list[2], data_list[1], data_list[0])
                if date_compressed > now().date():
                    raise ValueError
                else:
                    return date_compressed
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'], code='invalid')
        return None

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if not isinstance(widget, SplitDateWidget):
            return attrs
        for subfield, subwidget in zip(self.fields, widget.widgets):
            if subfield.min_value is not None:
                subwidget.attrs['min'] = subfield.min_value
            if subfield.max_value is not None:
                subwidget.attrs['max'] = subfield.max_value
        return attrs


class CustomYearField(forms.IntegerField):
    """
    In integer field that accepts years between 1900 and now
    Allows 2-digit year entry which is converted depending on the `era_boundary`
    """

    def __init__(self, era_boundary=None, bounds_error=None, min_value=2000, **kwargs):
        self.current_year = now().year
        self.century = 100 * (self.current_year // 100)
        if era_boundary is None:
            # Interpret two-digit dates as this century if they are before the current year
            # otherwise interpret them as a year from the previous century
            era_boundary = self.current_year - self.century
        self.era_boundary = era_boundary
        if bounds_error is None:
            bounds_error = gettext('Please check the date of the course') % {
                'current_year': self.current_year
            }
        else:
            bounds_error = gettext(bounds_error)
        options = {
            'min_value': min_value,
            'max_value': self.current_year,
            'error_messages': {
                'min_value': bounds_error,
                'max_value': bounds_error,
                'invalid': gettext('Enter year as a number'),
            }
        }
        options.update(kwargs)
        super().__init__(**options)

    def clean(self, value):
        value = self.to_python(value)
        if isinstance(value, int) and value < 100:
            if value > self.era_boundary:
                value += self.century - 100
            else:
                value += self.century
        return super().clean(value)
