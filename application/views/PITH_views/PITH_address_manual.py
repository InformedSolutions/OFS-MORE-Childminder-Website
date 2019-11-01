import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from application import status
from application.business_logic import child_address_logic, reset_declaration
from application.forms.PITH_forms import PITHManualAddressForm
from application.models import Application, AdultInHome, AdultInHomeAddress
from application.utils import build_url, get_id
from application.views.PITH_views.your_adults import __get_next_adult_number_for_address_entry

logger = logging.getLogger()


def PITHAddressManualView(request):

    return __PITH_address_manual(request)


def __PITH_address_manual(request):

    template = 'PITH_templates/PITH_address_manual.html'
    success_url = ('Task-List-View', 'PITH-Lived-Abroad-View')
    address_url = 'PITH-Address-Details-View'

    if request.method == 'GET':

        logger.debug('Use GET handler')

        return __PITH_address_manual_get_handler(request, template=template)

    if request.method == 'POST':

        logger.debug('User POST handler')

        return __PITH_address_manual_post_handler(request,
                                                          template=template,
                                                          success_url=success_url,
                                                          address_url=address_url)


def __PITH_address_manual_get_handler(request, template):
    """
    View logic implementation for managing GET requests to the manual address entry page in the Your Children task
    :param request: inbound HTTP request
    :return: Manual address entry page
    """
    application_id = get_id(request)
    adult = request.GET["adult"]

    logger.debug('Rendering manual adult address capture page for application with id: '
                 + str(application_id) + " and adult number: " + str(adult))

    adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)
    application = Application.objects.get(pk=application_id)
    form = PITHManualAddressForm(id=application_id, adult=adult)
    form.check_flag()

    if application.application_status == 'FURTHER_INFORMATION':

        form.error_summary_template_name = 'returned-error-summary.html'
        form.error_summary_title = 'There was a problem'

        logging.debug('Set returned error summary template')

    variables = {
        'form': form,
        'adult': adult,
        'name': adult_record,
        'application_id': application_id,
    }

    return render(request, template, variables)


def __PITH_address_manual_post_handler(request, template, success_url, address_url):
    """
    Method for handling POST requests to the page that allows a user to enter their Child's address using a manual form
    :param request: a request object used to generate the HttpResponse
    :return: Either a redirect to the next section in the task workflow or a rendered template of the requested page
    """
    current_date = timezone.now()

    application_id = get_id(request)
    adult = request.GET["adult"]

    logger.debug('Saving manual child address details for application with id: '
                 + str(application_id) + " and adult number: " + str(adult))

    application = Application.objects.get(pk=application_id)

    form = PITHManualAddressForm(request.POST, id=application_id, adult=adult)
    form.remove_flag()

    if form.is_valid():

        logger.debug('Form is valid')

        #pith_address_record = pith_address_logic(application_id, adult, form)
        #pith_address_record.save()
        application = Application.objects.get(pk=application_id)
        application.date_updated = current_date
        application.save()

        if application.people_in_home_status not in ['COMPLETED', 'WAITING']:
            logger.debug('Updating database with adult address for application: ' + application_id)
            status.update(application_id, 'people_in_home_status', 'IN_PROGRESS')
            logger.debug('Set task status to IN_PROGRESS')

        reset_declaration(application)

        logger.debug('Reset declaration')

        #__remove_arc_address_flag(child_address_record)

        #logger.debug('Removed ARC address flag for child address record')

        # Recurse through querystring params
        next_adult = __get_next_adult_number_for_address_entry(application_id, int(adult))

        logger.debug('Retrieve number for next child')

        if next_adult is None:

            logger.debug('If there is a next adult')

            invalid_adults_url, valid_adults_url = success_url
            redirect_url = valid_adults_url

            return HttpResponseRedirect(build_url(redirect_url, get={'id': application_id}))

        logger.debug('If there is no next adult')

        return HttpResponseRedirect(build_url(address_url, get={'id': application_id, 'adult': str(next_adult)}))

    else:

        logger.debug('Form is invalid')

        form.error_summary_title = 'There was a problem with your address'
        adult_record = AdultInHome.objects.get(application_id=application_id, adult=adult)

        if application.application_status == 'FURTHER_INFORMATION':

            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

            logger.debug('Set up returned error summary')

        variables = {
            'form': form,
            'adult': adult,
            'name': adult_record.get_full_name(),
            'application_id': application_id,
        }

        return render(request, template, variables)
