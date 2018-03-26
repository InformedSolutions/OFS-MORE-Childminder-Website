from django.urls import reverse

from .models import ArcComments, Application
from .summary_page_data import submit_link_dict, back_link_dict

class Table:
    """
    Table data structure use in generic summary template, this is used as a container for the list of rows with values
    """
    def get_errors(self):
        """
        Method to scan each row in a table for any occurrences in the ARC_COMMENTS table (i.e it has an error)
        :return: Does not need to return anything as it edits the rows in its row list
        """
        for row in self.row_list:
            for key in self.table_pk:
                if ArcComments.objects.filter(table_pk=key, field_name=row.data_name, flagged=True).count() == 1:
                    log = ArcComments.objects.get(table_pk=key, field_name=row.data_name)
                    try:
                        if log.flagged:
                            row.error = log.comment
                        else:
                            row.error = ''
                    except:
                        pass

    def add_row(self, row):
        """
        A method to add a row to a tables row list
        :param row: The new row object
        :return:
        """
        self.row_list.append(row)

    def get_row_list(self):
        """
        Standar get method for row list
        :return:
        """
        return self.row_list

    def get_error_amount(self):
        """
        Method to collect the amount of errors that have occurred in a table
        :return: Returns the amount of errors contained in thw rowlist
        """
        error_count = 0
        for row in self.row_list:
            if row.error != '':
                error_count = error_count + 1
        return error_count

    def __init__(self, table_pk):
        """
        Standard init for attributes used in other methods
        :param table_pk: The primary key of the database table from which the row list is made (this can be multiple)
        """
        self.row_list = []
        self.title = ''
        self.table_pk = table_pk


class Row:
    """
    Class to contain a specific row rendered in a table on the generic summary template
    """

    def __init__(self, data_name, row_name, value, back_link, error):
        """
        Standard init for all necessary fields
        :param data_name: The name of the field as stored in the database
        :param row_name: The name of the field as rendered on the template
        :param value: The value of the field
        :param back_link: The view which, when reversed, redirects to the page where the value is defined
        :param error: The error associated with the field, empty by default, only populated on table.get_errors
        """

        self.data_name = data_name
        self.row_name = row_name
        self.value = value
        self.back_link = back_link
        self.error = error


def table_creator(object_list, field_names, data_names, table_names, table_error_names, back_url_names):

    data_list = []
    table_list = []

    for object_table_list in object_list:
        for object in object_table_list:
            field_dict = field_mapper(object, data_names)
            for name in data_names:
                data_list.append(field_dict[name])
            row_data = zip(data_names,field_names, data_list, back_url_names)
            temp_table = Table([object.pk])
            for row in row_data:
                local_row = Row(row[0], row[1], row[2], row[3], '')
                temp_table.add_row(local_row)
        temp_table.get_errors()
        table_list.append(temp_table)
    table_to_title = zip(table_list, table_names, table_error_names)
    for table, name, error_name in table_to_title:
        table.title = name
        table.error_summary_title = error_name
    return table_list


def field_mapper(data_object, field_names, data_dictionary={}):
    for field in data_object._meta.get_fields():
        if field.name in field_names:
            data_dictionary[field.name] = getattr(data_object, field.name)
    return data_dictionary


def create_tables(tables_values, page_name_dict, page_link_dict):
    """
    Function to create a list of table objects
    :param tables_values: A list of dictionaries containing all the details of the  tables to be rendered on the page
    :param page_name_dict: The dictionary containing the data name for each of the fields linked to the name to be
    rendered on the page
    :param page_link_dict: The dictionary containing the data name for each of the fields linked to the change link
    where the data was defined
    :return: Returns the full list of table objects in a form that can be passed to the generic summary template
    """
    table_output_list = []
    for table in tables_values:

        # Each iteration of table will be a dictionary (see a call of this funciton for the definition of this)
        for key, value in table['fields'].items():
            # Create a row object as defined above, using the data name as the key
            temp_row = Row(key, page_name_dict[key], value, page_link_dict[key], '')
            # The actual table object is passed into the function without rows, the row is added here
            table['table_object'].add_row(temp_row)

        # Once all rows have been addded to the object, get errors can be called, getting any errors for all of the rows
        table['table_object'].get_errors()
        table['table_object'].title = table['title']
        table['table_object'].error_summary_title = table['error_summary_title']
        # An extra part to the back links must be added for the other people pages, if this detail is passed, its added
        if 'other_people_numbers' in table.keys():
            table['table_object'].other_people_numbers = table['other_people_numbers']
        table_output_list.append(table['table_object'])
    return table_output_list


def submit_link_setter(variables, table_list, section_name, application_id):
    application = Application.objects.get(application_id=application_id)
    for table in table_list:
        if table.get_error_amount() != 0:
            variables['submit_link'] = reverse(submit_link_dict[section_name])
        else:
            #Go to task list
            variables['submit_link'] = reverse('morebeta')
        #If section status is completed and not in arc review, we should go back to the previous question in section
        if application.application_status != 'FURTHER_INFORMATION':
            variables['back_link'] = back_link_dict[section_name]
        # Otherwise, return to the task list
        else:
            variables['back_link'] = 'morebeta'
    return variables
