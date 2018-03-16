def full_stop_stripper(self):
    for key, value in self.fields.items():
        if value.error_messages['required']:
            if value.error_messages['required'] == 'This field is required.':
                value.error_messages['required'] = 'This field is required'
