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
            number_of_children = 1   # Set the number of children to 1 to initialise one instance of the form

        if number_of_children == 1:
            remove_button = False    # Disable the remove person button

        remove_child(application_id_local, remove_person)
        rearrange_children(number_of_children, application_id_local)

        form_list = [PITHOwnChildrenDetailsForm(id=application_id_local, child=i, prefix=i) for i in range(1, number_of_children + 1)]

        if application.application_status == 'FURTHER_INFORMATION':
            for index, form in enumerate(form_list):
                if form.pk != '':  # If there are no children in the database yet, there will be no pk for the child.
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

        return render(request, 'PITH_templates/PITH_own_children_details.html', variables)

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
            form = PITHOwnChildrenDetailsForm(request.POST, id=application_id_local, child=i, prefix=i)
            form.error_summary_title = 'There was a problem with Child {0}\'s details'.format(str(i))

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.remove_flag()

            form_list.append(form)

            if form.is_valid():
                child_record = PITH_own_children_details_logic(application_id_local, form, i)
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

                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                return HttpResponseRedirect(build_url('PITH-Own-Children-Postcode-View', get={'id': application_id_local,
                                                                                              'children': 1}))

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
                return render(request, 'PITH_templates/PITH_own_children_details.html', variables)

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
                return HttpResponseRedirect(reverse('PITH-Own-Children-Details-View') + \
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
                return render(request, 'PITH_templates/PITH_own_children_details.html', variables)