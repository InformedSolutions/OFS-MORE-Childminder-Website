"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- business_logic.py --

@author: Informed Solutions
"""

import re
import enum
from datetime import datetime, timedelta

import pytz

from .models import (AdultInHome,
                     ApplicantHomeAddress,
                     ApplicantName,
                     ApplicantPersonalDetails,
                     Application,
                     ChildcareType,
                     ChildInHome,
                     CriminalRecordCheck,
                     ChildcareTraining,
                     FirstAidTraining,
                     HealthDeclarationBooklet,
                     Reference,
                     UserDetails, Child, ChildAddress)
from .utils import unique_values, get_first_duplicate_index, get_duplicate_list_entry_indexes
from . import dbs


def childcare_type_logic(application_id_local, form):
    """
    Business logic to create or update a Childcare_Type record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a ChildcareType object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    zero_to_five_status = '0-5' in form.cleaned_data.get('type_of_childcare')
    five_to_eight_status = '5-8' in form.cleaned_data.get('type_of_childcare')
    eight_plus_status = '8over' in form.cleaned_data.get('type_of_childcare')
    # If the user entered information for this task for the first time
    if ChildcareType.objects.filter(application_id=application_id_local).count() == 0:
        childcare_type_record = ChildcareType(zero_to_five=zero_to_five_status, five_to_eight=five_to_eight_status,
                                              eight_plus=eight_plus_status, application_id=this_application)
    # If the user previously entered information for this task
    elif ChildcareType.objects.filter(application_id=application_id_local).count() > 0:
        childcare_type_record = ChildcareType.objects.get(application_id=application_id_local)
        childcare_type_record.zero_to_five = zero_to_five_status
        childcare_type_record.five_to_eight = five_to_eight_status
        childcare_type_record.eight_plus = eight_plus_status
    return childcare_type_record


def childcare_register_type(application_id):
    """
    Function to determine the childcare register to which the applicant is applying.
    :param application_id: app_id of the applicant for which the check is being made.
    :return: a string containing the register to which the applicant is applying.
    """
    childcare_type_record = ChildcareType.objects.get(application_id=application_id)
    if not childcare_type_record.zero_to_five:
        return 'childcare_register_only'
    else:
        return 'early_years_register'


def login_contact_logic(application_id_local, form):
    """
    Business logic to create or update a User_Details record with e-mail address details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a UserDetails object to be saved
    """
    this_application = UserDetails.objects.get(application_id=application_id_local)
    email_address = form.cleaned_data.get('email_address')
    login_and_contact_details_record = this_application
    login_and_contact_details_record.email = email_address
    return login_and_contact_details_record


def login_contact_logic_mobile_phone(application_id_local, form):
    """
    Business logic to create or update a User_Details record with mobile phone number details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a UserDetails object to be saved
    """
    this_application = UserDetails.objects.get(application_id=application_id_local)
    mobile_number = form.cleaned_data.get('mobile_number')
    this_application.mobile_number = mobile_number
    return this_application


def login_contact_logic_add_phone(application_id_local, form):
    """
    Business logic to create or update a User_Details record with additional phone number details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a UserDetails object to be saved
    """
    this_application = UserDetails.objects.get(application_id=application_id_local)
    add_phone_number = form.cleaned_data.get('add_phone_number')
    this_application.add_phone_number = add_phone_number
    return this_application


def personal_name_logic(app_id, form):
    """
    Business logic to create or update an Applicant_Name record with name details

    :param app_id: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an ApplicantName object to be saved
    """
    app_obj = Application.objects.get(pk=app_id.pk)
    first_name = form.cleaned_data.get('first_name')
    middle_names = form.cleaned_data.get('middle_names')
    last_name = form.cleaned_data.get('last_name')

    # If the user entered information for this task for the first time
    if not ApplicantPersonalDetails.objects.filter(application_id=app_id).exists():

        # Create an empty ApplicantPersonalDetails object to generate a p_id
        personal_details_record = ApplicantPersonalDetails(
            birth_day=None,
            birth_month=None,
            birth_year=None,
            application_id=app_obj
        )

        personal_details_record.save()

        p_id = ApplicantPersonalDetails.objects.get(application_id=app_id)

        applicant_names_record = ApplicantName(
            application_id=app_obj,
            current_name='True',
            first_name=first_name,
            middle_names=middle_names,
            last_name=last_name,
            personal_detail_id=p_id
        )

    # If the user previously entered information for this task
    elif ApplicantPersonalDetails.objects.filter(application_id=app_id).exists():

        # Retrieve the personal_details_id corresponding to the application
        p_id = ApplicantPersonalDetails.objects.get(application_id=app_id).personal_detail_id

        applicant_names_record = ApplicantName.objects.get(personal_detail_id=p_id)
        applicant_names_record.application_id = app_obj
        applicant_names_record.first_name = first_name
        applicant_names_record.middle_names = middle_names
        applicant_names_record.last_name = last_name

    return applicant_names_record


def personal_dob_logic(application_id_local, form):
    """
    Business logic to create or update an Applicant_Personal_Details record with name details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an ApplicantPersonalDetails object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    birth_day = form.cleaned_data.get('date_of_birth')[0]
    birth_month = form.cleaned_data.get('date_of_birth')[1]
    birth_year = form.cleaned_data.get('date_of_birth')[2]
    # If the user entered information for this task for the first time
    if ApplicantPersonalDetails.objects.filter(application_id=application_id_local).count() == 0:
        personal_details_record = ApplicantPersonalDetails(birth_day=birth_day, birth_month=birth_month,
                                                           birth_year=birth_year, application_id=this_application)
        personal_details_record.save()
    # If the user previously entered information for this task
    elif ApplicantPersonalDetails.objects.filter(application_id=application_id_local).count() > 0:
        personal_details_record = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
        personal_details_record.birth_day = birth_day
        personal_details_record.birth_month = birth_month
        personal_details_record.birth_year = birth_year
    return personal_details_record


def personal_home_address_logic(app_id, form):
    """
    Business logic to create or update an Applicant_Home_Address record with home address details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an ApplicantHomeAddress object to be saved
    """

    app_obj = Application.objects.get(application_id=app_id)
    street_line1 = form.cleaned_data.get('street_line1')
    street_line2 = form.cleaned_data.get('street_line2')
    town = form.cleaned_data.get('town')
    county = form.cleaned_data.get('county')
    postcode = form.cleaned_data.get('postcode')
    personal_detail_record = ApplicantPersonalDetails.objects.get(application_id=app_obj)
    personal_detail_id = personal_detail_record.personal_detail_id

    # If the user entered information for this task for the first time
    if not ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id).exists():

        home_address_record = ApplicantHomeAddress(
            street_line1=street_line1,
            street_line2=street_line2,
            town=town,
            county=county,
            country='United Kingdom',
            postcode=postcode,
            childcare_address=None,
            current_address=True,
            move_in_month=0,
            move_in_year=0,
            personal_detail_id=personal_detail_record,
            application_id=app_obj
        )
        home_address_record.save()

    # If the user previously entered information for this task
    elif ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, current_address=True).exists():

        home_address_record = ApplicantHomeAddress.objects.get(
            personal_detail_id=personal_detail_id,
            current_address=True
        )
        home_address_record.street_line1 = street_line1
        home_address_record.street_line2 = street_line2
        home_address_record.town = town
        home_address_record.county = county
        home_address_record.postcode = postcode

    return home_address_record


def child_address_logic(app_id, child, form):
    """
    Business logic to create or update a child address record with address details
    :param app_id: A string object containing the current application ID
    :param child: A numerical identifier for the child
    :param form: A form object containing the data to be stored
    :return: an ChildAddress object to be saved
    """
    application = Application.objects.get(application_id=app_id)
    child_address = ChildAddress(application_id=application)

    if ChildAddress.objects.filter(application_id=app_id, child=child).exists():
        child_address = ChildAddress.objects.get(application_id=app_id, child=child)

    child_address.child = int(child)
    child_address.street_line1 = form.cleaned_data.get('street_line1')
    child_address.street_line2 = form.cleaned_data.get('street_line2')
    child_address.town = form.cleaned_data.get('town')
    child_address.county = form.cleaned_data.get('county')
    child_address.postcode = form.cleaned_data.get('postcode')

    return child_address


def personal_location_of_care_logic(application_id_local, form):
    """
    Business logic to update an Applicant_Home_Address record with home address details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an ApplicantHomeAddress object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    location_of_care = form.cleaned_data.get('childcare_location')
    # Retrieve the personal_details_id corresponding to the application
    personal_detail_record = ApplicantPersonalDetails.objects.get(application_id=this_application)
    personal_detail_id = personal_detail_record.personal_detail_id
    home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id, current_address=True)
    home_address_record.childcare_address = location_of_care
    return home_address_record


def multiple_childcare_address_logic(personal_detail_id):
    """
    Business logic to remove a duplicate childcare address if it is marked as the same as the home address
    :param personal_detail_id: A string object containing the personal detail ID corresponding to the
    current application ID
    """
    # If there are multiple addresses marked as the childcare address
    if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, childcare_address=True).count() > 1:
        # If the home address is marked as a childcare address
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, childcare_address=True,
                                               current_address=True).count() > 0:
            # If a non-home address is also marked as a childcare address
            if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, childcare_address=True,
                                                   current_address=False).count() > 0:
                childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                            childcare_address=True,
                                                                            current_address=False)
                childcare_address_record.delete()


def personal_childcare_address_logic(application_id_local, form):
    """
    Business logic to create or update an Applicant_Home_Address record with childcare address details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an ApplicantHomeAddress object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    street_line1 = form.cleaned_data.get('street_line1')
    street_line2 = form.cleaned_data.get('street_line2')
    town = form.cleaned_data.get('town')
    county = form.cleaned_data.get('county')
    postcode = form.cleaned_data.get('postcode')
    # Retrieve the personal_details_id corresponding to the application
    personal_detail_record = ApplicantPersonalDetails.objects.get(application_id=this_application)
    personal_detail_id = personal_detail_record.personal_detail_id
    # If the user entered information for this task for the first time
    if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                           childcare_address='True').count() == 0:
        childcare_address_record = ApplicantHomeAddress(street_line1=street_line1, street_line2=street_line2, town=town,
                                                        county=county, country='United Kingdom', postcode=postcode,
                                                        childcare_address=True, current_address=False, move_in_month=0,
                                                        move_in_year=0, personal_detail_id=personal_detail_record,
                                                        application_id=application_id_local)
        childcare_address_record.save()
    # If the user previously entered information for this task
    elif ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                             childcare_address='True').count() > 0:
        childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                    childcare_address=True)
        childcare_address_record.street_line1 = street_line1
        childcare_address_record.street_line2 = street_line2
        childcare_address_record.town = town
        childcare_address_record.county = county
        childcare_address_record.postcode = postcode
        childcare_address_record.current_address = False
    return childcare_address_record


def first_aid_logic(application_id_local, form):
    """
    Business logic to create or update a First_Aid_Training record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an FirstAidTraining object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    training_organisation = form.cleaned_data.get('first_aid_training_organisation')
    course_title = form.cleaned_data.get('title_of_training_course')
    course_day = form.cleaned_data.get('course_date')[0]
    course_month = form.cleaned_data.get('course_date')[1]
    course_year = form.cleaned_data.get('course_date')[2]
    # If the user entered information for this task for the first time
    if FirstAidTraining.objects.filter(application_id=application_id_local).count() == 0:
        first_aid_training_record = FirstAidTraining(training_organisation=training_organisation,
                                                     course_title=course_title, course_day=course_day,
                                                     course_month=course_month, course_year=course_year,
                                                     application_id=this_application)
    # If the user previously entered information for this task
    elif FirstAidTraining.objects.filter(application_id=application_id_local).count() > 0:
        first_aid_training_record = FirstAidTraining.objects.get(application_id=application_id_local)
        first_aid_training_record.training_organisation = training_organisation
        first_aid_training_record.course_title = course_title
        first_aid_training_record.course_day = course_day
        first_aid_training_record.course_month = course_month
        first_aid_training_record.course_year = course_year
    return first_aid_training_record


def eyfs_details_logic(application_id_local, form):
    """
    Business logic to create or update an EYFS record for someone applying to the Early Years register.
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an EYFS object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    eyfs_course_name = form.cleaned_data.get('eyfs_course_name')
    eyfs_course_date_day = form.cleaned_data.get('eyfs_course_date').day
    eyfs_course_date_month = form.cleaned_data.get('eyfs_course_date').month
    eyfs_course_date_year = form.cleaned_data.get('eyfs_course_date').year
    # If the user entered information for this task for the first time
    if ChildcareTraining.objects.filter(application_id=application_id_local).count() == 0:
        eyfs_record = ChildcareTraining(eyfs_course_name=eyfs_course_name, eyfs_course_date_day=eyfs_course_date_day,
                                        eyfs_course_date_month=eyfs_course_date_month,
                                        eyfs_course_date_year=eyfs_course_date_year, application_id=this_application)
    # If the user previously entered information for this task
    elif ChildcareTraining.objects.filter(application_id=application_id_local).count() > 0:
        eyfs_record = ChildcareTraining.objects.get(application_id=application_id_local)
        eyfs_record.eyfs_course_name = eyfs_course_name
        eyfs_record.eyfs_course_date_day = eyfs_course_date_day
        eyfs_record.eyfs_course_date_month = eyfs_course_date_month
        eyfs_record.eyfs_course_date_year = eyfs_course_date_year
    return eyfs_record


def training_for_childcare_register_logic(application_id_local, form):
    """
    Business logic to create or update an EYFS record for someone applying to the childcare register only.
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an EYFS object to be saved
    """
    childcare_training = form.cleaned_data['childcare_training']

    options = (
        'eyfs_training',
        'common_core_training',
        'no_training',
    )

    if ChildcareTraining.objects.filter(application_id=application_id_local).count() == 0:
        application_record = Application.objects.get(application_id=application_id_local)
        childcare_training_record = ChildcareTraining.objects.create(application_id=application_record)
    else:
        childcare_training_record = ChildcareTraining.objects.get(application_id=application_id_local)

    for option in options:
        if option in childcare_training:
            setattr(childcare_training_record, option, True)
        else:
            setattr(childcare_training_record, option, False)

    return childcare_training_record


def childcare_training_course_logic(application_id_local, form):
    """

    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a call to the function required to update the model with the information provided.
    """
    childcare_type = childcare_register_type(application_id_local)
    if childcare_type == 'childcare_register_only':
        return training_for_childcare_register_logic(application_id_local, form)
    else:
        return eyfs_details_logic(application_id_local, form)


def dbs_check_logic(application_id_local, form):
    """
    Business logic to create or update a Criminal_Record_Check record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an CriminalRecordCheck object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    dbs_certificate_number = form.cleaned_data.get('dbs_certificate_number')
    cautions_convictions = form.cleaned_data.get('cautions_convictions')
    # If the user entered information for this task for the first time
    if CriminalRecordCheck.objects.filter(application_id=application_id_local).count() == 0:
        dbs_record = CriminalRecordCheck(dbs_certificate_number=dbs_certificate_number,
                                         cautions_convictions=cautions_convictions, application_id=this_application)
    # If the user previously entered information for this task
    elif CriminalRecordCheck.objects.filter(application_id=application_id_local).count() > 0:
        dbs_record = CriminalRecordCheck.objects.get(application_id=application_id_local)
        dbs_record.dbs_certificate_number = dbs_certificate_number
        dbs_record.cautions_convictions = cautions_convictions
    return dbs_record


def references_first_reference_logic(application_id_local, form):
    """
    Business logic to create or update a Reference record with first reference details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an Reference object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    last_name = form.cleaned_data.get('last_name')
    relationship = form.cleaned_data.get('relationship')
    years_known = form.cleaned_data.get('time_known')[0]
    months_known = form.cleaned_data.get('time_known')[1]
    # If the user entered information for this task for the first time
    if Reference.objects.filter(application_id=application_id_local, reference=1).count() == 0:
        reference_record = Reference(reference=1,
                                     first_name=first_name,
                                     last_name=last_name,
                                     relationship=relationship,
                                     years_known=years_known,
                                     months_known=months_known,
                                     street_line1='',
                                     street_line2='',
                                     town='',
                                     county='',
                                     country='',
                                     postcode='',
                                     phone_number='',
                                     email='',
                                     application_id=this_application)
    # If the user previously entered information for this task
    elif Reference.objects.filter(application_id=application_id_local, reference=1).count() > 0:
        reference_record = Reference.objects.get(application_id=application_id_local, reference=1)
        reference_record.first_name = first_name
        reference_record.last_name = last_name
        reference_record.relationship = relationship
        reference_record.years_known = years_known
        reference_record.months_known = months_known
    return reference_record


def references_second_reference_logic(application_id_local, form):
    """
    Business logic to create or update a Reference record with first reference details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an Reference object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    last_name = form.cleaned_data.get('last_name')
    relationship = form.cleaned_data.get('relationship')
    years_known = form.cleaned_data.get('time_known')[0]
    months_known = form.cleaned_data.get('time_known')[1]
    # If the user entered information for this task for the first time
    if Reference.objects.filter(application_id=application_id_local, reference=2).count() == 0:
        reference_record = Reference(reference=2,
                                     first_name=first_name,
                                     last_name=last_name,
                                     relationship=relationship,
                                     years_known=years_known,
                                     months_known=months_known,
                                     street_line1='',
                                     street_line2='',
                                     town='',
                                     county='',
                                     country='',
                                     postcode='',
                                     phone_number='',
                                     email='',
                                     application_id=this_application)
    # If the user previously entered information for this task
    elif Reference.objects.filter(application_id=application_id_local, reference=2).count() > 0:
        reference_record = Reference.objects.get(application_id=application_id_local, reference=2)
        reference_record.first_name = first_name
        reference_record.last_name = last_name
        reference_record.relationship = relationship
        reference_record.years_known = years_known
        reference_record.months_known = months_known
    return reference_record


def health_check_logic(application_id_local, form):
    """
    Business logic to create or update a HealthDeclarationBooklet record with first reference details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: an HealthDeclarationBooklet object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    send_hdb_declare = True
    # If the user entered information for this task for the first time
    if HealthDeclarationBooklet.objects.filter(application_id=application_id_local).count() == 0:
        hdb_record = HealthDeclarationBooklet(send_hdb_declare=send_hdb_declare, application_id=this_application)
    # If the user previously entered information for this task
    elif HealthDeclarationBooklet.objects.filter(application_id=application_id_local).count() > 0:
        hdb_record = HealthDeclarationBooklet.objects.get(application_id=application_id_local)
        hdb_record.send_hdb_declare = send_hdb_declare
    return hdb_record


def your_children_details_logic(application_id_local, form, child):
    """
    Business logic to create or update an ChildInHome record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :param child: child number (integer)
    :return: an ChildInHome object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    middle_names = form.cleaned_data.get('middle_names')
    last_name = form.cleaned_data.get('last_name')
    birth_day = form.cleaned_data.get('date_of_birth')[0]
    birth_month = form.cleaned_data.get('date_of_birth')[1]
    birth_year = form.cleaned_data.get('date_of_birth')[2]
    # If the user entered information for this task for the first time
    if Child.objects.filter(application_id=this_application, child=child).exists():

        child_record = Child.objects.get(application_id=this_application, child=child)
        child_record.first_name = first_name
        child_record.middle_names = middle_names
        child_record.last_name = last_name
        child_record.birth_day = birth_day
        child_record.birth_month = birth_month
        child_record.birth_year = birth_year


    # If the user previously entered information for this task
    else:
        child_record = Child(first_name=first_name, middle_names=middle_names, last_name=last_name,
                             birth_day=birth_day, birth_month=birth_month, birth_year=birth_year,
                             application_id=this_application, child=child)

    return child_record


def other_people_adult_details_logic(application_id_local, form, adult):
    """
    Business logic to create or update an AdultInHome record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :param adult: adult number (integer)
    :return: an AdultInHome object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    middle_names = form.cleaned_data.get('middle_names')
    last_name = form.cleaned_data.get('last_name')
    birth_day = form.cleaned_data.get('date_of_birth')[0]
    birth_month = form.cleaned_data.get('date_of_birth')[1]
    birth_year = form.cleaned_data.get('date_of_birth')[2]
    relationship = form.cleaned_data.get('relationship')
    email = form.cleaned_data.get('email_address')
    # If the user entered information for this task for the first time
    if AdultInHome.objects.filter(application_id=this_application, adult=adult).exists():

        adult_record = AdultInHome.objects.get(application_id=this_application, adult=adult)
        if adult_record.email != email:
            adult_record.email_resent_timestamp = None
        adult_record.first_name = first_name
        adult_record.middle_names = middle_names
        adult_record.last_name = last_name
        adult_record.birth_day = birth_day
        adult_record.birth_month = birth_month
        adult_record.birth_year = birth_year
        adult_record.relationship = relationship
        adult_record.email = email
        adult_record.email_resent = 0


    # If the user previously entered information for this task
    else:
        adult_record = AdultInHome(first_name=first_name, middle_names=middle_names, last_name=last_name,
                                   birth_day=birth_day, birth_month=birth_month, birth_year=birth_year,
                                   relationship=relationship, email=email, application_id=this_application, adult=adult,
                                   email_resent=0)

    return adult_record


def remove_adult(application_id_local, remove_person):
    """
    Method to remove an adult from the database
    :param application_id_local: current application ID
    :param remove_person: adult to remove (integer)
    :return:
    """
    application = Application.objects.get(pk=application_id_local)

    if AdultInHome.objects.filter(application_id=application_id_local, adult=remove_person).exists() is True:
        AdultInHome.objects.get(application_id=application_id_local, adult=remove_person).delete()
        # Reset task status to WAITING if adults are updated
        if application.people_in_home_status == 'WAITING':
            application.people_in_home_status == 'IN_PROGRESS'
            application.save()


def rearrange_adults(number_of_adults, application_id_local):
    """
    Method to rearrange numbers assigned to adults
    :param number_of_adults: number of adults in database (integer)
    :param application_id_local: current application ID
    :return:
    """
    application = Application.objects.get(pk=application_id_local)

    for i in range(1, number_of_adults + 1):
        # If there is a gap in the sequence of adult numbers
        if AdultInHome.objects.filter(application_id=application_id_local, adult=i).count() == 0:
            next_adult = i + 1
            # If there is an adult that has the next number in the sequence, assign the missing number
            if AdultInHome.objects.filter(application_id=application_id_local, adult=next_adult).count() != 0:
                next_adult_record = AdultInHome.objects.get(application_id=application_id_local, adult=next_adult)
                next_adult_record.adult = i
                next_adult_record.save()
                # Reset task status to WAITING if adults are updated
                if application.people_in_home_status == 'WAITING':
                    application.people_in_home_status = 'IN_PROGRESS'
                    application.save()


def remove_child(application_id_local, remove_person):
    """
    Method to remove a child from the database
    :param application_id_local: current application ID
    :param remove_person: child to remove (integer)
    """
    if Child.objects.filter(application_id=application_id_local, child=remove_person).exists() is True:
        Child.objects.get(application_id=application_id_local, child=remove_person).delete()


def rearrange_children(number_of_children, application_id_local):
    """
    Method to rearrange numbers assigned to children
    :param number_of_children: number of children in database (integer)
    :param application_id_local: current application ID
    """
    children_records = Child.objects.filter(application_id=application_id_local).order_by('child')

    for index, child_record in enumerate(children_records):
        child_record.child = index + 1
        child_record.save()


def remove_child_in_home(application_id_local, remove_person):
    """
    Method to remove a child in home from the database
    :param application_id_local: current application ID
    :param remove_person: child to remove (integer)
    :return:
    """
    if ChildInHome.objects.filter(application_id=application_id_local, child=remove_person).exists() is True:
        ChildInHome.objects.get(application_id=application_id_local, child=remove_person).delete()


def rearrange_children_in_home(number_of_children, application_id_local):
    """
    Method to rearrange numbers assigned to adults
    :param number_of_children: number of children in database (integer)
    :param application_id_local: current application ID
    :return:
    """
    for i in range(1, number_of_children + 1):
        # If there is a gap in the sequence of child numbers
        if ChildInHome.objects.filter(application_id=application_id_local, child=i).count() == 0:
            next_child = i + 1
            # If there is a child that has the next number in the sequence, assign the missing number
            if ChildInHome.objects.filter(application_id=application_id_local, child=next_child).count() != 0:
                next_child_record = ChildInHome.objects.get(application_id=application_id_local, child=next_child)
                next_child_record.child = i
                next_child_record.save()


def other_people_children_details_logic(application_id_local, form, child):
    """
    Business logic to create or update an ChildInHome record
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :param child: child number (integer)
    :return: an ChildInHome object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    middle_names = form.cleaned_data.get('middle_names')
    last_name = form.cleaned_data.get('last_name')
    birth_day = form.cleaned_data.get('date_of_birth')[0]
    birth_month = form.cleaned_data.get('date_of_birth')[1]
    birth_year = form.cleaned_data.get('date_of_birth')[2]
    relationship = form.cleaned_data.get('relationship')
    # If the user entered information for this task for the first time
    if ChildInHome.objects.filter(application_id=this_application, child=child).count() == 0:
        child_record = ChildInHome(first_name=first_name, middle_names=middle_names, last_name=last_name,
                                   birth_day=birth_day, birth_month=birth_month, birth_year=birth_year,
                                   relationship=relationship, application_id=this_application, child=child)
    # If the user previously entered information for this task
    elif ChildInHome.objects.filter(application_id=this_application, child=child).count() > 0:
        child_record = ChildInHome.objects.get(application_id=this_application, child=child)
        child_record.first_name = first_name
        child_record.middle_names = middle_names
        child_record.last_name = last_name
        child_record.birth_day = birth_day
        child_record.birth_month = birth_month
        child_record.birth_year = birth_year
        child_record.relationship = relationship
    return child_record


def PITH_own_children_details_logic(application_id_local, form, child):
    """
    A subset mirror function of the above 'other_people_children_details_logic' function.
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :param child: child number (integer)
    :return: an ChildInHome object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    first_name = form.cleaned_data.get('first_name')
    middle_names = form.cleaned_data.get('middle_names')
    last_name = form.cleaned_data.get('last_name')
    birth_day = form.cleaned_data.get('date_of_birth')[0]
    birth_month = form.cleaned_data.get('date_of_birth')[1]
    birth_year = form.cleaned_data.get('date_of_birth')[2]

    if middle_names is None:
        middle_names = ""

    # If the user entered information for this task for the first time
    if Child.objects.filter(application_id=this_application, child=child).count() == 0:
        child_record = Child(first_name=first_name,
                             middle_names=middle_names,
                             last_name=last_name,
                             birth_day=birth_day,
                             birth_month=birth_month,
                             birth_year=birth_year,
                             application_id=this_application,
                             lives_with_childminder=False,
                             child=child)
    # If the user previously entered information for this task
    elif Child.objects.filter(application_id=this_application, child=child).count() > 0:
        child_record = Child.objects.get(application_id=this_application,
                                         child=child)
        child_record.first_name = first_name
        child_record.middle_names = middle_names
        child_record.last_name = last_name
        child_record.birth_day = birth_day
        child_record.birth_month = birth_month
        child_record.birth_year = birth_year
    return child_record


def get_card_expiry_years():
    """
    Business logic to calculate the card expiry date
    :return: A list of years when the card expires
    """
    year_list = []
    # Iterates 0 through 10, affixing each value to current year and appending to year list
    for year_iterable in range(0, 11):
        now = datetime.datetime.now()
        year_list.append((now.year + year_iterable, (str(now.year + year_iterable))))
    return year_list


def login_contact_security_question(application_id_local, form):
    """
    Business logic to create or update a User_Details record with phone number details
    :param application_id_local: A string object containing the current application ID
    :param form: A form object containing the data to be stored
    :return: a UserDetails object to be saved
    """
    this_application = Application.objects.get(application_id=application_id_local)
    security_answer = form.cleaned_data.get('security_answer')
    login_and_contact_details_record = this_application.login_id
    login_and_contact_details_record.security_answer = security_answer
    return login_and_contact_details_record


def reset_declaration(application):
    """
    Method to reset the declaration status to To Do if a task is updated
    :param application: current application
    """
    if application.declarations_status == 'COMPLETED':
        application.declarations_status = 'NOT_STARTED'
        application.share_info_declare = None
        application.display_contact_details_on_web = None
        application.suitable_declare = None
        application.information_correct_declare = None
        application.change_declare = None
        application.save()

    if application.application_status == 'FURTHER_INFORMATION':
        application.declarations_status = 'NOT_STARTED'
        application.share_info_declare = None
        application.display_contact_details_on_web = None
        application.suitable_declare = None
        application.information_correct_declare = None
        application.change_declare = None
        application.save()


def health_check_email_resend_logic(adult_record):
    """
    Method to verify if the last household member health check email should not be sent, given a limit of 3 resends per 24
    hours.
    :param: adult_record: An AdultInHome object
    :return: Boolean: True if email cannot be sent, False if email can be sent.
    """

    # If email_resent_timestamp is None then the email has never been resent.
    if adult_record.email_resent_timestamp is not None:

        # If the last e-mail was sent within the last 24 hours
        if (datetime.now(pytz.utc) - adult_record.email_resent_timestamp) < timedelta(1):

            # If the e-mail has been resent less than 3 times
            if adult_record.email_resent < 3:

                return False

            # If the email has been resent more than or equal to 3 times
            elif adult_record.email_resent >= 3:

                return True

        # If the last e-mail to the household member has been sent more than 24 hours ago
        elif (datetime.now(pytz.utc) - adult_record.email_resent_timestamp) > timedelta(1):
            # Reset the email resent count
            adult_record.email_resent = 0
            adult_record.save()

            return False
    else:
        return False


def dbs_matches_childminder_dbs(application, candidate_dbs_certificate_number):
    """
    Helper function to determine whether a DBS number matches the DBS recorded for the childminder
    :param application: the application to be checked against
    :param candidate_dbs_certificate_number: the candidate dbs number to be tested against
    :return: object detailing whether the dbs numbers contained in an application are unique.
    """
    try:
        childminder_dbs_record = CriminalRecordCheck.objects.get(application_id=application.application_id)
        return candidate_dbs_certificate_number == childminder_dbs_record.dbs_certificate_number
    except CriminalRecordCheck.DoesNotExist:
        return False


def household_member_dbs_form_duplicates_check(other_people_dbs_form_data):
    """
    Helper method to check for any duplicate DBS entries in the other people DBS form
    :param other_people_dbs_form_data: POSTed form data including the candidate DBS numbers to be recorded
    :return: an object articulating any duplicate matches identified
    """
    response = UniqueDbsCheckResult()

    dbs_numbers = list()

    # Note the POSTed form must be sorted as when sat behind a load-balancer
    # requests forwarded to an upstream may contain a body that has an altered ordering
    for key in sorted(other_people_dbs_form_data):
        if "dbs_certificate_number" in key:
            dbs_numbers.append(other_people_dbs_form_data[key])

    if unique_values(dbs_numbers):
        return response
    else:
        response.dbs_numbers_unique = False
        response.duplicates_household_member_dbs = True

        # Note that values in the list are incremented by 1 here given the positional
        # arguments of household members in a form start at 1 rather
        # than 0 (i.e. as they would in a natural python list)
        incremented_list = [x + 1 for x in get_duplicate_list_entry_indexes(dbs_numbers)]
        response.duplicate_entry_indexes = incremented_list
        return response


def get_duplicate_household_member_dbs_indexes(other_people_dbs_form_data):
    dbs_numbers = list()

    for key in other_people_dbs_form_data:
        if "dbs_certificate_number" in key:
            dbs_numbers.append(other_people_dbs_form_data[key])

    duplicate_entry = get_first_duplicate_index(dbs_numbers)
    duplicate_indexes = get_duplicate_list_entry_indexes(dbs_numbers, duplicate_entry)

    response = UniqueDbsCheckResult()
    response.duplicates_household_member_dbs = True
    response.duplicate_entry_indexes = duplicate_indexes
    return response


def childminder_dbs_duplicates_household_member_check(application, candidate_dbs_certificate_number, adult_record=None):
    """
    Helper method to check whether a childminder DBS number duplicates an existing household member's
    :param candidate_dbs_certificate_number: the candidate DBS number to be assigned
    :return: True/False result
    """
    adults = AdultInHome.objects.filter(application_id=application.application_id)
    if adult_record:
        adults_dbs_list = [adult.dbs_certificate_number for adult in adults if not adult.pk == adult_record.pk]
    else:
        adults_dbs_list = [adult.dbs_certificate_number for adult in adults]
    return candidate_dbs_certificate_number in adults_dbs_list


def get_duplicate_dbs_index(application, candidate_dbs_certificate_number):
    """
    Helper method for gathering the duplicate index
    :param application: the application to be tested against
    :param candidate_dbs_certificate_number: the candidate DBS number to be assigned
    :return: an integer which states the position of the erroneous DBS number
    """
    dbs_numbers = list()

    try:
        childminder_dbs_record = CriminalRecordCheck.objects.get(application_id=application.application_id)
        dbs_numbers.append(childminder_dbs_record.dbs_certificate_number)
    except CriminalRecordCheck.DoesNotExist:
        dbs_numbers.append('')

    # Check how many additional adults feature in application form
    additional_adults = AdultInHome.objects.filter(application_id=application.application_id)
    count_of_additional_adults_in_home = AdultInHome.objects.filter(application_id=application.application_id).count()

    # Iterate and push DBS numbers to comparison array
    if count_of_additional_adults_in_home > 0:
        for i in range(1, int(additional_adults.count()) + 1):
            adult = AdultInHome.objects.get(
                application_id=application.application_id, adult=i)
            # filter out any empty values so as not to get a false match on duplicate index
            if adult.dbs_certificate_number:
                dbs_numbers.append(adult.dbs_certificate_number)

    dbs_numbers.append(candidate_dbs_certificate_number)

    return get_first_duplicate_index(dbs_numbers)


class DBSStatus(enum.Enum):

    OK = 0
    DOB_MISMATCH = 1
    NEED_ASK_IF_CAPITA = 2
    NEED_ASK_IF_ON_UPDATE = 3
    NEED_APPLY_FOR_NEW = 4
    NEED_UPDATE_SERVICE_SIGN_UP = 5
    NEED_UPDATE_SERVICE_CHECK = 6


def find_dbs_status(dbs_number, obj_with_dob, capita=None, on_update=None):
    """
    Determines the next action to be taken for the given DBS check, if any

    :param dbs_number: The DBS certificate number given
    :param obj_with_dob: An object with birth_year, birth_month and birth_day attributes
    :param capita: (optional) User's response to being asked whether they have a Capita (enhanced) DBS certificate
    :param on_update: (optional) User's response to being asked whether they signed up to the DBS update service
    :return: DBSStatus
    """

    dbs_record = getattr(dbs.read(dbs_number), 'record', None)

    if dbs_record is not None:

        if not _dbs_dob_matches(dbs_record, obj_with_dob.birth_year, obj_with_dob.birth_month, obj_with_dob.birth_day):
            return DBSStatus.DOB_MISMATCH

        elif date_issued_within_three_months(datetime.strptime(dbs_record['date_of_issue'], '%Y-%m-%d')):
            return DBSStatus.OK

        elif on_update is None:
            return DBSStatus.NEED_ASK_IF_ON_UPDATE

        elif on_update:
            return DBSStatus.NEED_UPDATE_SERVICE_CHECK

        else:
            return DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP

    else:

        if capita is None:
            return DBSStatus.NEED_ASK_IF_CAPITA

        elif not capita:
            return DBSStatus.NEED_APPLY_FOR_NEW

        elif on_update is None:
            return DBSStatus.NEED_ASK_IF_ON_UPDATE

        elif on_update:
            return DBSStatus.NEED_UPDATE_SERVICE_CHECK

        else:
            return DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP


def awaiting_pith_dbs_action_from_user(dbs_statuses):
    return any(status in (DBSStatus.NEED_APPLY_FOR_NEW, DBSStatus.NEED_UPDATE_SERVICE_SIGN_UP)
               for status in dbs_statuses)


def dbs_date_of_birth_no_match(application, record):
    """
    :param application: the application to be tested against
    :param record: the record from the dbs api
    :return: a boolean to represent if there is no match between the applicant dob and the dbs dob
    """
    if record is None:
        return False

    app_details = ApplicantPersonalDetails.objects.get(application_id=application.application_id)

    return not _dbs_dob_matches(record, app_details.birth_year, app_details.birth_month, app_details.birth_day)


def _dbs_dob_matches(dbs_record, year, month, day):
    return datetime(year, month, day) == datetime.strptime(dbs_record['date_of_birth'], '%Y-%m-%d')


def date_issued_within_three_months(date_issued):
    """
    :param date_issued: the issue date of the dbs
    :return: a boolean to represent if there the dbs was issued within three months of today
    """
    now = datetime.today()
    if now - timedelta(3 * 365 / 12) <= date_issued:
        return True
    else:
        return False


def childminder_dbs_number_duplication_check(application, candidate_dbs_certificate_number):
    """
    Helper function to determine whether any DBS numbers listed in the application are not unique
    :param application: the application to be checked against
    :param candidate_dbs_certificate_number: the candidate dbs number to be tested against
    :return: object detailing whether the dbs numbers contained in an application are unique.
    """
    # Initialise response object (which defaults to indicating no duplicates)
    response = UniqueDbsCheckResult()

    if dbs_matches_childminder_dbs(application, candidate_dbs_certificate_number):
        response.dbs_numbers_unique = False
        response.duplicates_childminder_dbs = True
        response.duplicate_entry_indexes = get_duplicate_dbs_index(application, candidate_dbs_certificate_number)
        return response

    return response


def convert_mobile_to_notify_standard(mobile):
    mobile_prefix_REGEX = "^(\+44|0044)[7][0-9]{9}$"

    if mobile != "" and mobile is not None and re.match(mobile_prefix_REGEX, mobile):
        new_mobile = "07" + mobile[len(mobile) - 9:]
        return new_mobile
    else:
        return mobile


def childminder_references_and_user_email_duplication_check(email1, email2):
    """
    Helper function to determine whether the applications reference emails, and application email, are different.
    :param email1: an email to be compared.
    :param email2: another email to be compared.
    :return: A boolean True if emails are different or False if emails are the same.
    """

    if email1 != email2:
        return True
    else:
        return False


def show_resend_and_change_email(health_check_status, is_review=None):
    """
    Helper function to determine if the 'resend email' and 'change' email buttons should be visible inside the
        People in the Home task.
    :param health_check_status: Status of one adult's health check, a string equal to 'To do', 'Started' or 'Done'.
    :param is_review: A boolean True if the application is in review mode, e.g 'FURTHER INFORMATION'
    :return: A boolean True if the buttons should be displayed, False if the buttons should not be displayed.
    """

    # is_review is no longer needed, kept for legacy purposes but defaults to None.
    return health_check_status != 'Done'


def update_criminal_record_check(app_id, field_obj, status):
    """
    Updates the CriminalRecordCheck field with the given status.
    :param app_id: applicant's application_id
    :param field_obj: CriminalRecordCheck field or list of CriminalRecordCheck fields
    :param status: Value to update entry/entries with
    :return: Boolean True if successfully updated.
    """
    criminal_record_check_record = CriminalRecordCheck.objects.get(application_id=app_id)

    if isinstance(field_obj, list):
        for field in field_obj:
            setattr(criminal_record_check_record, field, status)
        criminal_record_check_record.save()

    elif isinstance(field_obj, str):
        setattr(criminal_record_check_record, field_obj, status)
        criminal_record_check_record.save()

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))

    return True


def get_criminal_record_check(app_id, field_obj):
    """
    :param app_id: applicant's application_id
    :param field_obj: CriminalRecordCheck field or list of CriminalRecordCheck fields
    :return: Boolean True if successfully updated.
    """
    criminal_record_check_record = CriminalRecordCheck.objects.get(application_id=app_id)

    if isinstance(field_obj, list):
        return {field: getattr(criminal_record_check_record, field) for field in field_obj}

    elif isinstance(field_obj, str):
        return getattr(criminal_record_check_record, field_obj)

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))


def get_childcare_register_type(app_id):
    childcare_record = ChildcareType.objects.get(application_id=app_id)

    if (childcare_record.zero_to_five is True) \
            & (childcare_record.five_to_eight is True) \
            & (childcare_record.eight_plus is True):
        cost = 35
        return 'EYR-CR-both', cost

    elif (childcare_record.zero_to_five is True) \
            & (childcare_record.five_to_eight is True) \
            & (childcare_record.eight_plus is False):
        cost = 35
        return 'EYR-CR-compulsory', cost

    elif (childcare_record.zero_to_five is True) \
            & (childcare_record.five_to_eight is False) \
            & (childcare_record.eight_plus is True):
        cost = 35
        return 'EYR-CR-voluntary', cost

    elif (childcare_record.zero_to_five is True) \
            & (childcare_record.five_to_eight is False) \
            & (childcare_record.eight_plus is False):
        cost = 35
        return 'EYR', cost

    elif (childcare_record.zero_to_five is False) \
            & (childcare_record.five_to_eight is True) \
            & (childcare_record.eight_plus is False):
        cost = 103
        return 'CR-compulsory', cost

    elif (childcare_record.zero_to_five is False) \
            & (childcare_record.five_to_eight is True) \
            & (childcare_record.eight_plus is True):
        cost = 103
        return 'CR-both', cost

    elif (childcare_record.zero_to_five is False) \
            & (childcare_record.five_to_eight is False) \
            & (childcare_record.eight_plus is True):
        cost = 103
        return 'CR-voluntary', cost


def get_adult_in_home(app_id, field_obj):
    """
    :param app_id: applicant's application_id
    :param field_obj: AdultInHome field or list of AdultInHome fields
    :return: Boolean True if successfully updated.
    """
    adult_in_home_record = AdultInHome.objects.get(application_id=app_id)

    if isinstance(field_obj, list):
        return {field: getattr(adult_in_home_record, field) for field in field_obj}

    elif isinstance(field_obj, str):
        return getattr(adult_in_home_record, field_obj)

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))


def update_adult_in_home(pk, field_obj, status):
    """
    Updates the AdultInHome field with the given status.
    :param pk: AdultInHome primary key
    :param field_obj: AdultInHome field or list of AdultInHome fields
    :param status: Value to update entry/entries with
    :return: Boolean True if successfully updated.
    """
    adult_in_home_record = AdultInHome.objects.get(pk=pk)

    if isinstance(field_obj, list):
        for field in field_obj:
            setattr(adult_in_home_record, field, status)
            adult_in_home_record.save()

    elif isinstance(field_obj, str):
        setattr(adult_in_home_record, field_obj, status)
        adult_in_home_record.save()

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))

    return True


def get_application_object(app_id):
    return Application.objects.get(application_id=app_id)


def get_application(app_id, field_obj):
    """
    :param app_id: applicant's application_id
    :param field_obj: Application field or list of Application fields
    :return:
    """
    application_record = Application.objects.get(application_id=app_id)

    if isinstance(field_obj, list):
        return {field: getattr(application_record, field) for field in field_obj}

    elif isinstance(field_obj, str):
        return getattr(application_record, field_obj)

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))


def update_application(app_id, field_obj, status):
    """
    Updates the Application field with the given status.
    :param app_id: applicant's application_id
    :param field_obj: Application field or list of Application fields
    :param status: Value to update entry/entries with
    :return: Boolean True if successfully updated.
    """
    application_record = Application.objects.get(application_id=app_id)

    if isinstance(field_obj, list):
        for field in field_obj:
            setattr(application_record, field, status)
            application_record.save()

    elif isinstance(field_obj, str):
        setattr(application_record, field_obj, status)
        application_record.save()

    else:
        raise TypeError(
            '{0} is not a valid field_obj, must be string or list not {1}'.format(field_obj, type(field_obj)))

    return True


class UniqueDbsCheckResult:
    """
    Class definition for the response object returned by a DBS uniqueness check
    """

    dbs_numbers_unique = True
    duplicates_childminder_dbs = False
    duplicates_household_member_dbs = False
    duplicate_entry_indexes = 0
