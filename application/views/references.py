from django.utils import timezone

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..summary_page_data import first_reference_name_dict, first_reference_link_dict,\
                                second_reference_name_dict, second_reference_link_dict
from ..table_util import Table, create_tables, submit_link_setter
from .. import address_helper, status
from ..business_logic import (references_first_reference_logic,
                              references_second_reference_logic,
                              reset_declaration)
from ..forms import (FirstReferenceForm,
                     ReferenceFirstReferenceAddressForm,
                     ReferenceFirstReferenceAddressLookupForm,
                     ReferenceFirstReferenceAddressManualForm,
                     ReferenceFirstReferenceContactForm,
                     ReferenceIntroForm,
                     ReferenceSecondReferenceAddressForm,
                     ReferenceSecondReferenceAddressLookupForm,
                     ReferenceSecondReferenceAddressManualForm,
                     ReferenceSecondReferenceContactForm,
                     ReferenceSummaryForm,
                     SecondReferenceForm)
from ..models import (Application,
                      Reference)


def references_intro(request):
    """
    Method returning the template for the 2 references: intro page (for a given application)
    and navigating to the Your health: intro page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: intro template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceIntroForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-intro.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceIntroForm(request.POST)
        application = Application.objects.get(pk=application_id_local)

        # Default status to in progress irrespective of choices made
        status.update(application_id_local, 'references_status', 'IN_PROGRESS')

        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-intro.html', variables)


def references_first_reference(request):
    """
    Method returning the template for the 2 references: first reference page (for a given application)
    and navigating to the 2 references: first reference address page when successfully completed;
    business logic is applied to either create or update the associated Reference record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstReferenceForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstReferenceForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            # Create or update Reference record
            references_record = references_first_reference_logic(
                application_id_local, form)
            references_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-address?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-first-reference.html', variables)


def references_first_reference_address(request):
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
        form = ReferenceFirstReferenceAddressForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            postcode = form.cleaned_data.get('postcode')
            first_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=1)
            first_reference_record.postcode = postcode
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/select-first-reference-address/?id='
                                            + application_id_local)
            if 'submit' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/enter-first-reference-address/?id='
                                            + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's postcode"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address.html', variables)


def references_first_reference_address_select(request):
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
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        postcode = first_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(
            postcode)
        if len(addresses) != 0:
            form = ReferenceFirstReferenceAddressLookupForm(
                id=application_id_local, choices=addresses)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'postcode': postcode,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-lookup.html', variables)
        else:
            form = ReferenceFirstReferenceAddressForm(id=application_id_local)
            form.check_flag()
            form.errors['postcode'] = {'Please enter a valid postcode.': 'invalid'}
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'references-first-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        postcode = first_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = ReferenceFirstReferenceAddressLookupForm(request.POST, id=application_id_local, choices=addresses)
        form.remove_flag()
        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            first_reference_record.street_line1 = line1
            first_reference_record.street_line2 = line2
            first_reference_record.town = town
            first_reference_record.county = ''
            first_reference_record.postcode = postcode
            first_reference_record.country = 'United Kingdom'
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem finding the referee's address"
            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-lookup.html', variables)


def references_first_reference_address_manual(request):
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
        form = ReferenceFirstReferenceAddressManualForm(id=application_id_local)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressManualForm(request.POST, id=application_id_local)
        form.remove_flag()
        if form.is_valid():
            street_name_and_number = form.cleaned_data.get(
                'street_name_and_number')
            street_name_and_number2 = form.cleaned_data.get(
                'street_name_and_number2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
            first_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=1)
            first_reference_record.street_line1 = street_name_and_number
            first_reference_record.street_line2 = street_name_and_number2
            first_reference_record.town = town
            first_reference_record.county = county
            first_reference_record.postcode = postcode
            first_reference_record.country = country
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's address"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-manual.html', variables)


def references_first_reference_contact_details(request):
    """
    Method returning the template for the 2 references: first reference contact details page (for a given application)
    and navigating to the 2 references: second reference page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference contact details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceFirstReferenceContactForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-contact-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceFirstReferenceContactForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')
            references_first_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                              reference=1)
            references_first_reference_address_record.phone_number = phone_number
            references_first_reference_address_record.email = email_address
            references_first_reference_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference?id=' + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's contact details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-first-reference-contact-details.html', variables)


def references_second_reference(request):
    """
    Method returning the template for the 2 references: second reference page (for a given application)
    and navigating to the 2 references: second reference address page when successfully completed;
    business logic is applied to either create or update the associated Reference record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = SecondReferenceForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = SecondReferenceForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            # Create or update Reference record
            references_record = references_second_reference_logic(
                application_id_local, form)
            references_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-address?id=' +
                                        application_id_local + '&manual=False&lookup=False')
        else:
            form.error_summary_title = "There was a problem with the referee's details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-second-reference.html', variables)


def references_second_reference_address(request):
    """
    Method returning the template for the 2 references: second reference address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            postcode = form.cleaned_data.get('postcode')
            second_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=2)
            second_reference_record.postcode = postcode
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/select-second-reference-address/?id='
                                            + application_id_local)
            if 'submit' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/enter-second-reference-address/?id='
                                            + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's postcode"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address.html', variables)


def references_second_reference_address_select(request):
    """
    Method returning the template for the 2 references: second reference select address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference select address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        postcode = second_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(
            postcode)
        if len(addresses) != 0:
            form = ReferenceSecondReferenceAddressLookupForm(
                id=application_id_local, choices=addresses)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'postcode': postcode,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-lookup.html', variables)
        else:
            form = ReferenceSecondReferenceAddressForm(id=application_id_local)
            form.check_flag()
            form.errors['postcode'] = {'Please enter a valid postcode.': 'invalid'}
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'references-second-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        postcode = second_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = ReferenceSecondReferenceAddressLookupForm(request.POST, id=application_id_local, choices=addresses)
        form.remove_flag()
        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            second_reference_record.street_line1 = line1
            second_reference_record.street_line2 = line2
            second_reference_record.town = town
            second_reference_record.county = ''
            second_reference_record.postcode = postcode
            second_reference_record.country = 'United Kingdom'
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem finding the referee's address"
            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-lookup.html', variables)


def references_second_reference_address_manual(request):
    """
    Method returning the template for the 2 references: second reference manual address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference manual address template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressManualForm(id=application_id_local)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressManualForm(request.POST, id=application_id_local)
        form.remove_flag()
        if form.is_valid():
            street_name_and_number = form.cleaned_data.get(
                'street_name_and_number')
            street_name_and_number2 = form.cleaned_data.get(
                'street_name_and_number2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
            second_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=2)
            second_reference_record.street_line1 = street_name_and_number
            second_reference_record.street_line2 = street_name_and_number2
            second_reference_record.town = town
            second_reference_record.county = county
            second_reference_record.postcode = postcode
            second_reference_record.country = country
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's address"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-manual.html', variables)


def references_second_reference_contact_details(request):
    """
    Method returning the template for the 2 references: second reference contact details page (for a given application)
    and navigating to the 2 references: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference contact details template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceSecondReferenceContactForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-contact-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceSecondReferenceContactForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            status.update(application_id_local,
                          'references_status', 'COMPLETED')
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')
            references_second_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                               reference=2)
            references_second_reference_address_record.phone_number = phone_number
            references_second_reference_address_record.email = email_address
            references_second_reference_address_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's contact details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-second-reference-contact-details.html', variables)


def references_summary(request):
    """
    Method returning the template for the 2 references: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        first_reference_first_name = first_reference_record.first_name
        first_reference_last_name = first_reference_record.last_name
        first_reference_relationship = first_reference_record.relationship
        first_reference_years_known = first_reference_record.years_known
        first_reference_months_known = first_reference_record.months_known
        first_reference_street_line1 = first_reference_record.street_line1
        first_reference_street_line2 = first_reference_record.street_line2
        first_reference_town = first_reference_record.town
        first_reference_county = first_reference_record.county
        first_reference_country = first_reference_record.country
        first_reference_postcode = first_reference_record.postcode
        first_reference_phone_number = first_reference_record.phone_number
        first_reference_email = first_reference_record.email
        second_reference_first_name = second_reference_record.first_name
        second_reference_last_name = second_reference_record.last_name
        second_reference_relationship = second_reference_record.relationship
        second_reference_years_known = second_reference_record.years_known
        second_reference_months_known = second_reference_record.months_known
        second_reference_street_line1 = second_reference_record.street_line1
        second_reference_street_line2 = second_reference_record.street_line2
        second_reference_town = second_reference_record.town
        second_reference_county = second_reference_record.county
        second_reference_country = second_reference_record.country
        second_reference_postcode = second_reference_record.postcode
        second_reference_phone_number = second_reference_record.phone_number
        second_reference_email = second_reference_record.email
        form = ReferenceSummaryForm()
        application = Application.objects.get(pk=application_id_local)

        first_reference_fields = {'full_name': ' '.join([first_reference_first_name, first_reference_last_name]),
                                  'relationship': first_reference_relationship,
                                  'known_for': ' '.join([str(first_reference_years_known), 'years,',
                                                         str(first_reference_months_known), 'months']),
                                  'address': ' '.join([first_reference_street_line1, (first_reference_street_line2 or ''),
                                                       first_reference_town, (first_reference_county or ''),
                                                       first_reference_postcode, first_reference_country]),
                                  'phone_number': first_reference_phone_number,
                                  'email_address': first_reference_email}
        first_reference_table = {'table_object': Table([first_reference_record.pk]),
                                 'fields': first_reference_fields,
                                 'title': 'First reference',
                                 'error_summary_title': "There's something wrong with your first reference"}
        first_reference_table = create_tables([first_reference_table], first_reference_name_dict,
                                              first_reference_link_dict)

        second_reference_fields = {'full_name': ' '.join([second_reference_first_name, second_reference_last_name]),
                                   'relationship': second_reference_relationship,
                                   'known_for': ' '.join([str(second_reference_years_known), 'years,',
                                                          str(second_reference_months_known), 'months']),
                                   'address': ' '.join(
                                      [second_reference_street_line1, (second_reference_street_line2 or ''),
                                       second_reference_town, (second_reference_county or ''),
                                       second_reference_postcode, second_reference_country]),
                                   'phone_number': second_reference_phone_number,
                                   'email_address': second_reference_email}
        second_reference_table = {'table_object': Table([second_reference_record.pk]),
                                  'fields': second_reference_fields,
                                  'title': 'Second reference',
                                  'error_summary_title': "There's something wrong with your first reference"}
        second_reference_table = create_tables([second_reference_table], second_reference_name_dict,
                                               second_reference_link_dict)
        table_list = first_reference_table + second_reference_table

        status.update(application_id_local, 'references_status', 'COMPLETED')
        variables = {
            'form': form,
            'application_id': application_id_local,
            'table_list': table_list,
            'page_title': 'Check your answers: references',
            'references_status': application.references_status,
        }
        variables = submit_link_setter(variables, table_list, 'references', application_id_local)

        return render(request, 'generic-summary-template.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceSummaryForm()
        if form.is_valid():
            status.update(application_id_local,
                          'references_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-summary.html', variables)
