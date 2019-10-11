"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- fields.py --
@author: Informed Solutions
"""

import datetime
import govuk_forms.widgets

from django import forms
from django.utils.timezone import now
from django.utils.translation import gettext, gettext_lazy as _

from application.widgets import ExpirySplitDateWidget, TimeKnownSplitDateWidget


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
            raise forms.ValidationError('Please enter the last 2 digits of the year')
        if isinstance(value, int) and value < 100:
                value += self.century

        return super().clean(value)


class ExpirySplitDateField(forms.MultiValueField):
    """
    This class defines the validation for the month field and also the overall ordering and organisation for the two
    fields
    """
    widget = ExpirySplitDateWidget
    hidden_widget = govuk_forms.widgets.SplitHiddenDateWidget
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


class TimeKnownField(forms.MultiValueField):
    """
    Class that defines the field type used for both month and years in the TimeKnownWidget
    """
    widget = TimeKnownSplitDateWidget
    hidden_widget = govuk_forms.widgets.SplitHiddenDateWidget
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


class CustomSplitDateFieldDOB(forms.MultiValueField):
    widget = govuk_forms.widgets.SplitDateWidget
    hidden_widget = govuk_forms.widgets.SplitHiddenDateWidget
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
        if not isinstance(widget, govuk_forms.widgets.SplitDateWidget):
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
    widget = govuk_forms.widgets.SplitDateWidget
    hidden_widget = govuk_forms.widgets.SplitHiddenDateWidget
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
        if not isinstance(widget, govuk_forms.widgets.SplitDateWidget):
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
