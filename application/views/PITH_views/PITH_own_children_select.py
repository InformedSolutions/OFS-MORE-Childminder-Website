import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application import status, address_helper
from application.forms import ChildAddressForm, YourChildrenAddressLookupForm
from application.models import Child, Application, ChildAddress, AdultInHome
from application.utils import build_url, get_id
from application.views.your_children import __remove_arc_address_flag, __get_next_child_number_for_address_entry

logger = logging.getLogger()


def PITHOwnChildrenSelectView(request):
    return __own_children_address_selection(request)


# The following code is a modified version of the your_children views
def __own_children_address_selection(request):
    template = 'PITH_templates/PITH_own_children_select.html'
    address_lookup_template = 'PITH_templates/PITH_own_children_postcode.html'
    success_url = ('Task-List-View', 'PITH-Summary-View')
    address_url = 'PITH-Own-Children-Postcode-View'

    if request.method == 'GET':
        return __own_children_address_selection_get_handler(request,
                                                            template=template,
                                                            address_lookup_template=address_lookup_template)
    if request.method == 'POST':
        return __own_children_address_selection_post_handler(request,
                                                             template=template,
                                                             success_url=success_url,
                                                             address_url=address_url)


def __own_children_address_selection_get_handler(request, template, address_lookup_template):
    """
    Method for handling GET requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address selection template
    """

    application_id = get_id(request)
    child = request.GET["children"]
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
            'children': child,
        }

        return render(request, template, variables)

    else:
        form = ChildAddressForm(id=application_id, child=child)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id,
            'children': child,
        }

        return render(request, address_lookup_template, variables)


def __own_children_address_selection_post_handler(request, template, success_url, address_url):
    """
    Method for handling POST requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow. This could be either another address capture request
    (for other children), or a redirect to the task summary page.
    """

    application_id = get_id(request)
    child = request.GET["children"]

    logger.debug('Saving full address child address (acquired by postcode lookup) for application with id: '
                 + str(application_id) + " and children number: " + str(child))

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
            invalid_adults_url, valid_adults_url = success_url
            adults = AdultInHome.objects.filter(application_id=application_id)

            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                redirect_url = invalid_adults_url
            else:
                redirect_url = valid_adults_url

            return HttpResponseRedirect(build_url(redirect_url, get={'id': application_id}))
        # Recurse through use of querystring params
        return HttpResponseRedirect(
            reverse(address_url) + '?id=' + application_id + '&children=' + str(next_child))
    else:

        form.error_summary_title = 'There was a problem finding your address'

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'postcode': postcode,
            'form': form,
            'application_id': application_id,
            'children': child,
            'name': child_record.get_full_name(),
        }

        return render(request, template, variables)