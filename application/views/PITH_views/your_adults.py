import collections
import datetime
import logging

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application.models import Application, AdultInHome, ChildAddress, ApplicantPersonalDetails, ApplicantHomeAddress


def get_first_adult_number_for_address_entry(application_id):
    """
    Helper method to fetch the child number for the first child for which address details are to be supplied
    :param application_id: the application identifier to be queried against
    :return: the next child number or None if no more children require address details to be provided
    """

    first_adult = AdultInHome.objects.filter(application_id=application_id, PITH_same_address=False).order_by(
        'adult').first()
    return first_adult.adult


def __get_next_adult_number_for_address_entry(application_id, current_adult):
    """
    Helper method for sequencing a user through the workflow for providing child address details
    :param application_id: the application identifier to be queried against
    :param current_child: the current child information is being supplied for
    :return: the next child number or None if no more children require address details to be provided
    """

    if __get_all_adults_count(application_id) > current_adult:
        next_adult = current_adult + 1
        next_adult_record = AdultInHome.objects.get(application_id=application_id, adult=next_adult)
        if not next_adult_record.PITH_same_address:
            return next_adult
        else:
            return __get_next_adult_number_for_address_entry(application_id, next_adult)
    else:
        return None


def __get_all_adults_count(application_id):
    """
    Helper method for providing a count of all children are associated with a childminder
    :param application_id: the application identifier to be queried against
    :return: a count of of how many children do not live a childminder
    """
    return AdultInHome.objects.filter(application_id=application_id).count()

