"""
Method returning the template for the Your personal details: guidance page (for a given application)
and navigating to the Your login and contact details: name page when successfully completed
"""

import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

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
                     PersonalDetailsSummaryForm)
from ..models import (ApplicantHomeAddress,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application)


def personal_details_guidance(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: guidance template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = PersonalDetailsGuidanceForm()
        application = Application.objects.get(pk=app_id)
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
            if Application.objects.get(pk=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/your-name?id=' + app_id)

        variables = {
            'form': form,
            'application_id': app_id
        }

        return render(request, 'personal-details-guidance.html', variables)


"""
Method returning the template for the Your personal details: name page (for a given application)
and navigating to the Your personal details: date of birth page when successfully completed;
business logic is applied to either create or update the associated Applicant_Name record
"""


def personal_details_name(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: name template
    """

    current_date = datetime.datetime.today()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = PersonalDetailsNameForm(id=app_id)
        form.check_flag()
        application = Application.objects.get(pk=app_id)
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
            if application.personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Create or update Applicant_Names record
            applicant_names_record = personal_name_logic(app_id, form)
            applicant_names_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(
                settings.URL_PREFIX + '/personal-details/your-date-of-birth/?id=' + app_id)

        else:
            form.error_summary_title = 'There was a problem with your name details'
            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'personal-details-name.html', variables)


"""
Method returning the template for the Your personal details: date of birth page (for a given application)
and navigating to the Your personal details: home address page when successfully completed;
"""


def personal_details_dob(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: date of birth template
    """

    current_date = datetime.datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = PersonalDetailsDOBForm(id=app_id)
        form.check_flag()
        application = Application.objects.get(pk=app_id)
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
        application = Application.objects.get(pk=app_id)
        if form.is_valid():
            if application.personal_details_status != 'COMPLETED':
                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update Applicant_Personal_Details record
            personal_details_record = personal_dob_logic(app_id, form)
            personal_details_record.save()
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(
                settings.URL_PREFIX + '/personal-details/your-home-address?id=' + app_id +
                '&manual=False&lookup=False')
        else:
            form.error_summary_title = 'There was a problem with your date of birth'
            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'personal-details-dob.html', variables)


"""
Method returning the template for the Your personal details: home address page (for a given application)
and navigating to the Your personal details: location of care page when successfully completed;
business logic is applied to either create or update the associated Applicant_Name record
"""


def personal_details_home_address(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """

    current_date = datetime.datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsHomeAddressForm(id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }

        return render(request, 'personal-details-home-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsHomeAddressForm(request.POST, id=app_id)
        if form.is_valid():

            postcode = form.cleaned_data.get('postcode')
            applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
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
                                                           personal_detail_id=applicant)
                home_address_record.save()

            elif ApplicantHomeAddress.objects.filter(personal_detail_id=applicant,
                                                     current_address=True).count() > 0:

                home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                       current_address=True)
                home_address_record.postcode = postcode
                home_address_record.save()

            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()

            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/select-home-address/?id=' + app_id)

            if 'submit' in request.POST:
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/enter-home-address/?id=' + app_id)

        else:
            form.error_summary_title = 'There was a problem with your postcode'
            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address.html', variables)


"""
Method returning the template for the Your personal details: select home address page (for a given application)
and navigating to the Your personal details: location of care page when successfully completed;
business logic is applied to either create or update the associated Applicant_Name record
"""


def personal_details_home_address_select(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """

    current_date = datetime.datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
        home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant, current_address=True)
        postcode = home_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

        if len(addresses) != 0:
            form = PersonalDetailsHomeAddressLookupForm(id=app_id, choices=addresses)
            variables = {
                'form': form,
                'application_id': app_id,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address-lookup.html', variables)

        else:
            form = PersonalDetailsHomeAddressForm(id=app_id)
            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
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
            personal_detail_record = ApplicantPersonalDetails.objects.get(application_id=app_id)
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
                                                           personal_detail_id=personal_detail_record)
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
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()

            if Application.objects.get(pk=app_id).personal_details_status != 'COMPLETED':

                status.update(app_id, 'personal_details_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/home-address-details?id=' +
                                        app_id)
        else:
            form.error_summary_title = 'There was a problem finding your address'
            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-home-address-lookup.html', variables)

"""
Method returning the template for the Your personal details: location of care page (for a given application)
and navigating to the Your personal details: childcare or summary page when successfully completed;
"""

def personal_details_location_of_care(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: location of care template
    """

    current_date = datetime.datetime.today()

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
        application = Application.objects.get(pk=app_id)

        if application.login_details_status != 'COMPLETED':

            status.update(app_id, 'login_details_status', 'COMPLETED')
        form = PersonalDetailsLocationOfCareForm(id=app_id)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': app_id,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'personal_details_status': application.login_details_status
        }
        return render(request, 'personal-details-location-of-care.html', variables)

    if request.method == 'POST':
        app_id = request.POST["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=app_id).personal_detail_id
        form = PersonalDetailsLocationOfCareForm(request.POST, id=app_id)
        form.remove_flag()

        if form.is_valid():
            # Reset status to in progress as question can change status of overall task
            status.update(app_id, 'personal_details_status', 'IN_PROGRESS')

            # Update home address record
            home_address_record = personal_location_of_care_logic(app_id, form)
            home_address_record.save()
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # Delete childcare address if it is marked the same as the home address
            multiple_childcare_address_logic(personal_detail_id)

            if home_address_record.childcare_address == 'True':

                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/personal-details/check-answers?id=' + app_id)

            elif home_address_record.childcare_address == 'False':

                return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/childcare-address?id=' +
                                            app_id + '&manual=False&lookup=False')
        else:
            form.error_summary_title = 'There was a problem with your address details'
            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'personal-details-location-of-care.html', variables)

"""
Method returning the template for the Your personal details: childcare address page (for a given application)
and navigating to the Your personal details: summary page when successfully completed;
"""
def personal_details_childcare_address(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: childcare template
    """

    current_date = datetime.datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsChildcareAddressForm(id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-childcare-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsChildcareAddressForm(request.POST, id=app_id)
        if form.is_valid():

            postcode = form.cleaned_data.get('postcode')
            applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
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
                                                                personal_detail_id=applicant)
                childcare_address_record.save()

            elif ApplicantHomeAddress.objects.filter(personal_detail_id=applicant, childcare_address=True,
                                                     current_address=False).count() > 0:

                childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                            childcare_address=True,
                                                                            current_address=False)
                childcare_address_record.postcode = postcode
                childcare_address_record.save()
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()

            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/select-childcare-address/?id='
                                            + app_id)

            if 'submit' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/enter-childcare-address/?id='
                                            + app_id)

        else:
            form.error_summary_title = 'There was a problem with your postcode'
            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address.html', variables)

"""
Method returning the template for the Your personal details: select childcare address page (for a given
application) and navigating to the Your personal details: location of care page when successfully completed;
business logic is applied to either create or update the associated Applicant_Name record
"""


def personal_details_childcare_address_select(request):
    """
        :param request: a request object used to generate the HttpResponse
        :return: an HttpResponse object with the rendered Your personal details: childcare address template
        """

    current_date = datetime.datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
        childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=applicant,
                                                                    childcare_address=True)
        postcode = childcare_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

        if len(addresses) != 0:

            form = PersonalDetailsChildcareAddressLookupForm(id=app_id, choices=addresses)
            variables = {
                'form': form,
                'application_id': app_id,
                'postcode': postcode,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address-lookup.html', variables)

        else:
            form = PersonalDetailsChildcareAddressForm(id=app_id)
            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }

            return render(request, 'personal-details-childcare-address.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        applicant = ApplicantPersonalDetails.objects.get(application_id=app_id)
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
                                                                personal_detail_id=personal_detail_record)
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
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()

            if Application.objects.get(pk=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id,
                              'personal_details_status', 'IN_PROGRESS')

            return HttpResponseRedirect(settings.URL_PREFIX + '/personal-details/check-answers?id=' +
                                        app_id)
        else:
            form.error_summary_title = 'There was a problem finding your address'
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
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        app_id = request.GET["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsChildcareAddressManualForm(id=app_id)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': app_id,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-childcare-address-manual.html', variables)
    if request.method == 'POST':
        app_id = request.POST["id"]
        application = Application.objects.get(pk=app_id)
        form = PersonalDetailsChildcareAddressManualForm(request.POST, id=app_id)
        form.remove_flag()
        if form.is_valid():
            street_line1 = form.cleaned_data.get('street_name_and_number')
            street_line2 = form.cleaned_data.get('street_name_and_number2')
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
                                                                personal_detail_id=applicant)
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
            application = Application.objects.get(pk=app_id)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=app_id).personal_details_status != 'COMPLETED':
                status.update(app_id,
                              'personal_details_status', 'IN_PROGRESS')
            reset_declaration(application)
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/personal-details/check-answers?id=' + app_id)
        else:
            form.error_summary_title = 'There was a problem with your address'
            variables = {
                'form': form,
                'application_id': app_id,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-childcare-address-manual.html', variables)


def personal_details_summary(request):
    """
    Method returning the template for the Your personal details: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: summary template
    """
    if request.method == 'GET':
        app_id = request.GET["id"]
        personal_detail_id = ApplicantPersonalDetails.objects.get(
            application_id=app_id)
        birth_day = personal_detail_id.birth_day
        birth_month = personal_detail_id.birth_month
        birth_year = personal_detail_id.birth_year
        applicant_name_record = ApplicantName.objects.get(
            personal_detail_id=personal_detail_id)
        first_name = applicant_name_record.first_name
        middle_names = applicant_name_record.middle_names
        last_name = applicant_name_record.last_name
        applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                         current_address=True)
        street_line1 = applicant_home_address_record.street_line1
        street_line2 = applicant_home_address_record.street_line2
        town = applicant_home_address_record.town
        county = applicant_home_address_record.county
        postcode = applicant_home_address_record.postcode
        location_of_childcare = applicant_home_address_record.childcare_address
        applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                              childcare_address=True)
        childcare_street_line1 = applicant_childcare_address_record.street_line1
        childcare_street_line2 = applicant_childcare_address_record.street_line2
        childcare_town = applicant_childcare_address_record.town
        childcare_county = applicant_childcare_address_record.county
        childcare_postcode = applicant_childcare_address_record.postcode
        form = PersonalDetailsSummaryForm()
        application = Application.objects.get(pk=app_id)
        status.update(app_id,
                      'personal_details_status', 'COMPLETED')
        variables = {
            'form': form,
            'application_id': app_id,
            'first_name': first_name,
            'middle_names': middle_names,
            'last_name': last_name,
            'birth_day': birth_day,
            'birth_month': birth_month,
            'birth_year': birth_year,
            'street_line1': street_line1,
            'street_line2': street_line2,
            'town': town,
            'county': county,
            'postcode': postcode,
            'location_of_childcare': location_of_childcare,
            'childcare_street_line1': childcare_street_line1,
            'childcare_street_line2': childcare_street_line2,
            'childcare_town': childcare_town,
            'childcare_county': childcare_county,
            'childcare_postcode': childcare_postcode,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-summary.html', variables)
    if request.method == 'POST':
        app_id = request.POST["id"]
        form = PersonalDetailsSummaryForm()
        if form.is_valid():
            status.update(app_id,
                          'personal_details_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + app_id)
        else:
            variables = {
                'form': form,
                'application_id': app_id
            }
            return render(request, 'personal-details-summary.html', variables)