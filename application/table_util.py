from .models import ArcComments


class Table:

    def get_errors(self):
        for row in self.row_list:
            if ArcComments.objects.filter(table_pk=self.table_pk, field_name=row.data_name).count() == 1:
                log = ArcComments.objects.get(table_pk=self.table_pk, field_name=row.data_name)
                try:
                    if log.flagged:
                        row.error = log.comment
                    else:
                        row.error = ''
                except:
                    pass

    def add_row(self, row):
        self.row_list.append(row)

    def get_row_list(self):
        return self.row_list

    def get_error_amount(self):
        error_count = 0
        for row in self.row_list:
            if row.error != '':
                error_count = error_count + 1
        return error_count

    def __init__(self, table_pk):
        self.row_list = []
        self.title = ''
        self.table_pk = table_pk


class Row:

    def __init__(self, data_name, row_name, value, back_link, error):

        self.data_name = data_name
        self.row_name = row_name
        self.value = value
        self.back_link = back_link
        self.error = error


def table_creator(object_list, field_names, data_names, table_names, table_error_names, back_url_names):

    data_list = []
    table_list = []
    for object in object_list:
        field_dict = field_mapper(object, data_names)
        for name in data_names:
            data_list.append(field_dict[name])
        row_data = zip(data_names,field_names, data_list, back_url_names)
        temp_table = Table(object.pk)
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