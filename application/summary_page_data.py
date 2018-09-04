import collections

###


childcare_type_name_dict = collections.OrderedDict([('childcare_age_groups', 'What age groups will you be able to care for?'),
                                                    (
                                                    'overnight_care', 'Will you be looking after children overnight?')])

childcare_type_link_dict = collections.OrderedDict([('childcare_age_groups', 'Type-Of-Childcare-Age-Groups-View'),
                                                    ('overnight_care', 'Type-Of-Childcare-Overnight-Care-View')])

childcare_type_change_link_description_dict = collections.OrderedDict([('childcare_age_groups',
                                                                        'the age groups you could be caring for'),
                                                                       ('overnight_care',
                                                                        "if you'll be looking after children overnight")])

###

dbs_summary_dict = collections.OrderedDict({'data_names': ['dbs_certificate_number', 'cautions_convictions'],
                                            'display_names': ['DBS certificate number',
                                                              'Do you have any cautions or convictions?',],
                                            'back_url_names': ['DBS-Check-DBS-Details-View',
                                                               'DBS-Check-DBS-Details-View'],
                                            'table_names': [''],
                                            'table_error_names': [
                                                'There was a problem'],
                                            'page_title': 'Check your answers: criminal record checks'
                                            })

###

# Name dict contains the data_name of each table field and the actual name to be rendered


contact_info_name_dict = collections.OrderedDict([('email_address', 'Your email'),
                                                 ('mobile_number', 'Your mobile number'),
                                                 ('add_phone_number', 'Other phone number')])

# Link dict contains the data_name of each table field and the name of the change_link view to be reversed in template

contact_info_link_dict = collections.OrderedDict([('email_address', 'Contact-Email-View'),
                                                  ('mobile_number', 'Contact-Phone-View'),
                                                  ('add_phone_number', 'Contact-Phone-View')])

###

personal_details_name_dict = collections.OrderedDict([('name', 'Your name'),
                                                      ('date_of_birth', 'Your date of birth'),
                                                      ('home_address', 'Home address'),
                                                      ('childcare_location', 'Childcare location')])

personal_details_link_dict = collections.OrderedDict([('name', 'Personal-Details-Name-View'),
                                                      ('date_of_birth', 'Personal-Details-DOB-View'),
                                                      ('home_address', 'Personal-Details-Home-Address-Manual-View'),
                                                      ('childcare_location', 'Personal-Details-Location-Of-Care-View')])

###

first_aid_name_dict = collections.OrderedDict([('first_aid_training_organisation', 'Training organisation'),
                                               ('title_of_training_course', 'Title of training course'),
                                               ('course_date', 'Date you completed course'),
                                               ('renew_certificate',
                                                'Will you renew your certificate in the next few months?'),
                                               ('show_certificate',
                                                'Will you show a copy of your certificate to an inspector?')])

first_aid_link_dict = collections.OrderedDict([('first_aid_training_organisation', 'First-Aid-Training-Details-View'),
                                               ('title_of_training_course', 'First-Aid-Training-Details-View'),
                                               ('course_date', 'First-Aid-Training-Details-View'),
                                               ('renew_certificate', 'First-Aid-Training-Renew-View'),
                                               ('show_certificate', 'First-Aid-Training-Declaration-View')])

first_aid_change_link_description_dict = collections.OrderedDict([('course_date', 'course completion date')])

###

eyfs_name_dict = collections.OrderedDict([('eyfs_course_name', 'Title of training course'),
                                               ('eyfs_course_date', 'Date you completed course')])

eyfs_link_dict = collections.OrderedDict([('eyfs_course_name', 'Childcare-Training-Details-View'),
                                               ('eyfs_course_date', 'Childcare-Training-Details-View')])

eyfs_change_link_description_dict = collections.OrderedDict([('eyfs_course_name', 'course title'),
                                                             ('eyfs_course_date', 'course completion date')])

###

health_name_dict = collections.OrderedDict(
    [('health_submission_consent', 'Will you submit a health declaration booklet to Ofsted')])

health_link_dict = collections.OrderedDict([('health_submission_consent', 'Health-Booklet-View')])

###
other_adult_name_dict = collections.OrderedDict([('health_check_status', 'Health check status'),
                                                 ('full_name', 'Name'),
                                                ('date_of_birth', 'Date of birth'),
                                                ('relationship', 'Relationship'),
                                                ('email', 'Email address'),
                                                ('dbs_certificate_number', 'DBS certificate number'),
                                                ('permission', 'Permission for checks')])

other_adult_link_dict = collections.OrderedDict([('health_check_status', 'Other-People-Resend-Email-View'),
                                                ('full_name', 'Other-People-Adult-Details-View'),
                                                ('date_of_birth', 'Other-People-Adult-Details-View'),
                                                ('relationship', 'Other-People-Adult-Details-View'),
                                                ('email', 'Other-People-Adult-Details-View'),
                                                ('dbs_certificate_number', 'Other-People-Adult-DBS-View'),
                                                ('permission', 'Other-People-Adult-Permission-View')])

###

other_child_name_dict = collections.OrderedDict([('full_name', 'Name'),
                                                 ('date_of_birth', 'Date of birth'),
                                                 ('relationship', 'Relationship')])

other_child_link_dict = collections.OrderedDict([('full_name', 'Other-People-Children-Details-View'),
                                                 ('date_of_birth', 'Other-People-Children-Details-View'),
                                                 ('relationship', 'Other-People-Children-Details-View')])

# The below dictionaries are for the two tables at the top of the other people summary page

other_adult_summary_name_dict = collections.OrderedDict(
    [('adults_in_home', 'Do you live with anyone who is 16 or over?')])
other_adult_summary_link_dict = collections.OrderedDict([('adults_in_home', 'Other-People-Adult-Question-View')])

other_child_summary_name_dict = collections.OrderedDict([('children_in_home', 'Do you live with any children?')])
other_child_summary_link_dict = collections.OrderedDict([('children_in_home', 'Other-People-Children-Question-View')])

###

first_reference_name_dict = collections.OrderedDict([('full_name', 'Full name'),
                                                     ('relationship', 'How they know you'),
                                                     ('known_for', 'Known for'),
                                                     ('address', 'Address'),
                                                     ('phone_number', 'Phone number'),
                                                     ('email_address', 'Email address')])

first_reference_link_dict = collections.OrderedDict([('full_name', 'References-First-Reference-View'),
                                                     ('relationship', 'References-First-Reference-View'),
                                                     ('known_for', 'References-First-Reference-View'),
                                                     ('address', 'References-Enter-First-Reference-Address-View'),
                                                     (
                                                     'phone_number', 'References-First-Reference-Contact-Details-View'),
                                                     ('email_address',
                                                      'References-First-Reference-Contact-Details-View')])

second_reference_name_dict = collections.OrderedDict([('full_name', 'Full name'),
                                                      ('relationship', 'How they know you'),
                                                      ('known_for', 'Known for'),
                                                      ('address', 'Address'),
                                                      ('phone_number', 'Phone number'),
                                                      ('email_address', 'Email address')])
second_reference_link_dict = collections.OrderedDict([('full_name', 'References-Second-Reference-View'),
                                                      ('relationship', 'References-Second-Reference-View'),
                                                      ('known_for', 'References-Second-Reference-View'),
                                                      ('address', 'References-Enter-Second-Reference-Address-View'),
                                                      ('phone_number',
                                                       'References-Second-Reference-Contact-Details-View'),
                                                      ('email_address',
                                                       'References-Second-Reference-Contact-Details-View')])

###

# This dictionary contains the view to be reversed if the user clicks submit on the summary page ONLY if there are
# errors to be rectified

submit_link_dict = collections.OrderedDict([('login_details', 'Contact-Email-View'),
                                            ('type_of_childcare', 'Type-Of-Childcare-Guidance-View'),
                                            ('personal_details', 'Personal-Details-Guidance-View'),
                                            ('first_aid_training', 'First-Aid-Training-Guidance-View'),
                                            ('eyfs_training', 'Childcare-Training-Guidance-View'),
                                            ('criminal_record_check', 'DBS-Lived-Abroad-View'),
                                            ('health', 'Health-Intro-View'),
                                            ('references', 'References-Intro-View'),
                                            ('people_in_home', 'Other-People-Guidance-View')])

back_link_dict = collections.OrderedDict([('login_details', 'Question-View'),
                                          ('type_of_childcare', 'Type-Of-Childcare-Guidance-View'),
                                          ('personal_details', 'Personal-Details-Location-Of-Care-View'),
                                          ('first_aid_training', 'First-Aid-Training-Details-View'),
                                          ('eyfs_training', 'Childcare-Training-Details-View'),
                                          ('criminal_record_check', 'DBS-Check-DBS-Details-View'),
                                          ('health', 'Health-Booklet-View'),
                                          ('references', 'References-Second-Reference-Contact-Details-View'),
                                          ('people_in_home', 'Other-People-Children-Question-View')])
