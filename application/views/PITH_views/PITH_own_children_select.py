import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application import status, address_helper
from application.business_logic import get_application
from application.forms import ChildAddressForm, YourChildrenAddressLookupForm
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome, Child, Application, ChildAddress
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_form_view import PITHFormView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm
from application.views.your_children import __remove_arc_address_flag, __get_next_child_number_for_address_entry


def PITHOwnChildrenSelectView(request):
    return __own_children_address_selection(request)


# The following code is a modified version of the your_children views
def __own_children_address_selection(request):
    template =

    if request.method == 'GET':
        return __own_children_address_selection_get_handler(request)
    if request.method == 'POST':
        return __own_children_address_selection_post_handler(request)


def __own_children_address_selection_get_handler(request, template):
    """
    Method for handling GET requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address selection template
    """

    application_id = request.GET["id"]
    child = request.GET["child"]
    application = Application.get_id(app_id=application_id)

    child_record = Child.objects.get(application_id=application_id, child=child)
    child_address_record = ChildAddress.objects.get(application_id=application_id, child=child)
    postcode = child_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

    if len(addresses) != 0:
        form = YourChildrenAddressLookupForm(id=application_id, choices=addresses)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id,
            'postcode': postcode,
            'name': child_record.get_full_name(),
            'child': child,
        }

        return render(request, 'your-childs-address.html', variables)

    else:
        form = ChildAddressForm(id=application_id, child=child)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id,
            'child': child,
        }

        return render(request, 'your-children-address-lookup.html', variables)


def __own_children_address_selection_post_handler(request, template, success_url):
    """
    Method for handling POST requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow. This could be either another address capture request
    (for other children), or a redirect to the task summary page.
    """

    application_id = request.POST["id"]
    child = request.POST["child"]

    logger.debug('Saving full address child address (acquired by postcode lookup) for application with id: '
                 + str(application_id) + " and child number: " + str(child))

    application = Application.get_id(app_id=application_id)
    child_record = Child.objects.get(application_id=application_id, child=str(child))
    child_address_record = ChildAddress.objects.get(application_id=application_id, child=str(child))
    postcode = child_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
    form = YourChildrenAddressLookupForm(request.POST, id=application_id, choices=addresses)

    if form.is_valid():
        selected_address_index = int(request.POST["address"])
        selected_address = address_helper.AddressHelper.get_posted_address(selected_address_index, postcode)
        line1 = selected_address['line1']
        line2 = selected_address['line2']
        town = selected_address['townOrCity']
        postcode = selected_address['postcode']

        child_address_record.street_line1 = line1
        child_address_record.street_line2 = line2
        child_address_record.town = town
        child_address_record.postcode = postcode
        child_address_record.country = 'United Kingdom'
        child_address_record.save()

        if Application.get_id(app_id=application_id).your_children_status != 'COMPLETED':
            status.update(application_id, 'your_children_status', 'IN_PROGRESS')

        # At this point, if an address was previously flagged by ARC, the comment can be safely removed
        __remove_arc_address_flag(child_address_record)

        next_child = __get_next_child_number_for_address_entry(application_id, int(child))

        if next_child is None:
            return HttpResponseRedirect(reverse('Your-Children-Summary-View') + '?id=' +
                                        application_id)

        # Recurse through use of querystring params
        return HttpResponseRedirect(
            reverse('Your-Children-Address-View') + '?id=' + application_id + '&child=' + str(next_child))
    else:

        form.error_summary_title = 'There was a problem finding your address'

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'postcode': postcode,
            'form': form,
            'application_id': application_id,
            'child': child,
            'name': child_record.get_full_name(),
        }

        return render(request, 'your-childs-address.html', variables)