from datetime import date

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic import View

from application.business_logic import (
    other_people_children_details_logic,
    rearrange_children_in_home,
    remove_child_in_home,
    reset_declaration,
)
from application.forms import OtherPeopleChildrenDetailsForm
from application.models import Application, ApplicantHomeAddress, AdultInHome


class PITHChildrenDetailsView(View):
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
            number_of_children = 1   # Set the number of children to 1 to initialise one instance of the form

        if number_of_children == 1:
            remove_button = False    # Disable the remove person button

        remove_child_in_home(application_id_local, remove_person)
        rearrange_children_in_home(number_of_children, application_id_local)

        form_list = [OtherPeopleChildrenDetailsForm(id=application_id_local, child=i, prefix=i) for i in range(1, number_of_children + 1)]

        if application.application_status == 'FURTHER_INFORMATION':
            for index, form in enumerate(form_list):
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = "There was a problem with Child {0}'s details".format(str(index + 1))
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

    def post(self, request):
        current_date = timezone.now()
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)

        number_of_children = int(request.POST["children"])
        remove_button = True

        if number_of_children == 0:  # If there are no children in the database
            number_of_children = 1   # Set the number of children to 1 to initialise one instance of the form

        if number_of_children == 1:
            remove_button = False  # Disable the remove person button

        form_list   = []
        forms_valid = True           # Bool indicating whether or not all the forms are valid
        children_turning_16 = False  # Bool indicating whether or not all any children are turning 16

        for i in range(1, int(number_of_children) + 1):
            form = OtherPeopleChildrenDetailsForm(request.POST, id=application_id_local, child=i, prefix=i)
            form.remove_flag()
            form.error_summary_title = 'There was a problem with Child {0}\'s details'.format(str(i))
            form_list.append(form)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'

            if form.is_valid():
                child_record = other_people_children_details_logic(application_id_local, form, i)
                child_record.save()
                reset_declaration(application)

                # Calculate child's age
                birth_day, birth_month, birth_year = form.cleaned_data.get('date_of_birth')
                applicant_dob = date(birth_year, birth_month, birth_day)
                today = date.today()

                age = today.year - applicant_dob.year - ((today.month, today.day) < (applicant_dob.month, applicant_dob.day))
                if 15 <= age < 16:
                    children_turning_16 = True

            else:
                forms_valid = False

        if 'submit' in request.POST:
            # If all forms are valid
            if forms_valid:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                }

                success_url = self.get_success_url(children_turning_16, application)
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                return HttpResponseRedirect(reverse(success_url) + '?id=' + application_id_local, variables)

            # If there is an invalid form
            else:
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
            if forms_valid:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }

                add_child = int(number_of_children) + 1
                add_child_string = str(add_child)

                # Redirect to self.get(), it seems.
                return HttpResponseRedirect(reverse('PITH-Children-Details-View') + \
                                            '?id=' + application_id_local + \
                                            '&children=' + add_child_string + \
                                            '&remove=0#person' + add_child_string,
                                            variables)

            # If there is an invalid form
            else:
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


    def get_success_url(self, children_turning_16, application):
        """
        Function containing logic for determining success_url.

        :param: children_turning_16: bool indicating whether or not any children were turning 16.
        :param: application: application object for the applicant.
        :return: reversible string for redirect target page.
        """
        adults = AdultInHome.objects.filter(application_id=application.pk)

        if children_turning_16:
            application.children_turning_16 = True
            success_url = 'PITH-Approaching-16-View'
        else:
            application.children_turning_16 = False

            home_address = ApplicantHomeAddress.objects.get(application_id=application.pk, current_address=True)
            childcare_address = ApplicantHomeAddress.objects.get(application_id=application.pk, childcare_address=True)

            if home_address == childcare_address:
                success_url = 'PITH-Own-Children-Check-View'
            else:
                if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                    success_url = 'Task-List-View'
                else:
                    success_url = 'PITH-Summary-View'

        application.save()

        return success_url