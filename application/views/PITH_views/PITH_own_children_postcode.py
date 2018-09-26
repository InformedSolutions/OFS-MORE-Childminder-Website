import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render

from application.business_logic import get_application
from application.models import AdultInHome, ApplicantHomeAddress, ChildInHome
from application.utils import get_id, build_url
from application.views.PITH_views.base_views.PITH_form_view import PITHFormView
from application.forms.PITH_forms.PITH_children_check_form import PITHChildrenCheckForm
from application.views.your_children import your_children_address_selection

logger = logging.getLogger('')

def PITHOwnChildrenPostcodeView(request):
    return your_children_address_selection(request)


# The following code is a modified version of the your_children views
def your_children_address_capture(request):
    """
    Method for rendering the page responsible for capturing details of a Child's address
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address capture template
    """

    if request.method == 'GET':
        return __your_children_address_capture_get_handler(request)
    if request.method == 'POST':
        return __your_children_address_lookup_post_handler(request)


def __your_children_address_capture_get_handler(request):
    """
    View method for rendering the Your Children's address lookup page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address capture template
    """

    application_id = request.GET["id"]
    child = request.GET["child"]

    logger.debug('Rendering postcode lookup page to capture a child address for application with id: '
                 + str(application_id) + " and child number: " + str(child))

    form = ChildAddressForm(id=application_id, child=child)

    child_record = Child.objects.get(application_id=application_id, child=child)

    variables = {
        'form': form,
        'name': child_record.get_full_name(),
        'application_id': application_id,
        'child': child,
    }

    return render(request, 'your-children-address-lookup.html', variables)


def __your_children_address_lookup_post_handler(request):
    """
    Method for managing POST requests to lookup addresses from a postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to a list of matched addresses or a returned page including any validation errors.
    """

    application_id = request.POST["id"]
    child = request.POST["child"]

    logger.debug('Fetching postcode lookup matches for child address details using application id: '
                 + str(application_id) + " and child number: " + str(child))

    form = ChildAddressForm(request.POST, id=application_id, child=child)

    application = Application.objects.get(application_id=application_id)

    if 'postcode-search' in request.POST:

        if form.is_valid():
            # If postcode search triggered instantiate address record with postcode saved
            postcode = form.cleaned_data.get('postcode')

            # Create or update address record based on presence test
            if ChildAddress.objects.filter(application_id=application_id, child=child).count() == 0:
                child_address_record = ChildAddress(street_line1='',
                                                    street_line2='',
                                                    town='',
                                                    county='',
                                                    country='',
                                                    postcode=postcode,
                                                    application_id=application,
                                                    child=child, )
                child_address_record.save()
            else:
                child_address_record = ChildAddress.objects.get(application_id=application_id, child=child)
                child_address_record.postcode = postcode
                child_address_record.save()

            if Application.get_id(app_id=application_id).personal_details_status != 'COMPLETED':
                status.update(application_id, 'your_children_status', 'IN_PROGRESS')

            return HttpResponseRedirect(reverse('Your-Children-Address-Select-View')
                                        + '?id=' + application_id + '&child=' + str(child))
        else:
            form.error_summary_title = 'There was a problem with your postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            child_record = Child.objects.get(application_id=application_id, child=child)

            variables = {
                'form': form,
                'name': child_record.get_full_name(),
                'application_id': application_id,
                'child': child,
            }

            return render(request, 'your-children-address-lookup.html', variables)