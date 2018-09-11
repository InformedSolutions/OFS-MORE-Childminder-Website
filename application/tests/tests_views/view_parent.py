"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_views.py --

@author: Informed Solutions
"""

import datetime
from uuid import UUID

from django.conf import settings
from django.test import Client
from django.test import TestCase
from django.urls import resolve, reverse

from ... import models
from ...views import (application_saved,
                      card_payment_details,
                      contact_phone,
                      contact_summary,
                      declaration_declaration,
                      declaration_summary,
                      documents_needed,
                      first_aid_training_declaration,
                      first_aid_training_details,
                      first_aid_training_guidance,
                      first_aid_training_renew,
                      first_aid_training_summary,
                      first_aid_training_training,
                      health_intro,
                      health_booklet,
                      health_check_answers,
                      home_ready,
                      other_people_guidance,
                      other_people_adult_question,
                      other_people_adult_details,
                      other_people_adult_dbs,
                      other_people_children_question,
                      other_people_children_details,
                      other_people_approaching_16,
                      other_people_summary,
                      payment,
                      payment_confirmation,
                      personal_details_childcare_address,
                      personal_details_childcare_address_manual,
                      personal_details_childcare_address_select,
                      personal_details_own_children,
                      personal_details_working_in_other_childminder_home,
                      personal_details_dob,
                      personal_details_guidance,
                      personal_details_home_address,
                      personal_details_home_address_manual,
                      personal_details_home_address_select,
                      personal_details_location_of_care,
                      personal_details_name,
                      personal_details_summary,
                      prepare_for_interview,
                      references_intro,
                      references_first_reference,
                      references_first_reference_address,
                      references_first_reference_address_select,
                      references_first_reference_address_manual,
                      references_first_reference_contact_details,
                      references_second_reference,
                      references_second_reference_address,
                      references_second_reference_address_select,
                      references_second_reference_address_manual,
                      references_second_reference_contact_details,
                      references_summary,
                      start_page,
                      task_list,
                      type_of_childcare_age_groups,
                      type_of_childcare_guidance,
                      type_of_childcare_register)
from ...views.login import account_selection, NewUserSignInView, ExistingUserSignInView
from ...models import Application, UserDetails


class ViewsTest(TestCase):
    """
    This is the base class that all the views tests will inherit from in order
    to inherit the imported modules
    """
    pass
