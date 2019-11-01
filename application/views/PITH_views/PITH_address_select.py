import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from application import status, address_helper
from application.forms.PITH_forms import PITHAddressLookupForm, PITHAddressForm
from application.models import Child, Application, ChildAddress, AdultInHome, AdultInHomeAddress
from application.utils import build_url, get_id
from application.views.PITH_views.your_adults import __get_next_adult_number_for_address_entry
from application.business_logic import awaiting_pith_dbs_action_from_user, find_dbs_status

logger = logging.getLogger()


def PITHAddressSelectView(request):

    return __PITH_address_selection(request)


# The following code is a modified version of the your_children views
def __PITH_address_selection(request):

    template = 'PITH_templates/PITH_address_select.html'
    address_lookup_template = 'PITH_templates/PITH_address_postcode.html'
    success_url = ('Task-List-View', 'PITH-Lived-Abroad-View')
    address_url = 'PITH-Address-Details-View'

    if request.method == 'GET':

        return __PITH_address_selection_get_handler(request,
                                                    template=template,
                                                    address_lookup_template=address_lookup_template)

    if request.method == 'POST':

        return __PITH_address_selection_post_handler(request,
                                                     template=template,
                                                     success_url=success_url,
                                                     address_url=address_url)


def __PITH_address_selection_get_handler(request, template, address_lookup_template):
    """
    Method for handling GET requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address selection template
    """

    application_id = get_id(request)
    adult = request.GET["adult"]
    application = Application.get_id(app_id=application_id)

    adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)
    adult_address_record = AdultInHomeAddress.objects.get(application_id=application_id, adult_in_home_address=adult)
    postcode = adult_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

    if len(addresses) != 0:

        form = PITHAddressLookupForm(id=application_id, choices=addresses)

        if application.application_status == 'FURTHER_INFORMATION':

            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id,
            'postcode': postcode,
            'name': adult_record,
            'adult': adult,
        }

        return render(request, template, variables)

    else:

        form = PITHAddressForm(id=application_id, adult=adult)

        if application.application_status == 'FURTHER_INFORMATION':

            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': application_id,
            'adult': adult,
        }

        return render(request, address_lookup_template, variables)


def __PITH_address_selection_post_handler(request, template, success_url, address_url):
    """
    Method for handling POST requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow. This could be either another address capture request
    (for other children), or a redirect to the task summary page.
    """

    application_id = get_id(request)
    adult = request.GET["adult"]

    logger.debug('Saving full address adult address (acquired by postcode lookup) for application with id: '
                 + str(application_id) + " and adult number: " + str(adult))

    application = Application.get_id(app_id=application_id)
    adult_record = AdultInHome.objects.get(application_id=application_id, adult=str(adult))
    adult_address_record = AdultInHomeAddress.objects.get(application_id=application_id, adult_in_home_address=str(adult))
    postcode = adult_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
    form = PITHAddressLookupForm(request.POST, id=application_id, choices=addresses)

    if form.is_valid():

        selected_address_index = int(request.POST["address"])
        selected_address = address_helper.AddressHelper.get_posted_address(selected_address_index, postcode)
        line1 = selected_address['line1']
        line2 = selected_address['line2']
        town = selected_address['townOrCity']
        postcode = selected_address['postcode']

        adult_address_record.street_line1 = line1
        adult_address_record.street_line2 = line2
        adult_address_record.town = town
        adult_address_record.postcode = postcode
        adult_address_record.country = 'United Kingdom'
        adult_address_record.save()

        if Application.get_id(app_id=application_id).people_in_home_status not in ['COMPLETED', 'WAITING']:
            status.update(application_id, 'people_in_home_status', 'IN_PROGRESS')

        # At this point, if an address was previously flagged by ARC, the comment can be safely removed
        #__remove_arc_address_flag(child_address_record)

        next_adult = __get_next_adult_number_for_address_entry(application_id, int(adult))

        if next_adult is None:

            invalid_adults_url, valid_adults_url = success_url
            redirect_url = valid_adults_url

            return HttpResponseRedirect(build_url(redirect_url, get={'id': application_id}))
        # Recurse through use of querystring params
        return HttpResponseRedirect(
            reverse(address_url) + '?id=' + application_id + '&adult=' + str(next_adult))

    else:

        form.error_summary_title = 'There was a problem finding your address'

        if application.application_status == 'FURTHER_INFORMATION':

            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'postcode': postcode,
            'form': form,
            'application_id': application_id,
            'adult': adult,
            'name': adult_record.get_full_name(),
        }

        return render(request, template, variables)
