def full_stop_stripper(self):
    """
    Method to be passed to classes that will strip full stop from validation messages.
    :param self: Instance of class to be passed.
    :return: None.
    """
    for key, value in self.fields.items():
        if value.error_messages['required']:
            if value.error_messages['required'] == 'This field is required.':
                value.error_messages['required'] = 'This field is required'
