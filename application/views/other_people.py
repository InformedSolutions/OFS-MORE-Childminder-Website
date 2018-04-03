import collections

from django.utils import timezone

import calendar
from datetime import date

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .. import status
from ..table_util import create_tables, Table, submit_link_setter
from ..summary_page_data import other_adult_link_dict, other_adult_name_dict, other_child_link_dict,\
                                other_child_name_dict, other_adult_summary_link_dict, other_adult_summary_name_dict,\
                                other_child_summary_name_dict, other_child_summary_link_dict
from ..business_logic import (other_people_adult_details_logic,
                              other_people_children_details_logic,
                              rearrange_adults,
                              rearrange_children,
                              remove_adult,
                              remove_child,
                              reset_declaration)
from ..forms import (OtherPeopleAdultDBSForm,
                     OtherPeopleAdultDetailsForm,
                     OtherPeopleAdultPermissionForm,
                     OtherPeopleAdultQuestionForm,
                     OtherPeopleApproaching16Form,
                     OtherPeopleChildrenDetailsForm,
                     OtherPeopleChildrenQuestionForm,
                     OtherPeopleGuidanceForm,
                     OtherPeopleSummaryForm)
from ..models import (AdultInHome,
                      Application,
                      ChildInHome)


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
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-question?id=' + application_id_local)
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
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'people_in_home_status', 'IN_PROGRESS')

        form = OtherPeopleAdultQuestionForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        number_of_adults = AdultInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            adults_in_home = form.cleaned_data.get('adults_in_home')
            application.adults_in_home = adults_in_home
            application.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # If adults live in your home, navigate to adult details page
            if adults_in_home == 'True':
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-details?id=' +
                                            application_id_local + '&adults=' + str(number_of_adults) + '&remove=0')
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
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-question?id=' +
                                            application_id_local)
        else:
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
        for i in range(1, number_of_adults + 1):
            form = OtherPeopleAdultDetailsForm(
                id=application_id_local, adult=i, prefix=i)
            form.check_flag()
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
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
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
        for i in range(1, int(number_of_adults) + 1):
            form = OtherPeopleAdultDetailsForm(
                request.POST, id=application_id_local, adult=i, prefix=i)
            form.remove_flag()
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
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
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-dbs?id=' + application_id_local +
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
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/other-people/adult-details?id=' +
                    application_id_local + '&adults=' + add_adult_string + '&remove=0',
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
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
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
            # Generate name to pass to form, for display in HTML
            if adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            elif adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            form = OtherPeopleAdultDBSForm(
                request.POST, id=application_id_local, adult=i, prefix=i, name=name)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
            if form.is_valid():
                adult_record = AdultInHome.objects.get(
                    application_id=application_id_local, adult=i)
                adult_record.dbs_certificate_number = form.cleaned_data.get(
                    'dbs_certificate_number')
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
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-permission?id=' +
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


def other_people_adult_permission(request):
    """
    Method returning the template for the People in your home: adult permission page (for a given application) and
    navigating to the People in your home: children question page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult permission template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_adults + 1):
            form = OtherPeopleAdultPermissionForm(
                id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-permission.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        for i in range(1, int(number_of_adults) + 1):
            form = OtherPeopleAdultPermissionForm(
                request.POST, id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
            if form.is_valid():
                adult_record = AdultInHome.objects.get(
                    application_id=application_id_local, adult=i)
                adult_record.permission_declare = form.cleaned_data.get(
                    'permission_declare')
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
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-question?id=' +
                                        application_id_local, variables)
        # If there is an invalid form
        elif False in valid_list:
            variables = {
                'form_list': form_list,
                'application_id': application_id_local,
                'number_of_adults': number_of_adults,
                'add_adult': int(number_of_adults) + 1,
                'people_in_home_status': application.people_in_home_status
            }
            return render(request, 'other-people-adult-permission.html', variables)


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
        application = Application.objects.get(pk=application_id_local)
        number_of_adults = AdultInHome.objects.filter(
            application_id=application_id_local).count()
        adults_in_home = application.adults_in_home
        variables = {
            'form': form,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'adults_in_home': adults_in_home,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-children-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'people_in_home_status', 'IN_PROGRESS')

        form = OtherPeopleChildrenQuestionForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
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
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-details?id=' +
                                            application_id_local + '&children=' + str(number_of_children) + '&remove=0')
            elif children_in_home == 'False':
                # Delete any existing children from database
                children = ChildInHome.objects.filter(
                    application_id=application_id_local)
                for child in children:
                    child.delete()
                reset_declaration(application)
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local)
        else:
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
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
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
            form.error_summary_title = 'There is a problem with this form (Child ' + str(
                i) + ')'
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
                    return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/approaching-16?id=' +
                                                application_id_local, variables)
                # If no child is approaching 16, navigate to summary page
                elif True not in age_list:
                    application.children_turning_16 = False
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                    return HttpResponseRedirect(
                        settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local,
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
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                add_child = int(number_of_children) + 1
                add_child_string = str(add_child)
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/other-people/children-details?id=' +
                    application_id_local + '&children=' + add_child_string + '&remove=0',
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
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            variables = {
                'form': form,
                'number_of_children': number_of_children,
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local, variables)
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
        adults_list = AdultInHome.objects.filter(
            application_id=application_id_local).order_by('adult')
        adult_name_list = []
        adult_birth_day_list = []
        adult_birth_month_list = []
        adult_birth_year_list = []
        adult_relationship_list = []
        adult_dbs_list = []
        adult_permission_list = []
        children_list = ChildInHome.objects.filter(
            application_id=application_id_local).order_by('child')
        child_name_list = []
        child_birth_day_list = []
        child_birth_month_list = []
        child_birth_year_list = []
        child_relationship_list = []
        form = OtherPeopleSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        adult_table_list = []
        adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                          adult_relationship_list, adult_dbs_list, adult_permission_list)
        for adult in adults_list:
            if adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            elif adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            birth_date = ' '.join([str(adult.birth_day),calendar.month_name[adult.birth_month],str(adult.birth_year)])
            other_adult_fields = collections.OrderedDict([
                ('full_name', name),
                ('date_of_birth', birth_date),
                ('relationship', adult.relationship),
                ('dbs_certificate_number', adult.dbs_certificate_number),
                ('permission', adult.permission_declare)
            ])

            other_adult_table = collections.OrderedDict({
                'table_object': Table([adult.pk]),
                'fields': other_adult_fields,
                'title': name,
                'error_summary_title': ('There is something wrong with a persons details (' + name + ')')
            })
            adult_table_list.append(other_adult_table)
        back_link_addition = '&adults=' + str((len(adult_table_list))) + '&remove=0'
        for table in adult_table_list:
            table['other_people_numbers'] = back_link_addition
        adult_table_list = create_tables(adult_table_list, other_adult_name_dict, other_adult_link_dict)

        child_table_list = []
        for child in children_list:
            if child.middle_names != '':
                name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
            elif child.middle_names == '':
                name = child.first_name + ' ' + child.last_name
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
                'error_summary_title': ('There is something wrong with a persons details (' + name + ')')
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
            'error_summary_title': 'There is a problem with the adults in your home'
        })

        child_table = collections.OrderedDict({
            'table_object': Table([application_id_local]),
            'fields': {'children_in_home': children_in_home},
            'title': 'Children in your home',
            'error_summary_title': 'There is a problem with the children in your home'
        })

        adult_table = create_tables([adult_table], other_adult_summary_name_dict, other_adult_summary_link_dict)
        child_table = create_tables([child_table], other_child_summary_name_dict, other_child_summary_link_dict)

        table_list = adult_table + child_table + adult_table_list + child_table_list

        variables = {
            'page_title': 'Check your answers: people in your home',
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'turning_16': application.children_turning_16,
            'people_in_home_status': application.people_in_home_status
        }
        variables = submit_link_setter(variables, table_list, 'people_in_home', application_id_local)

        status.update(application_id_local,
                      'people_in_home_status', 'COMPLETED')
        return render(request, 'generic-summary-template.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleSummaryForm()
        if form.is_valid():
            status.update(application_id_local,
                          'people_in_home_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-summary.html', variables)
