import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

from application import status
from application.forms.PITH_forms import PITHAddressForm
from application.models import AdultInHome, Application, AdultInHomeAddress
from application.utils import get_id, build_url

logger = logging.getLogger('')


def PITHAddressDetailsView(request):

    return __PITH_address_capture(request)


# The following code is a modified version of the your_children views
def __PITH_address_capture(request):
    """
    Method for rendering the page responsible for capturing details of a Adult's address
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered adult's address capture template
    """
    template = 'PITH_templates/PITH_address_details.html'
    success_url = 'PITH-Address-Select-View'

    if request.method == 'GET':

        logger.debug('Use GET handler')

        return __PITH_address_capture_get_handler(request,
                                                  template=template)
    if request.method == 'POST':

        logger.debug('Use POST handler')

        return __PITH_address_lookup_post_handler(request,
                                                  template=template,
                                                  success_url=success_url)


def __PITH_address_capture_get_handler(request, template):
    """
    View method for rendering the Your Adult's address lookup page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered adult's address capture template
    """

    application_id = get_id(request)
    adult = request.GET["adult"]
    adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)

    logger.debug('Rendering postcode lookup page to capture an adult address for application with id: '
                 + str(application_id) + " and adult number: " + str(adult))
    form = PITHAddressForm(id=application_id, adult=adult, adult_record=adult_record)

    adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)
    logger.debug('Adult record: {}'.format(adult_record))

    variables = {
        'form': form,
        'application_id': application_id,
        'adult': adult,
        'adult_record': adult_record
    }

    return render(request, template, variables)

    return render(request, template, variables)


def __PITH_address_lookup_post_handler(request, template, success_url):
    """
    Method for managing POST requests to lookup addresses from a postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to a list of matched addresses or a returned page including any validation errors.
    """

    application_id = get_id(request)
    adult = request.GET["adult"]
    adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)

    logger.debug('Fetching postcode lookup matches for adult address details using application id: '
                 + str(application_id) + " and adult number: " + str(adult))

    form = PITHAddressForm(request.POST, id=application_id, adult=adult, adult_record=adult_record)

    application = Application.objects.get(application_id=application_id)

    adult_id = adult_record.adult_id
    if 'postcode-search' in request.POST:

        if form.is_valid():
            # If postcode search triggered instantiate address record with postcode saved
            postcode = form.cleaned_data.get('postcode')

            # Create or update address record based on presence test
            if AdultInHomeAddress.objects.filter(application_id=application_id, adult_id=adult_id).count() == 0:
                pith_address_record = AdultInHomeAddress(street_line1='',
                                                         street_line2='',
                                                         town='',
                                                         county='',
                                                         country='',
                                                         postcode=postcode,
                                                         application_id=application,
                                                         adult_id=adult_record,
                                                         adult_in_home_address=adult)
                pith_address_record.save()
            else:
                pith_address_record = AdultInHomeAddress.objects.filter(adult_id=adult_id)
                pith_address_record.update(postcode=postcode)

            if Application.get_id(app_id=application_id).people_in_home_status not in ['COMPLETED', 'WAITING']:
                status.update(application_id, 'people_in_home_status', 'IN_PROGRESS')

            return HttpResponseRedirect(build_url(success_url, get={'id': application_id,
                                                                    'adult': str(adult)}))
        else:
            form.error_summary_title = 'There was a problem with the postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'
            adult_record = AdultInHome.objects.get(application_id=application_id, adult_in_home_address=adult)
            variables = {
                'form': form,
                'application_id': application_id,
                'adult': adult,
                'adult_record': adult_record,
            }

            return render(request, template, variables)
