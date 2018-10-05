import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

from application import status
from application.forms import ChildAddressForm
from application.models import Child, Application, ChildAddress
from application.utils import get_id, build_url

logger = logging.getLogger('')


def PITHOwnChildrenPostcodeView(request):

    return __own_children_address_capture(request)


# The following code is a modified version of the your_children views
def __own_children_address_capture(request):
    """
    Method for rendering the page responsible for capturing details of a Child's address
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address capture template
    """
    template = 'PITH_templates/PITH_own_children_postcode.html'
    success_url = 'PITH-Own-Children-Select-View'

    if request.method == 'GET':

        logger.debug('Use GET handler')

        return __own_children_address_capture_get_handler(request,
                                                          template=template)
    if request.method == 'POST':

        logger.debug('Use POST handler')

        return __own_children_address_lookup_post_handler(request,
                                                          template=template,
                                                          success_url=success_url)


def __own_children_address_capture_get_handler(request, template):
    """
    View method for rendering the Your Children's address lookup page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's address capture template
    """

    application_id = get_id(request)
    child = request.GET["children"]

    logger.debug('Rendering postcode lookup page to capture a child address for application with id: '
                 + str(application_id) + " and child number: " + str(child))

    form = ChildAddressForm(id=application_id, child=child)

    child_record = Child.objects.get(application_id=application_id, child=child)

    variables = {
        'form': form,
        'name': child_record.get_full_name(),
        'application_id': application_id,
        'children': child,
    }

    return render(request, template, variables)


def __own_children_address_lookup_post_handler(request, template, success_url):
    """
    Method for managing POST requests to lookup addresses from a postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to a list of matched addresses or a returned page including any validation errors.
    """

    application_id = get_id(request)
    child = request.GET["children"]

    logger.debug('Fetching postcode lookup matches for child address details using application id: '
                 + str(application_id) + " and children number: " + str(child))

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
                                                    child=child)
                child_address_record.save()
            else:
                child_address_record = ChildAddress.objects.get(application_id=application_id, child=child)
                child_address_record.postcode = postcode
                child_address_record.save()

            if Application.get_id(app_id=application_id).people_in_home_status not in ['COMPLETED', 'WAITING']:
                status.update(application_id, 'people_in_home_status', 'IN_PROGRESS')

            return HttpResponseRedirect(build_url(success_url, get={'id': application_id,
                                                                    'children': str(child)}))
        else:
            form.error_summary_title = 'There was a problem with the postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            child_record = Child.objects.get(application_id=application_id, child=child)

            variables = {
                'form': form,
                'name': child_record.get_full_name(),
                'application_id': application_id,
                'children': child,
            }

            return render(request, template, variables)
