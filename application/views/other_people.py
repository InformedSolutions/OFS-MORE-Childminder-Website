import collections
import logging
import os
import random
import string

import pytz

from django.utils import timezone

import calendar
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from application.utils import build_url
from .. import status
from ..table_util import create_tables, Table, submit_link_setter
from ..summary_page_data import other_adult_link_dict, other_adult_name_dict, other_child_link_dict, \
    other_child_name_dict, other_adult_summary_link_dict, other_adult_summary_name_dict, \
    other_child_summary_name_dict, other_child_summary_link_dict
from ..business_logic import (health_check_email_resend_logic,
                              other_people_adult_details_logic,
                              other_people_children_details_logic,
                              rearrange_adults,
                              rearrange_children,
                              remove_adult,
                              remove_child,
                              reset_declaration,
                              show_resend_and_change_email)
from ..forms import (OtherPeopleAdultDBSForm,
                     OtherPeopleAdultDetailsForm,
                     OtherPeopleAdultQuestionForm,
                     OtherPeopleApproaching16Form,
                     OtherPeopleChildrenDetailsForm,
                     OtherPeopleChildrenQuestionForm,
                     OtherPeopleEmailConfirmationForm,
                     OtherPeopleGuidanceForm,
                     OtherPeopleResendEmailForm,
                     OtherPeopleSummaryForm)
from ..models import (AdultInHome,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      ArcComments,
                      ChildInHome)
from application.notify import send_email


logger = logging.getLogger()

def other_people_guidance(request):
    """
    Method returning the template for the People in your home: guidance page (for a given application)
    and navigating to the People in your home: adult question page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleGuidanceForm()
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleGuidanceForm(request.POST)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.people_in_home_status != 'COMPLETED':
                if application.people_in_home_status != 'WAITING':
                    status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('Other-People-Adult-Question-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-guidance.html', variables)


def other_people_adult_question(request):
    """
    Method returning the template for the People in your home: adult question page (for a given application) and
    navigating to the People in your home: adult details or People in your home: children details page when
    successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult question template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleAdultQuestionForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-adult-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
        application = Application.objects.get(pk=application_id_local)

        form = OtherPeopleAdultQuestionForm(request.POST, id=application_id_local)
        form.remove_flag()
        number_of_adults = AdultInHome.objects.filter(application_id=application_id_local).count()
        if form.is_valid():
            adults_in_home = form.cleaned_data.get('adults_in_home')
            application.adults_in_home = adults_in_home
            application.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # If adults live in your home, navigate to adult details page
            if adults_in_home == 'True':
                return HttpResponseRedirect(
                    reverse('Other-People-Adult-Details-View') + '?id=' + application_id_local + '&adults=' + str(
                        number_of_adults) + '&remove=0')
            # If adults do not live in your home, navigate to children question page
            elif adults_in_home == 'False':
                # Delete any existing adults
                adults = AdultInHome.objects.filter(
                    application_id=application_id_local)
                for adult in adults:
                    adult.delete()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                return HttpResponseRedirect(
                    reverse('Other-People-Children-Question-View') + '?id=' + application_id_local)
        else:

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-adult-question.html', variables)


def other_people_adult_details(request):
    """
    Method returning the template for the People in your home: adult details page (for a given application) and
    navigating to the People in your home: adult DBS page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        remove_person = int(request.GET["remove"])
        remove_button = True
        # If there are no adults in the database
        if number_of_adults == 0:
            # Set the number of adults to 1 to initialise one instance of the form
            number_of_adults = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one adult in the database
        if number_of_adults == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Remove specific adult if remove button is pressed
        remove_adult(application_id_local, remove_person)
        # Rearrange adult numbers if there are gaps
        rearrange_adults(number_of_adults, application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        email_list = [value for key, value in request.POST.items() if 'email_address' in key.lower()]
        for i in range(1, number_of_adults + 1):
            form = OtherPeopleAdultDetailsForm(
                id=application_id_local, adult=i, prefix=i, email_list=email_list)

            form.check_flag()
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Person " + str(i) + ")"
                is_review = True
            else:
                is_review = False



            # Disable email_address field if it cannot be changed.
            if AdultInHome.objects.filter(application_id=application_id_local, adult=i).exists():
                adult_record = AdultInHome.objects.get(application_id=application_id_local, adult=i)
                adult_health_check_status = adult_record.health_check_status
                if not show_resend_and_change_email(adult_health_check_status, is_review):
                    form.fields['email_address'].disabled = True
                else:
                    form.fields['email_address'].disabled = False

            form_list.append(form)

        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'remove_adult': number_of_adults - 1,
            'remove_button': remove_button,
            'people_in_home_status': application.people_in_home_status
        }
        status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-details.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        remove_button = True
        # If there are no adults in the database
        if number_of_adults == 0:
            # Set the number of adults to 1 to initialise one instance of the form
            number_of_adults = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one adult in the database
        if number_of_adults == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []

        email_list = [value for key, value in request.POST.items() if 'email_address' in key.lower()]
        for i in range(1, int(number_of_adults) + 1):

            form = OtherPeopleAdultDetailsForm(
                request.POST, id=application_id_local, adult=i, prefix=i, email_list=email_list)
            form.remove_flag()
            form_list.append(form)
            form.error_summary_title = 'There was a problem with the details (Person ' + str(
                i) + ')'
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Person " + str(i) + ")"
            if form.is_valid():
                adult_record = other_people_adult_details_logic(
                    application_id_local, form, i)
                adult_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                valid_list.append(True)
            else:
                valid_list.append(False)
        if 'submit' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                return HttpResponseRedirect(reverse('Other-People-Adult-DBS-View') + '?id=' + application_id_local +
                                            '&adults=' + number_of_adults, variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_adults': number_of_adults,
                    'add_adult': int(number_of_adults) + 1,
                    'remove_adult': int(number_of_adults) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-adult-details.html', variables)
        if 'add_person' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                add_adult = int(number_of_adults) + 1
                add_adult_string = str(add_adult)
                # Reset task status to IN_PROGRESS if adults are updated
                status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
                return HttpResponseRedirect(reverse('Other-People-Adult-Details-View') + '?id=' +
                                            application_id_local + '&adults=' + add_adult_string + '&remove=0#person' + add_adult_string,
                                            variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_adults': number_of_adults,
                    'add_adult': int(number_of_adults) + 1,
                    'remove_adult': int(number_of_adults) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-adult-details.html', variables)


def other_people_adult_dbs(request):
    """
    Method returning the template for the People in your home: adult DBS page (for a given application) and
    navigating to the People in your home: adult permission page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult DBS template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_adults + 1):
            adult = AdultInHome.objects.get(
                application_id=application_id_local, adult=i)
            if adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            elif adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            form = OtherPeopleAdultDBSForm(
                id=application_id_local, adult=i, prefix=i, name=name)
            form.check_flag()
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Person " + str(i) + ")"
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-adult-dbs.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        for i in range(1, int(number_of_adults) + 1):
            adult = AdultInHome.objects.get(
                application_id=application_id_local, adult=i)

            # Reset DBS number per post request such that it is cleansed per submission
            adult.dbs_certificate_number = ''

            # Generate name to pass to form, for display in HTML
            if adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            elif adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            form = OtherPeopleAdultDBSForm(
                request.POST, id=application_id_local, adult=i, prefix=i, name=name)

            form_list.append(form)
            form.error_summary_title = 'There was a problem with the DBS details (Person ' + str(
                i) + ')'
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Person " + str(i) + ")"
            if form.is_valid():
                adult_record = AdultInHome.objects.get(
                    application_id=application_id_local, adult=i)
                adult_record.dbs_certificate_number = form.cleaned_data.get(
                    'dbs_certificate_number')
                form.remove_flag()
                adult_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                valid_list.append(True)
            else:
                valid_list.append(False)
        # If all forms are valid
        if False not in valid_list:
            variables = {
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            return HttpResponseRedirect(reverse('Other-People-Children-Question-View') + '?id=' +
                                        application_id_local + '&adults=' + number_of_adults, variables)
        # If there is an invalid form
        elif False in valid_list:
            variables = {
                'form_list': form_list,
                'application_id': application_id_local,
                'number_of_adults': number_of_adults,
                'add_adult': int(number_of_adults) + 1,
                'people_in_home_status': application.people_in_home_status
            }
            return render(request, 'other-people-adult-dbs.html', variables)


def other_people_children_question(request):
    """
    Method returning the template for the People in your home: children question page (for a given application) and
    navigating to the People in your home: children details page or summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: children question template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleChildrenQuestionForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        number_of_adults = AdultInHome.objects.filter(
            application_id=application_id_local).count()
        adults_in_home = application.adults_in_home
        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem"
        variables = {
            'form': form,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'adults_in_home': adults_in_home,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-children-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleChildrenQuestionForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        form.remove_flag()
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            children_in_home = form.cleaned_data.get('children_in_home')
            application.children_in_home = children_in_home
            application.children_turning_16 = False
            application.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if children_in_home == 'True':
                return HttpResponseRedirect(
                    reverse('Other-People-Children-Details-View') + '?id=' + application_id_local + '&children=' + str(
                        number_of_children) + '&remove=0')
            elif children_in_home == 'False':
                # Delete any existing children from database
                children = ChildInHome.objects.filter(
                    application_id=application_id_local)
                for child in children:
                    child.delete()
                reset_declaration(application)
                return HttpResponseRedirect(reverse('Other-People-Summary-View') + '?id=' + application_id_local)
        else:
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-children-question.html', variables)


def other_people_children_details(request):
    """
    Method returning the template for the People in your home: children details page (for a given application) and
    navigating to the People in your home: approaching 16 page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: children details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_children = int(request.GET["children"])
        remove_person = int(request.GET["remove"])
        remove_button = True
        # If there are no adults in the database
        if number_of_children == 0:
            # Set the number of children to 1 to initialise one instance of the form
            number_of_children = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one child in the database
        if number_of_children == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        remove_child(application_id_local, remove_person)
        rearrange_children(number_of_children, application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_children + 1):
            form = OtherPeopleChildrenDetailsForm(
                id=application_id_local, child=i, prefix=i)
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Child " + str(i) + ")"
            form_list.append(form)
            form.check_flag()
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'add_child': number_of_children + 1,
            'remove_button': remove_button,
            'remove_child': number_of_children - 1,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-children-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_children = request.POST["children"]
        remove_button = True
        # If there are no adults in the database
        if number_of_children == 0:
            # Set the number of children to 1 to initialise one instance of the form
            number_of_children = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one child in the database
        if number_of_children == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        # List to allow for the age verification of each form
        age_list = []
        for i in range(1, int(number_of_children) + 1):
            form = OtherPeopleChildrenDetailsForm(
                request.POST, id=application_id_local, child=i, prefix=i)
            form.remove_flag()
            form_list.append(form)
            form.error_summary_title = 'There was a problem with the details (Child ' + str(i) + ')'
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem (Person " + str(i) + ")"
            if form.is_valid():
                child_record = other_people_children_details_logic(
                    application_id_local, form, i)
                child_record.save()
                reset_declaration(application)
                valid_list.append(True)
                # Calculate child's age
                birth_day = form.cleaned_data.get('date_of_birth')[0]
                birth_month = form.cleaned_data.get('date_of_birth')[1]
                birth_year = form.cleaned_data.get('date_of_birth')[2]
                applicant_dob = date(birth_year, birth_month, birth_day)
                today = date.today()
                age = today.year - applicant_dob.year - (
                        (today.month, today.day) < (applicant_dob.month, applicant_dob.day))
                if 15 <= age < 16:
                    age_list.append(True)
                elif age < 15:
                    age_list.append(False)
            else:
                valid_list.append(False)
        if 'submit' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                }
                # If a child is approaching 16, navigate to approaching 16 page
                if True in age_list:
                    application.children_turning_16 = True
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                    return HttpResponseRedirect(
                        reverse('Other-People-Approaching-16-View') + '?id=' + application_id_local, variables)
                # If no child is approaching 16, navigate to summary page
                elif True not in age_list:
                    application.children_turning_16 = False
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                    return HttpResponseRedirect(reverse('Other-People-Summary-View') + '?id=' + application_id_local,
                                                variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-children-details.html', variables)
        if 'add_child' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                # If a child is approaching 16, navigate to approaching 16 page
                if True in age_list:
                    application.children_turning_16 = True
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                add_child = int(number_of_children) + 1
                add_child_string = str(add_child)
                return HttpResponseRedirect(reverse('Other-People-Children-Details-View') + '?id=' +
                                            application_id_local + '&children=' + add_child_string + '&remove=0#person' + add_child_string,
                                            variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-children-details.html', variables)


def other_people_approaching_16(request):
    """
    Method returning the template for the People in your home: approaching 16 page (for a given application)
    and navigating to the People in your home: number of children page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: approaching 16 template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleApproaching16Form()
        application = Application.objects.get(pk=application_id_local)
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-approaching-16.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleApproaching16Form(request.POST)
        application = Application.objects.get(pk=application_id_local)
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            variables = {
                'form': form,
                'number_of_children': number_of_children,
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            return HttpResponseRedirect(reverse('Other-People-Summary-View') + '?id=' + application_id_local, variables)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-approaching-16.html', variables)


def other_people_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
        children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
        form = OtherPeopleSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        adult_table_list = []
        adult_health_check_status_list = []

        for index, adult in enumerate(adults_list):

            name = ' '.join([adult.first_name, (adult.middle_names or ''), adult.last_name])
            birth_date = ' '.join([str(adult.birth_day), calendar.month_name[adult.birth_month], str(adult.birth_year)])

            if application.people_in_home_status == 'IN_PROGRESS' and any(
                    [adult.email_resent_timestamp is None for adult in adults_list]):

                other_adult_fields = collections.OrderedDict([
                    ('full_name', name),
                    ('date_of_birth', birth_date),
                    ('relationship', adult.relationship),
                    ('email', adult.email),
                    ('dbs_certificate_number', adult.dbs_certificate_number),
                ])

            else:

                other_adult_fields = collections.OrderedDict([
                    ('health_check_status', adult.health_check_status),
                    ('full_name', name),
                    ('date_of_birth', birth_date),
                    ('relationship', adult.relationship),
                    ('email', adult.email),
                    ('dbs_certificate_number', adult.dbs_certificate_number),
                ])

            if adult.health_check_status == 'To do':
                status.update(application_id_local, 'people_in_home_status', 'WAITING')

            # If adult health check status is not complete, add to health check status list
            if adult.health_check_status != 'Done':
                adult_health_check_status_list.append('To do')

            # If the adult health check status is marked as flagged, set the email resend limit to 0
            if adult.health_check_status == 'Started':
                adult.email_resent = 0
                adult.save()

            # Counter for table object to correctly set link in generic-error-summary template for flagged health check.
            table = Table([adult.pk])
            table.loop_counter = index + 1

            other_adult_table = collections.OrderedDict({
                'table_object': table,
                'fields': other_adult_fields,
                'title': name,
                'error_summary_title': ('There was a problem (' + name + ')')
            })

            adult_table_list.append(other_adult_table)

        # Set People in home status to Done if all adult health check statuses have been completed
        if len(adult_health_check_status_list) == 0:
            status.update(application_id_local, 'people_in_home_status', 'COMPLETED')

        back_link_addition = '&adults=' + str((len(adult_table_list))) + '&remove=0'

        for table in adult_table_list:
            table['other_people_numbers'] = back_link_addition

        # Add display_buttons for each adult
        is_review = application.application_status == 'FURTHER_INFORMATION'

        display_buttons_list = []

        for table in adult_table_list:
            display_buttons = show_resend_and_change_email(adult.health_check_status, is_review)

            display_buttons_list.append(display_buttons)

        adult_table_list = create_tables(adult_table_list, other_adult_name_dict, other_adult_link_dict)

        child_table_list = []
        for child in children_list:
            name = ' '.join([child.first_name, (child.middle_names or ''), child.last_name])

            other_child_fields = collections.OrderedDict([
                ('full_name', name),
                ('date_of_birth', ' '.join([str(child.birth_day), calendar.month_name[child.birth_month],
                                            str(child.birth_year)])),
                ('relationship', child.relationship)
            ])

            other_child_table = collections.OrderedDict({
                'table_object': Table([child.pk]),
                'fields': other_child_fields,
                'title': name,
                'error_summary_title': ('There was a problem (' + name + ')')
            })

            child_table_list.append(other_child_table)

        back_link_addition = '&children=' + str(len(child_table_list)) + '&remove=0'

        for table in child_table_list:
            table['other_people_numbers'] = back_link_addition
        child_table_list = create_tables(child_table_list, other_child_name_dict, other_child_link_dict, )

        if not adult_table_list:
            adults_in_home = False
        else:
            adults_in_home = True

        if not child_table_list:
            children_in_home = False
        else:
            children_in_home = True

        adult_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'adults_in_home': adults_in_home},
            'title': 'Adults in your home',
            'error_summary_title': 'There was a problem'
        })

        child_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'children_in_home': children_in_home},
            'title': 'Children in your home',
            'error_summary_title': 'There was a problem'
        })

        adult_table = create_tables([adult_table], other_adult_summary_name_dict, other_adult_summary_link_dict)
        child_table = create_tables([child_table], other_child_summary_name_dict, other_child_summary_link_dict)

        table_list = adult_table + child_table + adult_table_list + child_table_list

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem"

        variables = {
            'page_title': 'Check your answers: people in your home',
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'turning_16': application.children_turning_16,
            'people_in_home_status': application.people_in_home_status,
            'display_buttons_list': display_buttons_list
        }
        variables = submit_link_setter(variables, table_list, 'people_in_home', application_id_local)

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(application_id=application_id_local)

        # If reaching the summary page for the first time
        if application.people_in_home_status == 'IN_PROGRESS' or application.people_in_home_status == 'WAITING':
            adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
            if application.adults_in_home is True and any(
                    [adult.email_resent_timestamp is None for adult in adults_list]):
                return HttpResponseRedirect(
                    reverse('Other-People-Email-Confirmation-View') + '?id=' + application_id_local)
            elif application.adults_in_home is False:
                status.update(application_id_local, 'people_in_home_status', 'COMPLETED')
                return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
            else:
                return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)

        else:
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)


def other_people_email_confirmation(request):
    """
    Method returning the template for the People in your home: email confirmation page (for a given application)
    and navigating to the task list when successfully completed. Emails are sent to each adult living with or
    regularly visiting the home of the applicant
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: email confirmation template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleEmailConfirmationForm()
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        adults = AdultInHome.objects.filter(application_id=application_id_local)
        # Send health check e-mail to each household member
        # Generate parameters for Notify e-mail template
        template_id = '1e3c066a-4bbe-4743-b6b1-1d52ac291caf'

        if all([adult.email_resent_timestamp is not None for adult in adults]):
            return HttpResponseRedirect(build_url('Task-List-View', get={'id': application_id_local}))

        applicant = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
        applicant_name = ApplicantName.objects.get(personal_detail_id=applicant)
        if applicant_name.middle_names == '':
            applicant_name_formatted = applicant_name.first_name + ' ' + applicant_name.last_name
        else:
            applicant_name_formatted = applicant_name.first_name + ' ' + applicant_name.middle_names + ' ' + applicant_name.last_name

        if settings.EXECUTING_AS_TEST == 'True':
            os.environ['EMAIL_VALIDATION_URL'] = ''
        # For each household member, generate a unique link to access their health check page
        # and send an e-mail
        for adult in adults:
            if adult.health_check_status != 'Done':
                adult.token = ''.join([random.choice(string.digits[1:]) for n in range(7)])
                email = adult.email
                base_url = settings.PUBLIC_APPLICATION_URL
                personalisation = {"link": base_url +
                                           reverse('Health-Check-Authentication', kwargs={'id': adult.token}).replace(
                                               '/childminder', ''),
                                   "firstName": adult.first_name,
                                   "ApplicantName": applicant_name_formatted}
                print(personalisation['link'])
                r = send_email(email, personalisation, template_id)
                if settings.EXECUTING_AS_TEST == 'True':
                    os.environ['EMAIL_VALIDATION_URL'] = os.environ['EMAIL_VALIDATION_URL'] + " " + str(
                        personalisation['link'])

                # Set a timestamp when the e-mail was last send (for later use in resend e-mail logic)
                adult.email_resent_timestamp = datetime.now(pytz.utc)
                adult.save()

        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-email-confirmation.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleEmailConfirmationForm(request.POST)
        form.remove_flag()
        if form.is_valid():
            # Set the People in your home task to WAITING (to be set to Done once all household members
            # have completed their health checks) only if all health checks have been completed
            adults_list = AdultInHome.objects.filter(application_id=application_id_local)
            adult_health_check_status_list = []
            for adult in adults_list:
                if adult.health_check_status != 'Done':
                    adult_health_check_status_list.append('To do')
            if len(adult_health_check_status_list) > 0:
                status.update(application_id_local, 'people_in_home_status', 'WAITING')
            elif len(adult_health_check_status_list) == 0:
                status.update(application_id_local, 'people_in_home_status', 'COMPLETED')
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-email-confirmation.html', variables)


def other_people_resend_email(request):
    """
    Method returning the template for the People in your home: resend email page (for a given application)
    and navigating to the task list when successfully completed. An e-mail is resent to a specific household
    member upon clicking a button, with a limit of 3 resends per 24 hours permitted
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: resend email template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults = request.GET["adult"]
        adult_number = int(adults) - 2
        form = OtherPeopleResendEmailForm()
        form.check_flag()
        # Generate variables for display on email resend page
        application = Application.objects.get(pk=application_id_local)
        adult_record = AdultInHome.objects.get(application_id=application_id_local, adult=adult_number)

        if adult_record.middle_names != '':
            name = adult_record.first_name + ' ' + adult_record.middle_names + ' ' + adult_record.last_name

        elif adult_record.middle_names == '':
            name = adult_record.first_name + ' ' + adult_record.last_name

        # If the health check email has been resent more than 3 times, display an error message
        if adult_record.email_resent > 3:
            resend_limit = True
            variables = {
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status,
                'name': name,
                'email': adult_record.email,
                'adult': adult_record.adult,
                'resend_limit': resend_limit
            }
            return render(request, 'other-people-resend-email.html', variables)

        else:
            resend_limit = False
            variables = {
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status,
                'name': name,
                'email': adult_record.email,
                'adult': adult_record.adult,
                'resend_limit': resend_limit
            }

            if adult_record.health_check_status == 'Started':
                variables['error_summary_title'] = "There was a problem with " \
                                                   + name + "'s answers to the health questions"
                variables['arc_comment'] = ArcComments.objects.get(table_pk=adult_record.pk).comment

            return render(request, 'other-people-resend-email.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        adult = request.POST["adult"]
        form = OtherPeopleResendEmailForm(request.POST)
        form.remove_flag()
        # Generate parameters for e-mail template
        application = Application.objects.get(pk=application_id_local)
        applicant = ApplicantPersonalDetails.objects.get(application_id=application_id_local)
        applicant_name = ApplicantName.objects.get(personal_detail_id=applicant)
        if applicant_name.middle_names == '':
            applicant_name_formatted = applicant_name.first_name + ' ' + applicant_name.last_name
        else:
            applicant_name_formatted = applicant_name.first_name + ' ' + applicant_name.middle_names + ' ' + applicant_name.last_name

        adult_record = AdultInHome.objects.get(application_id=application_id_local, adult=adult)

        if adult_record.middle_names != '':
            name = adult_record.first_name + ' ' + adult_record.middle_names + ' ' + adult_record.last_name
        elif adult_record.middle_names == '':
            name = adult_record.first_name + ' ' + adult_record.last_name

        if form.is_valid():

            resend_limit_reached = health_check_email_resend_logic(adult_record)

            if resend_limit_reached is False:

                # Generate variables for e-mail template
                if application.people_in_home_arc_flagged is True:
                    template_id = '63628c30-da8a-4533-b1e3-712942c75abb'
                else:
                    template_id = '5bbf3677-49e9-47d0-acf2-55a9a03d8242'
                email = adult_record.email
                # Generate unique link for the household member to access their health check page
                adult_record.token = ''.join([random.choice(string.digits[1:]) for n in range(7)])
                adult_record.validated = False
                base_url = settings.PUBLIC_APPLICATION_URL.replace('/childminder', '')
                personalisation = {"link": base_url + reverse('Health-Check-Authentication',
                                                              kwargs={'id': adult_record.token}),
                                   "firstName": adult_record.first_name,
                                   "ApplicantName": applicant_name_formatted}
                print(personalisation['link'])
                # Send e-mail to household member
                r = send_email(email, personalisation, template_id)
                # Increase the email resend count by 1
                email_resent = adult_record.email_resent
                if email_resent is not None:
                    adult_record.email_resent = email_resent + 1
                else:
                    adult_record.email_resent = 1
                # Reset timestamp of when an email was last sent to the household member
                adult_record.email_resent_timestamp = datetime.now(pytz.utc)
                adult_record.save()

                # If health check has been flagged, remove flag once email resent; else, pass.
                # form.remove_flag won't work because form is simply a 'Continue' button - it has no fields.
                try:
                    adult_arc_comment = ArcComments.objects.get(table_pk=adult_record.pk)
                    if adult_arc_comment.flagged:
                        adult_arc_comment.flagged = False
                        adult_arc_comment.save()
                except ObjectDoesNotExist:
                    pass

                return HttpResponseRedirect(reverse(
                    'Other-People-Resend-Confirmation-View') + '?id=' + application_id_local + '&adult=' + adult)

            elif resend_limit_reached:

                # Display error message
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                    'name': name,
                    'email': adult_record.email,
                    'adult': adult_record.adult,
                    'resend_limit': resend_limit_reached
                }
                return render(request, 'other-people-resend-email.html', variables)

        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-resend-email.html', variables)


def other_people_resend_confirmation(request):
    """
    Method returning the template for the People in your home: resend confirmation page (for a given application)
    and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: resend confirmation template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults = request.GET["adult"]
        adult_number = int(adults)
        form = OtherPeopleResendEmailForm()
        form.check_flag()
        # Generate variables for display on email resent page
        application = Application.objects.get(pk=application_id_local)
        adult_record = AdultInHome.objects.get(application_id=application_id_local, adult=adult_number)

        if adult_record.middle_names != '':
            name = adult_record.first_name + ' ' + adult_record.middle_names + ' ' + adult_record.last_name

        elif adult_record.middle_names == '':
            name = adult_record.first_name + ' ' + adult_record.last_name

        if adult_record.health_check_status == 'Started':
            status.update(application_id_local, 'people_in_home_status', 'WAITING')
            adult_record.health_check_status = 'To do'
            adult_record.save()

        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status,
            'name': name,
            'email': adult_record.email
        }
        return render(request, 'other-people-resend-confirmation.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleResendEmailForm(request.POST)
        form.remove_flag()

        # Navigate back to task summary
        if form.is_valid():
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-resend-confirmation.html', variables)
