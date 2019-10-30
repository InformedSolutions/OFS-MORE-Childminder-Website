from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from .. import address_helper, status

#from application.business_logic import (PITH_adults_details_logic,
#                              reset_declaration)
from application.models.application import Application
from application.models.adult_in_home import AdultInHome
from application.forms.PITH_forms.PITH_address_details import (
                     PITHAddressDetailsForm,
                     PITHAddressDetailsManualLookupForm,
                     PITHAddressDetailsManualForm)

def pith_address_details(request):
    """
    Method returning the template for the 2 references: first reference address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = PITHAddressDetailsForm(id=application_id_local)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.PITH_status
        }
        return render(request, 'PITH_address_details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = PITHAddressDetailsForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            postcode = form.cleaned_data.get('postcode')
            pith_address_record = AdultInHome.objects.get(
                application_id=application_id_local, adult=1)
            pith_address_record.postcode = postcode
            pith_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(reverse('PITH-Adult-Address-Details-View') + '?id='
                                            + application_id_local)
            if 'submit' in request.POST:
                return HttpResponseRedirect(reverse('PITH-Adult-Address-Details-View') + '?id='
                                            + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the adult's postcode"

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.PITH_status
            }
            return render(request, 'PITH_address_details.html', variables)


def pith_address_details_select(request):
    """
    Method returning the template for the 2 references: first reference select address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference select address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        pith_address_record = AdultInHome.objects.get(
            application_id=application_id_local, adult=1)
        postcode = pith_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(
            postcode)
        if len(addresses) != 0:
            form = PITHAddressDetailsManualLookupForm(
                id=application_id_local, choices=addresses)

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local,
                'postcode': postcode,
                'people_in_home_status': application.PITH_status
            }
            return render(request, 'PITH_address_details_lookup.html', variables)
        else:
            form = PITHAddressDetailsForm(id=application_id_local)
            form.check_flag()
            form.errors['postcode'] = {'Please enter a valid postcode.': 'invalid'}

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.PITH_status
            }
            return render(request, 'PITH_address_details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        pith_address_record = AdultInHome.objects.get(
            application_id=application_id_local, adult=1)
        postcode = pith_address_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = PITHAddressDetailsManualLookupForm(request.POST, id=application_id_local, choices=addresses)
        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            pith_address_record.street_line1 = line1
            pith_address_record.street_line2 = line2
            pith_address_record.town = town
            pith_address_record.county = ''
            pith_address_record.postcode = postcode
            pith_address_record.country = 'United Kingdom'
            pith_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=application_id_local).people_in_home_status != 'COMPLETED':
                status.update(application_id_local, 'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('PITH_address_details.html') + '?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem finding the adult's address"

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.PITH_status
            }
            return render(request, 'PITH_address_details_lookup.html', variables)


def pith_address_details_manual(request):
    """
    Method returning the template for the 2 references: first reference manual address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference manual address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = PITHAddressDetailsManualForm(id=application_id_local)
        form.check_flag()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.PITH_status
        }
        return render(request, 'PITH_address_details_manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = PITHAddressDetailsManualForm(request.POST, id=application_id_local)
        form.remove_flag()

        if form.is_valid():
            street_line1 = form.cleaned_data.get(
                'street_line1')
            street_line2 = form.cleaned_data.get(
                'street_line2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
            pith_address_record = AdultInHome.objects.get(
                application_id=application_id_local, adult=1)
            pith_address_record.street_line1 = street_line1
            pith_address_record.street_line2 = street_line2
            pith_address_record.town = town
            pith_address_record.county = county
            pith_address_record.postcode = postcode
            pith_address_record.country = country
            pith_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(reverse('PITH-Address-Details-View') + '?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the adult's address"

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': application_id_local,
                'people_in_home_status': application.PITH_status
            }
            return render(request, 'PITH_address_details_manual.html', variables)