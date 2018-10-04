import logging

from datetime import date

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic import View

from application.business_logic import (
    PITH_own_children_details_logic,
    rearrange_children,
    remove_child,
    reset_declaration,
)
from application.forms.PITH_forms.PITH_own_children_details_form import PITHOwnChildrenDetailsForm
from application.models import Application, ApplicantHomeAddress, AdultInHome
from application.utils import build_url

# Initiate logging
log = logging.getLogger('')


class PITHOwnChildrenDetailsView(View):
    """
    Class containing the methods responsible for handling requests to the 'Children-In-The-Home-Details' page.
    """

    def get(self, request):

        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)

        number_of_children = int(request.GET["children"])
        remove_person = int(request.GET["remove"])
        remove_button = True

        if number_of_children == 0:  # If there are no children in the database

            number_of_children = 1  # Set the number of children to 1 to initialise one instance of the form
            log.debug('Number of children set to 1 to initialise one instance of the form')

        if number_of_children == 1:
            remove_button = False  # Disable the remove person button
            log.debug('Remove button disabled')

        remove_child(application_id_local, remove_person)
        log.debug('Child ' + str(remove_person) + ' removed')
        rearrange_children(number_of_children, application_id_local)
        log.debug('Children rearranged')

        form_list = [PITHOwnChildrenDetailsForm(id=application_id_local, child=i, prefix=i) for i in
                     range(1, number_of_children + 1)]
        log.debug('List of own children not in the home generated')

        if application.application_status == 'FURTHER_INFORMATION':

            for index, form in enumerate(form_list):

                if form.pk != '':  # If there are no children in the database yet, there will be no pk for the child.

                    form.error_summary_template_name = 'returned-error-summary.html'
                    form.error_summary_title = "There was a problem with Child {0}'s details".format(str(index + 1))
                    form.check_flag()

                    log.debug('Error summary set up')

        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'add_child': number_of_children + 1,
            'remove_button': remove_button,
            'remove_child': number_of_children - 1,
            'people_in_home_status': application.people_in_home_status
        }

        return render(request, 'PITH_templates/PITH_own_children_details.html', variables)

    def post(self, request):

        current_date = timezone.now()
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)

        number_of_children = int(request.POST["children"])
        remove_button = True

        if number_of_children == 0:  # If there are no children in the database

            number_of_children = 1  # Set the number of children to 1 to initialise one instance of the form
            log.debug('Number of children set to 1 to initialise one instance of the form')

        if number_of_children == 1:
            remove_button = False  # Disable the remove person button
            log.debug('Remove button disabled')

        form_list = []
        forms_valid = True  # Bool indicating whether or not all the forms are valid
        children_turning_16 = False  # Bool indicating whether or not all any children are turning 16

        for i in range(1, int(number_of_children) + 1):

            form = PITHOwnChildrenDetailsForm(request.POST, id=application_id_local, child=i, prefix=i)
            form.error_summary_title = 'There was a problem with Child {0}\'s details'.format(str(i))
            log.debug('Form initialised for child ' + str(i))

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.remove_flag()
                log.debug('Returned error summary template set up')

            form_list.append(form)

            if form.is_valid():

                child_record = PITH_own_children_details_logic(application_id_local, form, i)
                child_record.save()
                log.debug('Child ' + str(i) + ' record saved to database')
                reset_declaration(application)
                log.debug('Declaration status reset')

                # Calculate child's age
                birth_day, birth_month, birth_year = form.cleaned_data.get('date_of_birth')
                applicant_dob = date(birth_year, birth_month, birth_day)
                today = date.today()

                age = today.year - applicant_dob.year - (
                        (today.month, today.day) < (applicant_dob.month, applicant_dob.day))
                log.debug('Child ' + str(i) + 'age calculated:' + str(age))

                if 15 <= age < 16:
                    children_turning_16 = True
                    log.debug('Child is approaching 16')

            else:

                forms_valid = False
                log.debug('Form for child ' + str(i) + ' invalid')

        if 'submit' in request.POST:
            # If all forms are valid
            if forms_valid:

                log.debug('All forms valid')

                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                }

                application.date_updated = current_date
                application.save()
                log.debug('Update date updated for application: ' + application_id_local)
                reset_declaration(application)
                log.debug('Declaration status reset')
                return HttpResponseRedirect(
                    build_url('PITH-Own-Children-Postcode-View', get={'id': application_id_local,
                                                                      'children': 1}))

            # If there is an invalid form
            else:

                log.debug('Forms invalid')

                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }

                return render(request, 'PITH_templates/PITH_own_children_details.html', variables)

        if 'add_child' in request.POST:

            # If all forms are valid
            if forms_valid:

                log.debug('All forms valid')

                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }

                add_child = int(number_of_children) + 1
                add_child_string = str(add_child)

                log.debug('Generate URL to add child')

                # Redirect to self.get(), it seems.
                return HttpResponseRedirect(reverse('PITH-Own-Children-Details-View') + \
                                            '?id=' + application_id_local + \
                                            '&children=' + add_child_string + \
                                            '&remove=0#person' + add_child_string,
                                            variables)

            # If there is an invalid form
            else:

                log.debug('Forms invalid')

                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }

                return render(request, 'PITH_templates/PITH_own_children_details.html', variables)
