import collections
import logging
import os
import random
import string

import pytz

from django.utils import timezone

import calendar
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from application.utils import build_url
from application.views.your_children import __create_child_table
from .. import status
from ..table_util import create_tables, Table, submit_link_setter
from ..summary_page_data import other_adult_link_dict, other_adult_name_dict, other_child_link_dict, \
    other_child_name_dict, other_adult_summary_link_dict, other_adult_summary_name_dict, \
    other_child_summary_name_dict, other_child_summary_link_dict, child_not_in_the_home_link_dict, \
    child_not_in_the_home_name_dict, other_child_not_in_the_home_summary_name_dict, \
    other_child_not_in_the_home_summary_link_dict
from ..business_logic import (health_check_email_resend_logic,
                              other_people_adult_details_logic,
                              rearrange_adults,
                              remove_adult,
                              reset_declaration,
                              show_resend_and_change_email)
from ..forms import (
                     OtherPeopleAdultDetailsForm,
                     OtherPeopleApproaching16Form,
                     OtherPeopleEmailConfirmationForm,
                     OtherPeopleResendEmailForm,
                     OtherPeopleSummaryForm)
from ..models import (AdultInHome,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      ArcComments,
                      ChildInHome, Child, ApplicantHomeAddress)
from application.notify import send_email


logger = logging.getLogger()


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
                form.error_summary_title = "There was a problem with Person {0}'s details".format(str(i))
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
            form.error_summary_title = "There was a problem with Person {0}'s details".format(str(i))
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
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
                return HttpResponseRedirect(reverse('PITH-Lived-Abroad-View') + '?id=' + application_id_local +
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
                return HttpResponseRedirect(reverse('PITH-Adult-Details-View') + '?id=' +
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


def other_people_approaching_16(request):
    """
    Method returning the template for the People in your home: approaching 16 page (for a given application)
    and navigating to the People in your home: number of children page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: approaching 16 template
    """

    def get_success_url(app_id):
        adults = AdultInHome.objects.filter(application_id=app_id)
        home_address = ApplicantHomeAddress.objects.get(application_id=app_id, current_address=True)
        childcare_address = ApplicantHomeAddress.objects.get(application_id=app_id, childcare_address=True)

        if home_address == childcare_address:
            return 'PITH-Own-Children-Check-View'
        else:
            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                return 'Task-List-View'
            else:
                return 'PITH-Summary-View'

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
            return HttpResponseRedirect(reverse(get_success_url(application_id_local)) + '?id=' + application_id_local, variables)
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

    def __create_child_not_in_the_home_table(child):
        child_table = __create_child_table(child)
        child_table['table_object'].other_people_numbers = '&children=' + str(child.child) + '&remove=0'

        return child_table

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
        children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
        children_not_in_the_home_list = Child.objects.filter(application_id=application_id_local).order_by('child')
        form = OtherPeopleSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        adult_table_list = []
        adult_health_check_status_list = []
        display_buttons_list = []

        for index, adult in enumerate(adults_list):

            name = ' '.join([adult.first_name, (adult.middle_names or ''), adult.last_name])
            birth_date = ' '.join([str(adult.birth_day), calendar.month_name[adult.birth_month], str(adult.birth_year)])

            # Add display_buttons for each adult
            is_review = application.application_status == 'FURTHER_INFORMATION'

            try:
                adult_health_check_status = adult.health_check_status
            except KeyError:
                adult_health_check_status = ''

            display_buttons = show_resend_and_change_email(adult_health_check_status, is_review)
            display_buttons_list.append(display_buttons)

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
                'error_summary_title': ('There was a problem with {0}\'s details'.format(name))
            })

            adult_table_list.append(other_adult_table)

        # Set People in home status to Done if all adult health check statuses have been completed
        if len(adult_health_check_status_list) == 0:
            status.update(application_id_local, 'people_in_home_status', 'COMPLETED')

        back_link_addition = '&adults=' + str((len(adult_table_list))) + '&remove=0'

        for table in adult_table_list:
            table['other_people_numbers'] = back_link_addition

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
                'error_summary_title': ('There was a problem with {0}\'s details'.format(name))
            })

            child_table_list.append(other_child_table)

        back_link_addition = '&children=' + str(len(child_table_list)) + '&remove=0'

        for table in child_table_list:
            table['other_people_numbers'] = back_link_addition
        child_table_list = create_tables(child_table_list, other_child_name_dict, other_child_link_dict)

        # Populating Children not in the Home:
        children_not_in_the_home_table_list = [__create_child_not_in_the_home_table(child) for child in children_not_in_the_home_list]
        children_not_in_the_home_table = create_tables(children_not_in_the_home_table_list,
                                                       child_not_in_the_home_name_dict, child_not_in_the_home_link_dict)

        adults_in_home = bool(adult_table_list)
        children_in_home = bool(child_table_list)
        children_not_in_home = bool(children_not_in_the_home_table_list)

        adult_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'adults_in_home': adults_in_home},
            'title': 'Adults in the home',
            'error_summary_title': 'There was a problem'
        })

        child_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'children_in_home': children_in_home},
            'title': 'Children in the home',
            'error_summary_title': 'There was a problem'
        })

        not_child_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'children_not_in_the_home': children_not_in_home},
            'title': 'Children not in the home',
            'error_summary_title': 'There was a problem'
        })

        adult_table = create_tables([adult_table], other_adult_summary_name_dict, other_adult_summary_link_dict)
        child_table = create_tables([child_table], other_child_summary_name_dict, other_child_summary_link_dict)
        not_child_table = create_tables([not_child_table], other_child_not_in_the_home_summary_name_dict, other_child_not_in_the_home_summary_link_dict)

        table_list = adult_table + adult_table_list + child_table + child_table_list
        if application.own_children_not_in_home is not None:
            table_list += not_child_table + children_not_in_the_home_table

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem"

        sending_emails = application.adults_in_home is True and any(
                [adult.email_resent_timestamp is None for adult in adults_list])

        num_children_not_in_home = len(Child.objects.filter(application_id=application_id_local))

        variables = {
            'page_title': 'Check your answers: people in the home',
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'turning_16': application.children_turning_16,
            'people_in_home_status': application.people_in_home_status,
            'display_buttons_list': display_buttons_list,
            'sending_emails': sending_emails,
            'num_children_not_in_home': num_children_not_in_home
        }
        variables = submit_link_setter(variables, table_list, 'people_in_home', application_id_local)

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(application_id=application_id_local)

        # If reaching the summary page for the first time
        if application.people_in_home_status == 'IN_PROGRESS' or application.people_in_home_status == 'WAITING':
            adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
            if any(adult.health_check_status == 'To do' for adult in adults_list):
                status.update(application_id_local, 'people_in_home_status', 'WAITING')

            if application.adults_in_home is True and any(
                    [adult.email_resent_timestamp is None for adult in adults_list]):
                status.update(application_id_local, 'people_in_home_status', 'WAITING')
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
                variables['arc_comment'] = ArcComments.objects.get(table_pk=adult_record.pk, field_name='health_check_status').comment

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

                # If the previous adult_record was completed and resent:
                if adult_record.validated:
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
                    adult_arc_comment = ArcComments.objects.get(table_pk=adult_record.pk, field_name='health_check_status')
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
