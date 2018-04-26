import re
from datetime import date

from django import forms
from django.conf import settings
from govuk_forms.widgets import RadioSelect

from application.customfields import ExpirySplitDateField, ExpirySplitDateWidget
from application.forms.childminder import ChildminderForms
from application.forms_helper import full_stop_stripper


class PaymentForm(ChildminderForms):
    """
    GOV.UK form for the Payment selection page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('Credit', 'Credit or debit card'),
        ('PayPal', 'PayPal')
    )
    payment_method = forms.ChoiceField(label='How would you like to pay?', choices=options,
                                       widget=RadioSelect, required=True,
                                       error_messages={'required': 'Please select how you would like to pay'})


class PaymentDetailsForm(ChildminderForms):
    """
    GOV.UK form for the Payment details page
    """
    field_label_classes = 'form-label-bold'
    error_summary_template_name = 'standard-error-summary.html'
    auto_replace_widgets = True

    options = (
        ('a', 'Alpha'),
        ('b', 'Beta')
    )
    grouped_options = (
        ('First', options),
        ('Second', (('c', 'Gamma'), ('d', 'Delta'))),
    )
    card_type_options = (
        (None, '(Please select)'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('american_express', 'American Express'),
        ('maestro', 'Maestro')
    )
    card_type = forms.ChoiceField(label='Card type', choices=card_type_options, required=True,
                                  error_messages={'required': 'Please select the type of card'})
    card_number = forms.CharField(label='Card number', required=True,
                                  error_messages={'required': 'Please enter the number on your card'})
    expiry_date = ExpirySplitDateField(label='Expiry date', required=True, widget=ExpirySplitDateWidget,
                                       help_text='For example, 10/20',
                                       error_messages={'required': 'Please enter the expiry date on the card'})
    cardholders_name = forms.CharField(label="Cardholder's name", required=True,
                                       error_messages={'required': 'Please enter the name of the cardholder'})
    card_security_code = forms.IntegerField(label='Card security code',
                                            help_text='3 or 4 digit number on back of card', required=True,
                                            error_messages={
                                                'required': 'Please enter the 3 or 4 digit card security code'})

    def __init__(self, *args, **kwargs):
        super(PaymentDetailsForm, self).__init__(*args, **kwargs)
        full_stop_stripper(self)

    def clean_card_type(self):
        card_type = self.cleaned_data['card_type']
        if not card_type:
            raise forms.ValidationError('Please select the type of card')

    def clean_card_number(self):
        """
        Card number validation
        :return: string
        """
        card_type = self.data['card_type']
        card_number = self.cleaned_data['card_number']
        card_number = re.sub('[ -]+', '', card_number)
        # noinspection PyPep8
        try:
            int(card_number)
        except:
            # At the moment this is a catch all error, in the case of there being multiple error
            # types this must be revisited
            raise forms.ValidationError('Please check the number on your card')
        if settings.VISA_VALIDATION:
            if card_type == 'visa':
                if re.match("^4[0-9]{12}(?:[0-9]{3})?$", card_number) is None:
                    raise forms.ValidationError('Please check the number on your card')
        if card_type == 'mastercard':
            if re.match("^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$",
                        card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        elif card_type == 'american_express':
            if re.match("^3[47][0-9]{13}$", card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        elif card_type == 'maestro':
            if re.match("^(?:5[0678]\d\d|6304|6390|67\d\d)\d{8,15}$", card_number) is None:
                raise forms.ValidationError('Please check the number on your card')
        return card_number

    def clean_expiry_date(self):
        """
        Expiry date validation
        :return: expiry date
        """
        expiry_date = self.cleaned_data['expiry_date']
        year = expiry_date[0]
        month = expiry_date[1]
        today_month = date.today().month
        today_year = date.today().year
        expiry_date_object = date(year, month, 1)
        today_date = date(today_year, today_month, 1)
        date_difference = expiry_date_object - today_date
        if date_difference.days < 0:
            raise forms.ValidationError('Check the expiry date or use a new card')

    def clean_cardholders_name(self):
        """
        Cardholder's name validation
        :return: string
        """
        cardholders_name = self.cleaned_data['cardholders_name']
        if len(cardholders_name) > 50:
            raise forms.ValidationError('Please enter 50 characters or less')

    def clean_card_security_code(self):
        """
        Card security code validation
        :return: string
        """
        card_security_code = str(self.cleaned_data['card_security_code'])
        if re.match("^[0-9]{3,4}$", card_security_code) is None:
            raise forms.ValidationError('The code should be 3 or 4 digits long')
