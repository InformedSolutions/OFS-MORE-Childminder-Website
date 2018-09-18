import collections

from django.utils import timezone
import calendar

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from ..table_util import Table, create_tables, submit_link_setter
from ..summary_page_data import personal_details_name_dict, personal_details_link_dict
from .. import address_helper, status
from ..business_logic import (multiple_childcare_address_logic,
                              personal_dob_logic,
                              personal_location_of_care_logic,
                              personal_name_logic,
                              reset_declaration)
from ..forms import (PersonalDetailsChildcareAddressForm,
                     PersonalDetailsChildcareAddressLookupForm,
                     PersonalDetailsChildcareAddressManualForm,
                     PersonalDetailsDOBForm,
                     PersonalDetailsGuidanceForm,
                     PersonalDetailsHomeAddressForm,
                     PersonalDetailsHomeAddressLookupForm,
                     PersonalDetailsLocationOfCareForm,
                     PersonalDetailsNameForm,
                     PersonalDetailsOwnChildrenForm,
                     PersonalDetailsSummaryForm,
                     PersonalDetailsWorkingInOtherChildminderHomeForm)
from ..models import (ApplicantHomeAddress,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      Arc)


def personal_details_guidance(request):
    """
    Method returning the template for the Your personal details: guidance page (for a given application)
    and navigating to the Your login and contact details: name page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: guidance template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = PersonalDetailsGuidanceForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }

        return render(request, 'personal-details-guidance.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PersonalDetailsGuidanceForm(request.POST)

        if form.is_valid():
            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            return HttpResponseRedirect(reverse('Personal-Details-Name-View') + '?id=' + app_id)

        variables = {
            'form': form,
            'application_id': app_id
        }

        return render(request, 'personal-details-guidance.html', variables)


def personal_details_name(request):
    """
    Method returning the template for the Your personal details: name page (for a given application)
    and navigating to the Your personal details: date of birth page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: name template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = PersonalDetailsNameForm(id=app_id)
        form.check_flag()
        application = Application.get_id(app_id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }

        return render(request, 'personal-details-name.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PersonalDetailsNameForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.objects.get(pk=app_id)

        if form.is_valid():

            # Create or update Applicant_Names record
            applicant_names_record = personal_name_logic(application, form)
            applicant_names_record.save()
            application.date_updated = current_date
            application.save()
            if application.personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Personal-Details-DOB-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem with your name details'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'personal-details-name.html', variables)


def personal_details_dob(request):
    """
    Method returning the template for the Your personal details: date of birth page (for a given application)
    and navigating to the Your personal details: home address page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: date of birth template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = PersonalDetailsDOBForm(id=app_id)
        form.check_flag()
        application = Application.get_id(app_id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }

        return render(request, 'personal-details-dob.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PersonalDetailsDOBForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        if form.is_valid():
            if application.personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update Applicant_Personal_Details record
            personal_details_record = personal_dob_logic(app_id, form)
            personal_details_record.save()
            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(
                reverse('Personal-Details-Home-Address-View') + '?id=' + app_id + '&manual=False&lookup=False')

        else:

            form.error_summary_title = 'There was a problem with your date of birth'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'personal-details-dob.html', variables)


def personal_details_home_address(request):
    """
    Method returning the template for the Your personal details: home address page (for a given application)
    and navigating to the Your personal details: location of care page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsHomeAddressForm(id=app_id)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }

        return render(request, 'personal-details-home-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsHomeAddressForm(request.POST, id=app_id)
        form.remove_flag()
        if form.is_valid():

            postcode = form.cleaned_data.get('postcode')
            applicant = ApplicantPersonalDetails.get_id(app_id=app_id)
            if ApplicantHomeAddress.objects.filter(personal_detail_id=applicant,
                                                   current_address=True).count() == 0:

                home_address_record = ApplicantHomeAddress(street_line1='',
                                                           street_line2='',
                                                           town='',
                                                           county='',
                                                           country='',
                                                           postcode=postcode,
                                                           current_address=True,
                                                           childcare_address=None,
                                                           move_in_month=0,
                                                           move_in_year=0,
                                                           personal_detail_id=applicant,
                                                           application_id=application)
                home_address_record.save()

            elif ApplicantHomeAddress.objects.filter(personal_detail_id=applicant,
                                                     current_address=True).count() > 0:

                home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                       current_address=True)
                home_address_record.postcode = postcode
                home_address_record.save()

            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()

            if 'postcode-search' in request.POST:

                if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                    status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

                return HttpResponseRedirect(reverse('Personal-Details-Home-Address-Select-View') + '?id=' + app_id)

            if 'submit' in request.POST:
                return HttpResponseRedirect(reverse('Personal-Details-Home-Address-Manual-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem with your postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address.html', variables)


def personal_details_home_address_select(request):
    """
    Method returning the template for the Your personal details: select home address page (for a given application)
    and navigating to the Your personal details: location of care page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        applicant = ApplicantPersonalDetails.get_id(app_id=app_id)
        home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant, current_address=True)
        postcode = home_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

        if len(addresses) != 0:
            form = PersonalDetailsHomeAddressLookupForm(id=app_id, choices=addresses)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address-lookup.html', variables)

        else:
            form = PersonalDetailsHomeAddressForm(id=app_id)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        applicant = ApplicantPersonalDetails.get_id(app_id=app_id)
        home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant, current_address=True)
        postcode = home_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = PersonalDetailsHomeAddressLookupForm(request.POST, id=app_id, choices=addresses)

        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            personal_detail_record = ApplicantPersonalDetails.get_id(app_id=app_id)
            personal_detail_id = personal_detail_record.personal_detail_id

            # If the user entered information for this task for the first time
            if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id).count() == 0:

                home_address_record = ApplicantHomeAddress(street_line1=line1,
                                                           street_line2=line2,
                                                           town=town,
                                                           county='',
                                                           country='United Kingdom',
                                                           postcode=postcode,
                                                           childcare_address=None,
                                                           current_address=True,
                                                           move_in_month=0,
                                                           move_in_year=0,
                                                           personal_detail_id=personal_detail_record,
                                                           application_id=app_id)
                home_address_record.save()

            # If the user previously entered information for this task
            elif ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                                     current_address=True).count() > 0:

                home_address_record = ApplicantHomeAddress.objects.get(
                    personal_detail_id=personal_detail_id,
                    current_address=True)
                home_address_record.street_line1 = line1
                home_address_record.street_line2 = line2
                home_address_record.town = town
                home_address_record.postcode = postcode
                home_address_record.save()
            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()

            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('Personal-Details-Location-Of-Care-View') + '?id=' + app_id)
        else:

            form.error_summary_title = 'There was a problem finding your address'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address-lookup.html', variables)


def personal_details_location_of_care(request):
    """
    Method returning the template for the Your personal details: location of care page (for a given application)
    and navigating to the Your personal details: childcare or summary page when successfully completed.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: location of care template
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=app_id).personal_detail_id
        applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                  current_address=True)
        # Delete childcare address if it is marked the same as the home address
        multiple_childcare_address_logic(personal_detail_id)
        street_line1 = applicant_home_address.street_line1
        street_line2 = applicant_home_address.street_line2
        town = applicant_home_address.town
        county = applicant_home_address.county
        postcode = applicant_home_address.postcode
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsLocationOfCareForm(id=app_id)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-location-of-care.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(application_id=app_id).personal_detail_id
        form = PersonalDetailsLocationOfCareForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        if form.is_valid():
            # Reset status to in progress as question can change status of overall task
            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update home address record
            home_address_record = personal_location_of_care_logic(app_id, form)
            home_address_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # Delete childcare address if it is marked the same as the home address
            multiple_childcare_address_logic(personal_detail_id)

            if home_address_record.childcare_address:

                # Set working in other childminder home to false
                application.working_in_other_childminder_home = False
                application.date_updated = current_date
                application.save()
                return HttpResponseRedirect(reverse('Personal-Details-Summary-View') + '?id=' + app_id)

            else:

                return HttpResponseRedirect(reverse('Personal-Details-Childcare-Address-View') + '?id=' + app_id)
        else:

            form.error_summary_title = 'There was a problem with your address details'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            applicant_home_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                      current_address=True)
            street_line1 = applicant_home_address.street_line1
            street_line2 = applicant_home_address.street_line2
            town = applicant_home_address.town
            county = applicant_home_address.county
            postcode = applicant_home_address.postcode

            variables = {
                'form': form,
                'application_id': app_id,
                'street_line1': street_line1,
                'street_line2': street_line2,
                'town': town,
                'county': county,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-location-of-care.html', variables)


def personal_details_childcare_address(request):
    """
    Method returning the template for the Your personal details: childcare address page (for a given application)
    and navigating to the Your personal details: summary page when successfully completed.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: childcare template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsChildcareAddressForm(id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-childcare-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsChildcareAddressForm(request.POST, id=app_id)

        if form.is_valid():

            postcode = form.cleaned_data.get('postcode')
            applicant = ApplicantPersonalDetails.get_id(app_id=app_id)

            if ApplicantHomeAddress.objects.filter(personal_detail_id=applicant, childcare_address=True,
                                                   current_address=False).count() == 0:

                childcare_address_record = ApplicantHomeAddress(street_line1='',
                                                                street_line2='',
                                                                town='',
                                                                county='',
                                                                country='',
                                                                postcode=postcode,
                                                                current_address=False,
                                                                childcare_address=True,
                                                                move_in_month=0,
                                                                move_in_year=0,
                                                                personal_detail_id=applicant,
                                                                application_id=application)
                childcare_address_record.save()

            elif ApplicantHomeAddress.objects.filter(personal_detail_id=applicant, childcare_address=True,
                                                     current_address=False).count() > 0:

                childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                            childcare_address=True,
                                                                            current_address=False)
                childcare_address_record.postcode = postcode
                childcare_address_record.save()
            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()

            if 'postcode-search' in request.POST:

                if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                    status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

                return HttpResponseRedirect(reverse('Personal-Details-Childcare-Address-Select-View') + '?id=' + app_id)

            if 'submit' in request.POST:

                if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                    status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

                return HttpResponseRedirect(reverse('Personal-Details-Childcare-Address-Manual-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem with the postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address.html', variables)


def personal_details_childcare_address_select(request):
    """
    Method returning the template for the Your personal details: select childcare address page (for a given
    application) and navigating to the Your personal details: location of care page when successfully completed;
    business logic is applied to either create or update the associated Applicant_Name record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: childcare address template
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        applicant = ApplicantPersonalDetails.get_id(app_id=app_id)
        childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                    childcare_address=True)
        postcode = childcare_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

        if len(addresses) != 0:
            form = PersonalDetailsChildcareAddressLookupForm(id=app_id, choices=addresses)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address-lookup.html', variables)

        else:
            form = PersonalDetailsChildcareAddressForm(id=app_id)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        applicant = ApplicantPersonalDetails.get_id(app_id=app_id)
        childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                    childcare_address=True)
        postcode = childcare_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = PersonalDetailsChildcareAddressLookupForm(request.POST, id=app_id, choices=addresses)

        if form.is_valid():

            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            personal_detail_record = ApplicantPersonalDetails.objects.get(
                application_id=app_id)
            personal_detail_id = personal_detail_record.personal_detail_id
            # If the user entered information for this task for the first time
            if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id).count() == 0:

                childcare_address_record = ApplicantHomeAddress(street_line1=line1,
                                                                street_line2=line2,
                                                                town=town,
                                                                county='',
                                                                country='United Kingdom',
                                                                postcode=postcode,
                                                                childcare_address=True,
                                                                current_address=False,
                                                                move_in_month=0,
                                                                move_in_year=0,
                                                                personal_detail_id=personal_detail_record,
                                                                application_id=app_id)
                childcare_address_record.save()

            # If the user previously entered information for this task
            elif ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id,
                                                     childcare_address=True).count() > 0:

                childcare_address_record = ApplicantHomeAddress.objects.get(
                    personal_detail_id=personal_detail_id,
                    childcare_address=True)
                childcare_address_record.street_line1 = line1
                childcare_address_record.street_line2 = line2
                childcare_address_record.town = town
                childcare_address_record.postcode = postcode
                childcare_address_record.save()
            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()

            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            return HttpResponseRedirect(reverse('Personal-Details-Childcare-Address-Details-View') + '?id=' + app_id)
        else:

            form.error_summary_title = 'There was a problem finding your address'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address-lookup.html', variables)


def personal_details_childcare_address_manual(request):
    """
    Method returning the template for the Your personal details: childcare address manual page (for a given application)
    and navigating to the Your personal details: summary page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: childcare template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsChildcareAddressManualForm(id=app_id)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-childcare-address-manual.html', variables)
    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsChildcareAddressManualForm(request.POST, id=app_id)
        form.remove_flag()

        if form.is_valid():

            street_line1 = form.cleaned_data.get('street_line1')
            street_line2 = form.cleaned_data.get('street_line2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            applicant = ApplicantPersonalDetails.objects.get(
                application_id=app_id)

            if ApplicantHomeAddress.objects.filter(personal_detail_id=applicant, childcare_address=True,
                                                   current_address=False).count() == 0:
                childcare_address_record = ApplicantHomeAddress(street_line1=street_line1,
                                                                street_line2=street_line2,
                                                                town=town,
                                                                county=county,
                                                                postcode=postcode,
                                                                current_address=False,
                                                                childcare_address=True,
                                                                move_in_month=0,
                                                                move_in_year=0,
                                                                personal_detail_id=applicant,
                                                                application_id=application)
                childcare_address_record.save()

            elif ApplicantHomeAddress.objects.filter(personal_detail_id=applicant, childcare_address=True,
                                                     current_address=False).count() > 0:
                childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                            childcare_address=True,
                                                                            current_address=False)
                childcare_address_record.street_line1 = street_line1
                childcare_address_record.street_line2 = street_line2
                childcare_address_record.town = town
                childcare_address_record.county = county
                childcare_address_record.postcode = postcode
                childcare_address_record.save()
            application = Application.get_id(app_id=app_id)
            application.date_updated = current_date
            application.save()

            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')
            reset_declaration(application)
            return HttpResponseRedirect(reverse('Personal-Details-Childcare-Address-Details-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem with your address'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address-manual.html', variables)


def personal_details_working_in_other_childminder_home(request):
    """
    Method returning the template for the Your personal details: your childcare address details page (for a given
    application) and navigating to the Your personal details: your own children page when successfully completed.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: your childcare address details template
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(application_id=app_id).personal_detail_id
        applicant_childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                       childcare_address=True)
        street_line1 = applicant_childcare_address.street_line1
        street_line2 = applicant_childcare_address.street_line2
        town = applicant_childcare_address.town
        county = applicant_childcare_address.county
        postcode = applicant_childcare_address.postcode
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsWorkingInOtherChildminderHomeForm(id=app_id)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-childcare-address-details.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PersonalDetailsWorkingInOtherChildminderHomeForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        if form.is_valid():
            # Reset status to in progress as question can change status of overall task
            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update Application record
            working_in_other_childminder_home = form.cleaned_data.get('working_in_other_childminder_home')

            if working_in_other_childminder_home == 'True':
                application.working_in_other_childminder_home = True
            elif working_in_other_childminder_home == 'False':
                application.working_in_other_childminder_home = False
            application.save()

            # Set People in your home task status to Completed when the applicant works in another childminder's home
            if application.working_in_other_childminder_home is True:
                application.people_in_home_status = 'NOT_STARTED'

                # Reset ARC status if there are comments
                if Arc.objects.filter(application_id=app_id).count() > 0:

                    arc = Arc.objects.get(application_id=app_id)

                    if arc.people_in_home_review != 'FLAGGED':
                        arc.people_in_home_review = 'NOT_STARTED'
            else:
                application.people_in_home_status = 'COMPLETED'

                if Arc.objects.filter(application_id=app_id).count() > 0:
                    arc = Arc.objects.get(application_id=app_id)
                    arc.people_in_home_review = 'COMPLETED'

            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Personal-Details-Your-Own-Children-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            personal_detail_id = ApplicantPersonalDetails.objects.get(application_id=app_id).personal_detail_id
            applicant_childcare_address = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                           childcare_address=True)
            street_line1 = applicant_childcare_address.street_line1
            street_line2 = applicant_childcare_address.street_line2
            town = applicant_childcare_address.town
            county = applicant_childcare_address.county
            postcode = applicant_childcare_address.postcode

            variables = {
                'form': form,
                'application_id': app_id,
                'street_line1': street_line1,
                'street_line2': street_line2,
                'town': town,
                'county': county,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address-details.html', variables)


def personal_details_own_children(request):
    """
    Method returning the template for the Your personal details: your own children page (for a given
    application) and navigating to the Your personal details: check your answers page when successfully completed.
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: your own children template
    """

    current_date = timezone.now()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.get_id(app_id=app_id)
        form = PersonalDetailsOwnChildrenForm(id=app_id)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-your-own-children.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = PersonalDetailsOwnChildrenForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        if form.is_valid():
            # Reset status to in progress as question can change status of overall task
            if Application.get_id(app_id=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update Application record
            own_children = form.cleaned_data.get('own_children')
            
            if own_children == 'True':
                application.own_children = True
            elif own_children == 'False':
                application.own_children = False
            application.save()

            # Set Your children task status to Completed when the applicant has no own children
            if application.own_children is True:
                application.your_children_status = 'NOT_STARTED'

                # Reset ARC status if there are comments
                if Arc.objects.filter(application_id=app_id).count() > 0:

                    arc = Arc.objects.get(application_id=app_id)

                    if arc.your_children_review != 'FLAGGED':
                        arc.your_children_review = 'NOT_STARTED'
            else:
                application.your_children_status = 'COMPLETED'

                if Arc.objects.filter(application_id=app_id).count() > 0:

                    arc = Arc.objects.get(application_id=app_id)
                    arc.your_children_review = 'COMPLETED'

            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Personal-Details-Summary-View') + '?id=' + app_id)

        else:

            form.error_summary_title = 'There was a problem on this page'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-your-own-children.html', variables)


def personal_details_summary(request):
    """
    Method returning the template for the Your personal details: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: summary template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        application = Application.objects.get(application_id=app_id)
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id=app_id)
        birth_day = personal_detail_id.birth_day
        birth_month = personal_detail_id.birth_month
        birth_year = personal_detail_id.birth_year
        applicant_name_record = ApplicantName.get_id(app_id=app_id)
        first_name = applicant_name_record.first_name
        middle_names = applicant_name_record.middle_names
        last_name = applicant_name_record.last_name
        applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                         current_address=True)
        applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                              childcare_address=True)
        street_line1 = applicant_home_address_record.street_line1
        street_line2 = applicant_home_address_record.street_line2
        town = applicant_home_address_record.town
        county = applicant_home_address_record.county
        postcode = applicant_home_address_record.postcode
        location_of_childcare = applicant_home_address_record.childcare_address

        childcare_street_line1 = applicant_childcare_address_record.street_line1
        childcare_street_line2 = applicant_childcare_address_record.street_line2
        childcare_town = applicant_childcare_address_record.town
        childcare_county = applicant_childcare_address_record.county
        childcare_postcode = applicant_childcare_address_record.postcode

        if location_of_childcare:
            childcare_address = 'Same as home address'
        else:
            childcare_address = ' '.join(
                [childcare_street_line1, (childcare_street_line2 or ''), childcare_town, (childcare_county or ''),
                 childcare_postcode])

        if application.working_in_other_childminder_home:
            working_in_other_childminder_home = 'Yes'
        else:
            working_in_other_childminder_home = 'No'

        if application.own_children:
            own_children = 'Yes'
        else:
            own_children = 'No'

        name_dob_table_dict = collections.OrderedDict([
            ('name', ' '.join([first_name, (middle_names or ''), last_name])),
            ('date_of_birth', ' '.join([str(birth_day), calendar.month_name[birth_month], str(birth_year)]))
        ])

        home_address = ' '.join([street_line1, (street_line2 or ''), town, (county or ''), postcode])

        address_table_dict = collections.OrderedDict([
            ('home_address', home_address),
            ('childcare_address', childcare_address),
            ('working_in_other_childminder_home', working_in_other_childminder_home)
        ])

        own_children_table_dict = collections.OrderedDict([
            ('own_children', own_children)
        ])

        name_dob_dict = collections.OrderedDict({
            'table_object': Table([personal_detail_id.pk, applicant_name_record.pk]),
            'fields': name_dob_table_dict,
            'title': 'Your name and date of birth',
            'error_summary_title': 'There was a problem'
        })

        address_dict = collections.OrderedDict({
            'table_object': Table(
                [applicant_home_address_record.pk, getattr(applicant_childcare_address_record, 'pk', None),
                 application.pk]),
            'fields': address_table_dict,
            'title': 'Your home and childcare address',
            'error_summary_title': 'There was a problem'
        })

        own_children_dict = collections.OrderedDict({
            'table_object': Table([application.pk]),
            'fields': own_children_table_dict,
            'title': 'Your children',
            'error_summary_title': 'There was a problem'
        })

        tables = [name_dob_dict, address_dict, own_children_dict]
        table_list = create_tables(tables, personal_details_name_dict, personal_details_link_dict)

        form = PersonalDetailsSummaryForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'table_list': table_list,
            'page_title': 'Check your answers: personal details',
            'personal_details_status': application.personal_details_status
        }
        variables = submit_link_setter(variables, table_list, 'personal_details', app_id)

        return render(request, 'generic-summary-template.html', variables)

    if request.method == 'POST':
        app_id = request.POST["id"]

        application = Application.objects.get(application_id=app_id)
        personal_detail_id = ApplicantPersonalDetails.get_id(app_id=app_id)
        birth_day = personal_detail_id.birth_day
        birth_month = personal_detail_id.birth_month
        birth_year = personal_detail_id.birth_year
        applicant_name_record = ApplicantName.get_id(app_id=app_id)
        first_name = applicant_name_record.first_name
        middle_names = applicant_name_record.middle_names
        last_name = applicant_name_record.last_name
        applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                         current_address=True)
        applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                              childcare_address=True)
        street_line1 = applicant_home_address_record.street_line1
        street_line2 = applicant_home_address_record.street_line2
        town = applicant_home_address_record.town
        county = applicant_home_address_record.county
        postcode = applicant_home_address_record.postcode
        location_of_childcare = applicant_home_address_record.childcare_address

        childcare_street_line1 = applicant_childcare_address_record.street_line1
        childcare_street_line2 = applicant_childcare_address_record.street_line2
        childcare_town = applicant_childcare_address_record.town
        childcare_county = applicant_childcare_address_record.county
        childcare_postcode = applicant_childcare_address_record.postcode

        if location_of_childcare:
            childcare_address = 'Same as home address'
        else:
            childcare_address = ' '.join(
                [childcare_street_line1, (childcare_street_line2 or ''), childcare_town, (childcare_county or ''),
                 childcare_postcode])

        if application.working_in_other_childminder_home:
            working_in_other_childminder_home = 'Yes'
        else:
            working_in_other_childminder_home = 'No'

        if application.own_children:
            own_children = 'Yes'
        else:
            own_children = 'No'

        name_dob_table_dict = collections.OrderedDict([
            ('name', ' '.join([first_name, (middle_names or ''), last_name])),
            ('date_of_birth', ' '.join([str(birth_day), calendar.month_name[birth_month], str(birth_year)]))
        ])

        home_address = ' '.join([street_line1, (street_line2 or ''), town, (county or ''), postcode])

        address_table_dict = collections.OrderedDict([
            ('home_address', home_address),
            ('childcare_address', childcare_address),
            ('working_in_other_childminder_home', working_in_other_childminder_home)
        ])

        own_children_table_dict = collections.OrderedDict([
            ('own_children', own_children)
        ])

        name_dob_dict = collections.OrderedDict({
            'table_object': Table([personal_detail_id.pk, applicant_name_record.pk]),
            'fields': name_dob_table_dict,
            'title': 'Your name and date of birth',
            'error_summary_title': 'There was a problem'
        })

        address_dict = collections.OrderedDict({
            'table_object': Table(
                [applicant_home_address_record.pk, getattr(applicant_childcare_address_record, 'pk', None),
                 application.pk]),
            'fields': address_table_dict,
            'title': 'Your home and childcare address',
            'error_summary_title': 'There was a problem'
        })

        own_children_dict = collections.OrderedDict({
            'table_object': Table([application.pk]),
            'fields': own_children_table_dict,
            'title': 'Your children',
            'error_summary_title': 'There was a problem'
        })

        tables = [name_dob_dict, address_dict, own_children_dict]
        table_list = create_tables(tables, personal_details_name_dict, personal_details_link_dict)

        form = PersonalDetailsSummaryForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'table_list': table_list,
            'page_title': 'Check your answers: your personal details',
            'personal_details_status': application.personal_details_status
        }
        variables = submit_link_setter(variables, table_list, 'personal_details', app_id)

        if not sum([table.get_error_amount() for table in variables['table_list']]):  # If no errors found.
            status.update(app_id, 'personal_details_status', 'COMPLETED')

        return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + app_id)
