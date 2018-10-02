import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from application import status
from application.business_logic import child_address_logic, reset_declaration
from application.forms import YourChildManualAddressForm, Child
from application.models import Application, AdultInHome
from application.utils import build_url, get_id
from application.views.your_children import __remove_arc_address_flag, __get_next_child_number_for_address_entry

logger = logging.getLogger()


def PITHOwnChildrenManualView(request):
    return __own_children_address_manual(request)


def __own_children_address_manual(request):
    template = 'PITH_templates/PITH_own_children_manual.html'
    success_url = ('Task-List-View', 'PITH-Summary-View')
    address_url = 'PITH-Own-Children-Postcode-View'

    if request.method == 'GET':
        return __own_children_address_manual_get_handler(request, template=template)
    if request.method == 'POST':
        return __own_children_address_manual_post_handler(request,
                                                          template=template,
                                                          success_url=success_url,
                                                          address_url=address_url)


def __own_children_address_manual_get_handler(request, template):
    """
    View logic implementation for managing GET requests to the manual address entry page in the Your Children task
    :param request: inbound HTTP request
    :return: Manual address entry page
    """
    application_id = get_id(request)
    child = request.GET["children"]

    logger.debug('Rendering manual child address capture page for application with id: '
                 + str(application_id) + " and child number: " + str(child))

    child_record = Child.objects.get(application_id=application_id, child=child)
    application = Application.objects.get(pk=application_id)
    form = YourChildManualAddressForm(id=application_id, child=child)
    form.check_flag()

    if application.application_status == 'FURTHER_INFORMATION':
        form.error_summary_template_name = 'returned-error-summary.html'
        form.error_summary_title = 'There was a problem'

    variables = {
        'form': form,
        'children': child,
        'name': child_record.get_full_name(),
        'application_id': application_id,
    }

    return render(request, template, variables)


def __own_children_address_manual_post_handler(request, template, success_url, address_url):
    """
    Method for handling POST requests to the page that allows a user to enter their Child's address using a manual form
    :param request: a request object used to generate the HttpResponse
    :return: Either a redirect to the next section in the task workflow or a rendered template of the requested page
    """
    current_date = timezone.now()

    application_id = get_id(request)
    child = request.GET["children"]

    logger.debug('Saving manual child address details for application with id: '
                 + str(application_id) + " and child number: " + str(child))

    application = Application.objects.get(pk=application_id)

    form = YourChildManualAddressForm(request.POST, id=application_id, child=child)
    form.remove_flag()

    if form.is_valid():

        child_address_record = child_address_logic(application_id, child, form)
        child_address_record.save()
        application = Application.objects.get(pk=application_id)
        application.date_updated = current_date
        application.save()

        status.update(application_id, 'people_in_home_status', 'IN_PROGRESS')

        reset_declaration(application)

        __remove_arc_address_flag(child_address_record)

        # Recurse through querystring params
        next_child = __get_next_child_number_for_address_entry(application_id, int(child))

        if next_child is None:
            invalid_adults_url, valid_adults_url = success_url
            adults = AdultInHome.objects.filter(application_id=application_id)

            if len(adults) != 0 and any(not adult.capita and not adult.on_update for adult in adults):
                redirect_url = invalid_adults_url
            else:
                redirect_url = valid_adults_url

            return HttpResponseRedirect(build_url(redirect_url, get={'id': application_id}))

        return HttpResponseRedirect(
            build_url(address_url, get={'id': application_id, 'children': str(next_child)}))
    else:
        form.error_summary_title = 'There was a problem with your address'
        child_record = Child.objects.get(application_id=application_id, child=child)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'
        variables = {
            'form': form,
            'children': child,
            'name': child_record.get_full_name(),
            'application_id': application_id,
        }
        return render(request, template, variables)