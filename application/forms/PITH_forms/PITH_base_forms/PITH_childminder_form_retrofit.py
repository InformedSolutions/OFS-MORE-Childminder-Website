from application.forms import ChildminderForms


class PITHChildminderFormAdapter(ChildminderForms):
    """
    - Childminder forms' methods require a field_list whose names correspond exactly to the field names in the database
      tables in order to work.
    - The PITHMultiRadioForm currently use fields whose names are the field_name + person_id, for example:
      'lived_abroad17aea132-7f9a-4cc1-b9d1-a92e69b9758c'.
    - This was done to determine which data contained in a POST request related to which adult.
    - These form names will not work with the existing Childminder forms.
    - This class acts as an Adapter class for PITH forms to use the Childminder forms functionality.
    """
    def check_flag(self):
        """
        Strip uuid from field_names, then call ChildminderForms check_flag() method, before returning field_list to
        previous state.
        :return: None
        """
        self.field_list = [field[:-36] for field in self.field_list]
        super(PITHChildminderFormAdapter, self).check_flag()
        self.field_list = [field + str(self.pk) for field in self.field_list]

    def remove_flag(self):
        """
        Strip uuid from field_names, then call ChildminderForms remove_flag() method, before returning field_list to
        previous state.
        :return: None
        """
        self.field_list = [field[:-36] for field in self.field_list]
        super(PITHChildminderFormAdapter, self).remove_flag()
        self.field_list = [field + str(self.pk) for field in self.field_list]

    def add_error(self, field, error):
        """
        Override built-in method to manipulate the field name, that way errors are added to Form by check_flag correctly
        """
        field += str(self.pk)
        return super(PITHChildminderFormAdapter, self).add_error(field, error)
