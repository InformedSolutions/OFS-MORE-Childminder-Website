import collections
import datetime

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms import YourChildrenGuidanceForm, YourChildrenDetailsForm, YourChildrenLivingWithYouForm, ChildAddressForm, \
    YourChildrenSummaryForm, YourChildrenAddressLookupForm, YourChildManualAddressForm, ArcComments
from ..models import Application, Child, ChildAddress
from .. import status, address_helper
from ..business_logic import remove_child, rearrange_children, your_children_details_logic, reset_declaration, \
    child_address_logic
from ..table_util import create_tables, Table, submit_link_setter, Row
from ..summary_page_data import your_children_children_dict, your_children_children_link_dict
from ..utils import get_non_db_field_arc_comment


def __get_first_child_number_for_address_entry(application_id):
    """
    Helper method to fetch the child number for the first child for which address details are to be supplied
    :param application_id: the application identifier to be queried against
    :return: the next child number or None if no more children require address details to be provided
    """

    first_child = Child.objects.filter(application_id=application_id, lives_with_childminder=False).order_by(
        'child').first()
    return first_child.child


def __get_next_child_number_for_address_entry(application_id, current_child):
    """
    Helper method for sequencing a user through the workflow for providing child address details
    :param application_id: the application identifier to be queried against
    :param current_child: the current child information is being supplied for
    :return: the next child number or None if no more children require address details to be provided
    """

    if __get_all_children_count(application_id) > current_child:
        next_child = current_child + 1
        next_child_record = Child.objects.get(application_id=application_id, child=next_child)
        if not next_child_record.lives_with_childminder:
            return next_child
        else:
            return __get_next_child_number_for_address_entry(application_id, next_child)
    else:
        return None


def __get_all_children_count(application_id):
    """
    Helper method for providing a count of all children are associated with a childminder
    :param application_id: the application identifier to be queried against
    :return: a count of of how many children do not live a childminder
    """
    return Child.objects.filter(application_id=application_id).count()


def __get_children_not_living_with_childminder_count(application_id):
    """
    Helper method for providing a count of how many children do not live a childminder
    :param application_id: the application identifier to be queried against
    :return: a count of of how many children do not live a childminder
    """

    return Child.objects.filter(application_id=application_id, lives_with_childminder=False).count()


def your_children_guidance(request):
    """
    Method for handling HTTP requests made to the "Your Children" task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: a routed request to either the guidance page or the next page in the workflow
    """

    if request.method == 'GET':
        return __your_children_guidance_get_handler(request)
    if request.method == 'POST':
        return __your_children_guidance_post_handler(request)


def __your_children_guidance_get_handler(request):
    """
    Private get method handler for the "Your Children" task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered guidance page template
    """

    application_id = request.GET["id"]
    form = YourChildrenGuidanceForm()
    application = Application.get_id(app_id=application_id)
    variables = {
        'form': form,
        'application_id': application_id,
        'your_children_status': application.your_children_status,
    }

    if application.your_children_status != 'COMPLETED':
        status.update(application_id, 'your_children_status', 'IN_PROGRESS')

    return render(request, 'your-children-guidance.html', variables)


def __your_children_guidance_post_handler(request):
    """
    Private POST method handler for the "Your Children" task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to a page asking for details of the children
    """

    application_id = request.POST["id"]

    return HttpResponseRedirect(
        reverse('Your-Children-Details-View') + '?id=' + application_id)


def your_children_details(request):
    """
    Method for rendering the page responsible for capturing details of a Childminder's children
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered children's details capture template
    """

    if request.method == 'GET':
        return __your_children_details_get_handler(request)

    if request.method == 'POST':
        return __your_children_details_post_handler(request)


def __your_children_details_get_handler(request):
    """
    Method for handling a GET request to view the "Your children details" page
    :param request: a request object used to generate the HttpResponse
    :return the "Your children details" page which allows a user to supply information regarding their children
    """

    application_id = request.GET["id"]

    number_of_children_present_in_querystring = request.GET.get('children') is not None

    if number_of_children_present_in_querystring:
        number_of_children = int(request.GET["children"])
    else:
        number_of_children = __get_all_children_count(application_id)

    remove_request_querystring_present = (request.GET.get('remove') is not None)

    child_to_remove = 0

    remove_button = True

    if remove_request_querystring_present:
        child_to_remove = int(request.GET.get('remove'))

    # If there are no children in the database
    if number_of_children == 0:
        # Set the number of children to 1 to initialise one instance of the form
        number_of_children = 1
    # If there is only one children in the database
    if number_of_children == 1:
        # Disable the remove person button
        remove_button = False

    application = Application.objects.get(pk=application_id)

    # Remove specific children if remove link is clicked
    if remove_request_querystring_present:
        remove_child(application_id, child_to_remove)
        rearrange_children(number_of_children, application_id)

    # Generate a list of forms to iterate through in the HTML
    form_list = []

    for i in range(1, number_of_children + 1):
        form = YourChildrenDetailsForm(
            id=application_id, child=i, prefix=i)

        form.check_flag()
        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem with your children's details"

        form_list.append(form)

    variables = {
        'form_list': form_list,
        'application_id': application_id,
        'number_of_children': number_of_children,
        'add_child': number_of_children + 1,
        'remove_child': number_of_children - 1,
        'remove_button': remove_button,
    }

    status.update(application_id, 'your_children_status', 'IN_PROGRESS')

    return render(request, 'your-children-details.html', variables)


def __your_children_details_post_handler(request):
    """
    View handler for managing details of children being submitted
    :param request: a request object used to generate the HttpResponse
    :return the Your Children details page containing either validation errors or a redirect to either the summary page
    or pages where a user gets asked for their respective addresses
    """
    application_id = request.POST["id"]
    number_of_children = request.POST["children"]
    current_date = timezone.now()

    remove_button = True

    # Initialize page with an empty child representation
    if number_of_children == 0:
        number_of_children = 1

    if number_of_children == 1:
        remove_button = False

    application = Application.objects.get(pk=application_id)

    form_list = []
    valid_list = []

    for i in range(1, int(number_of_children) + 1):

        form = YourChildrenDetailsForm(
            request.POST, id=application_id, child=i, prefix=i)
        form.remove_flag()
        form_list.append(form)
        form.error_summary_title = "There was a problem with your children's details"

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem with your children's details"

        if form.is_valid():
            child_record = your_children_details_logic(
                application_id, form, i)
            child_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            valid_list.append(True)
        else:
            valid_list.append(False)

    if 'submit' in request.POST:
        return __your_children_details_post_handler_for_submissions(request, application_id,
                                                                    valid_list, form_list, number_of_children,
                                                                    remove_button, application)

    if 'add_person' in request.POST:
        return __your_children_details_post_handler_for_adding_children(request, application_id,
                                                                        valid_list, form_list, number_of_children,
                                                                        remove_button, application)


def __your_children_details_post_handler_for_submissions(request, application_id, valid_list, form_list,
                                                         number_of_children, remove_button, application):
    """
    A dedicated post handler for cases where submissions are being made to the "Your children details" page
    :param request: a request object used to generate the HttpResponse
    :param application_id: the unique identifier of an application
    :param valid_list: a list of validated children details forms
    :param form_list: a full list of forms containing children details
    :param number_of_children: the total number of children associated with a childminder
    :param remove_button: a boolean flag that switches the visiblity of the remove link
    :param application: a full application object based on the supplied identifier
    :return: a redirect to the next portion of the workflow (Your Children Living with you page)
    """

    if False not in valid_list:
        return HttpResponseRedirect(reverse('Your-Children-Living-With-You-View') + '?id=' + application_id)

    # If there is an invalid form
    elif False in valid_list:
        variables = {
            'form_list': form_list,
            'application_id': application_id,
            'number_of_children': number_of_children,
            'add_child': int(number_of_children) + 1,
            'remove_child': int(number_of_children) - 1,
            'remove_button': remove_button,
            'your_children_status': application.your_children_status
        }
        return render(request, 'your-children-details.html', variables)


def __your_children_details_post_handler_for_adding_children(request, application_id, valid_list, form_list,
                                                             number_of_children, remove_button, application):
    """
    A dedicated post handler for cases where children are being added on the "Your children details" page
    :param request: a request object used to generate the HttpResponse
    :param application_id: the unique identifier of an application
    :param valid_list: a list of validated children details forms
    :param form_list: a full list of forms containing children details
    :param number_of_children: the total number of children associated with a childminder
    :param remove_button: a boolean flag that switches the visiblity of the remove link
    :param application: a full application object based on the supplied identifier
    :return: a refreshed "Your children details" page with new input fields for the additional child
    """

    if False not in valid_list:
        variables = {
            'application_id': application_id,
            'your_children_status': application.your_children_status
        }
        add_child = int(number_of_children) + 1
        add_child_string = str(add_child)
        # Reset task status to IN_PROGRESS if adults are updated
        status.update(application_id, 'your_children_status', 'IN_PROGRESS')
        return HttpResponseRedirect(reverse('Your-Children-Details-View') + '?id=' +
                                    application_id + '&children=' + add_child_string + '&remove=0#person'
                                    + add_child_string, variables)
    # If there is an invalid form
    elif False in valid_list:
        variables = {
            'form_list': form_list,
            'application_id': application_id,
            'number_of_children': number_of_children,
            'add_adult': int(number_of_children) + 1,
            'remove_child': int(number_of_children) - 1,
            'remove_button': remove_button,
            'your_children_status': application.your_children_status
        }

        return render(request, 'your-children-details.html', variables)


def your_children_living_with_you(request):
    """
    View handler for the "Your children addresses" page
    :param request: a request object used to generate the HttpResponse
    :return: a routed request to either the Your children address page or the next page in the workflow
    """

    if request.method == 'GET':
        return __your_children_living_with_you_get_handler(request)
    if request.method == 'POST':
        return __your_children_living_with_you_post_handler(request)


def __your_children_living_with_you_get_handler(request):
    """
    Method for handling a request to view the "Your children addresses" page
    :param request: a request object used to generate the HttpResponse
    :return the "Your children addresses" page
    """

    application_id = request.GET["id"]
    form = YourChildrenLivingWithYouForm(id=application_id)

    variables = {
        'form': form,
        'application_id': application_id,
    }

    return render(request, 'your-children-living-with-you.html', variables)


def __your_children_living_with_you_post_handler(request):
    """
    Method for handling a submission to the "Your children addresses" page
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow (Your Children Addresses with you page)
    """

    application_id = request.POST["id"]
    form = YourChildrenLivingWithYouForm(request.POST, id=application_id)

    if not form.is_valid():
        variables = {
            'form': form,
            'application_id': application_id,
        }

        return render(request, 'your-children-living-with-you.html', variables)

    # Mark children listed as living in the home

    children = Child.objects.filter(application_id=application_id)

    for child in children:
        child.lives_with_childminder = \
            str(child.child) in form.cleaned_data['children_living_with_childminder_selection']
        child.save()

    if __get_children_not_living_with_childminder_count(application_id) > 0:
        child_number = __get_first_child_number_for_address_entry(application_id)

        return HttpResponseRedirect(reverse('Your-Children-Address-View') + '?id=' +
                                    application_id + '&child=' + str(child_number))
    else:
        return HttpResponseRedirect(reverse('Your-Children-Summary-View') + '?id=' +
                                    application_id)


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


def your_children_address_selection(request):
    """
    Method for rendering the page that allows a user to select their Child's address from a list of addresses that match
    a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow. This could be either another address capture request
    (for other children), or a redirect to the task summary page.
    """

    if request.method == 'GET':
        return __your_children_address_selection_get_handler(request)
    if request.method == 'POST':
        return __your_children_address_selection_post_handler(request)


def __your_children_address_selection_get_handler(request):
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


def __your_children_address_selection_post_handler(request):
    """
    Method for handling POST requests to the page that allows a user to select their Child's address from a list of
    addresses that match a supplied postcode
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to the next portion of the workflow. This could be either another address capture request
    (for other children), or a redirect to the task summary page.
    """

    application_id = request.POST["id"]
    child = request.POST["child"]
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


def your_children_address_manual(request):
    """
    View logic implementation for managing the manual address entry page in the Your Children task
    :param request: inbound HTTP request object using either a GET or POST method
    :return: Either a redirect to the next section in the task workflow or a rendered template of the requested page
    """
    if request.method == 'GET':
        return __your_children_address_manual_get_handler(request)
    if request.method == 'POST':
        return _your_children_address_manual_post_handler(request)


def __your_children_address_manual_get_handler(request):
    """
    View logic implementation for managing GET requests to the manual address entry page in the Your Children task
    :param request: inbound HTTP request
    :return: Manual address entry page
    """
    application_id = request.GET["id"]
    child = request.GET["child"]

    child_record = Child.objects.get(application_id=application_id, child=child)
    application = Application.objects.get(pk=application_id)
    form = YourChildManualAddressForm(id=application_id, child=child)
    form.check_flag()

    if application.application_status == 'FURTHER_INFORMATION':
        form.error_summary_template_name = 'returned-error-summary.html'
        form.error_summary_title = 'There was a problem'

    variables = {
        'form': form,
        'child': child,
        'name': child_record.get_full_name(),
        'application_id': application_id,
    }

    return render(request, 'your-children-address-manual.html', variables)


def _your_children_address_manual_post_handler(request):
    """
    Method for handling POST requests to the page that allows a user to enter their Child's address using a manual form
    :param request: a request object used to generate the HttpResponse
    :return: Either a redirect to the next section in the task workflow or a rendered template of the requested page
    """
    current_date = timezone.now()

    application_id = request.POST["id"]
    child = request.POST["child"]
    application = Application.objects.get(pk=application_id)

    form = YourChildManualAddressForm(request.POST, id=application_id, child=child)
    form.remove_flag()

    if form.is_valid():

        child_address_record = child_address_logic(application_id, child, form)
        child_address_record.save()
        application = Application.objects.get(pk=application_id)
        application.date_updated = current_date
        application.save()

        if Application.objects \
                .get(pk=application_id) \
                .personal_details_status != 'COMPLETED':
            status.update(application_id, 'your_children_status', 'IN_PROGRESS')

        reset_declaration(application)

        # Recurse through querystring params
        next_child = __get_next_child_number_for_address_entry(application_id, int(child))

        if next_child is None:
            return HttpResponseRedirect(reverse('Your-Children-Summary-View') + '?id=' +
                                        application_id)

        return HttpResponseRedirect(
            reverse('Your-Children-Address-View') + '?id=' + application_id + '&child=' + str(next_child))
    else:
        form.error_summary_title = 'There was a problem with your address'
        child_record = Child.objects.get(application_id=application_id, child=child)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'
        variables = {
            'form': form,
            'child': child,
            'name': child_record.get_full_name(),
            'application_id': application_id,
        }
        return render(request, 'your-children-address-manual.html', variables)


def your_children_summary(request):
    """
    View method for rendering the Your Children task summary page.
    :param request: a request object used to generate the HttpResponse
    :return: Either a redirect to the task list or the Your Children task summary page
    """

    if request.method == "GET":
        return __your_children_summary_get_handler(request)
    if request.method == "POST":
        return __your_children_summary_post_handler(request)


def __your_children_summary_get_handler(request):
    """
    View method for rendering the Your Children task summary page
    :param request: a request object used to generate the HttpResponse
    :return: The Your Children task summary page
    """

    application_id = request.GET["id"]
    application = Application.objects.get(application_id=application_id)

    form = YourChildrenSummaryForm()

    if application.application_status == 'FURTHER_INFORMATION':
        form.error_summary_template_name = 'returned-error-summary.html'
        form.error_summary_title = "There was a problem"

    children = Child.objects.filter(application_id=application_id).order_by('child')

    child_table_list = []

    for child in children:
        child_table = __create_child_table(child)
        child_table_list.append(child_table)

    child_table_list = create_tables(child_table_list, your_children_children_dict, your_children_children_link_dict)

    children_living_with_you_table = __create_children_living_with_you_table(application)

    table_list = [children_living_with_you_table] + child_table_list

    variables = {
        'page_title': 'Check your answers: your children',
        'form': form,
        'application_id': application_id,
        'table_list': table_list,
        'your_children_status': application.your_children_status
    }

    variables = submit_link_setter(variables, table_list, 'your_children', application_id)

    __add_arc_comments_to_child_tables(application_id, child_table_list)

    return render(request, 'generic-summary-template.html', variables)


def __create_children_living_with_you_table(application):
    children_living_with_childminder_temp_store = []

    children_living_with_childminder = \
        Child.objects.filter(application_id=application.application_id, lives_with_childminder=True)

    for child in children_living_with_childminder:
        children_living_with_childminder_temp_store.append(child.get_full_name())

    if len(children_living_with_childminder_temp_store) == 0:
        children_living_with_you_response_string = 'None'
    else:
        children_living_with_you_response_string = ", ".join(children_living_with_childminder_temp_store)

    table = Table([application.pk])

    table.title = "Children living with you"
    table.error_summary_title = "There was a problem with your children's details"

    back_link = 'Your-Children-Living-With-You-View'

    arc_comment = get_non_db_field_arc_comment(application.application_id, 'children_living_with_childminder_selection')

    row = Row('children_living_with_you', 'Which of your children live with you?',
              children_living_with_you_response_string, back_link, arc_comment)
    table.add_row(row)
    return table


def __create_child_table(child):
    dob = datetime.date(child.birth_year, child.birth_month, child.birth_day)

    if not child.lives_with_childminder:
        child_address = ChildAddress.objects.get(application_id=child.application_id, child=child.child)
        child_address_string = ' '.join([child_address.street_line1, (child_address.street_line2 or ''),
                                         child_address.town, (child_address.county or ''), child_address.postcode])
        child_fields = collections.OrderedDict([
            ('full_name', child.get_full_name()),
            ('date_of_birth', dob),
            ('address', child_address_string)
        ])
    else:
        child_fields = collections.OrderedDict([
            ('full_name', child.get_full_name()),
            ('date_of_birth', dob),
            ('address', 'Same as your own')
        ])

    table = Table([child.pk])
    table.other_people_numbers = '&child=' + str(child.child)

    # Table container object including title, errors etc.
    child_table = collections.OrderedDict({
        'table_object': table,
        'fields': child_fields,
        'title': child.get_full_name(),
        'error_summary_title': "There was a problem with your children's details"
    })

    return child_table


def __add_arc_comments_to_child_tables(application_id, child_tables):
    """
    Helper method for applying ARC comments to dynamic tables presented on the task summary page
    :param application_id: the unique identifier of the application
    :param child_tables: a collection of table objects consumed by the generic summary page
    """
    for index, table in enumerate(child_tables):
        # Set child index to plus 1 as these are not zero indexed
        child_index = index + 1

        # Append any dynamic errors to the full name of a child field
        name_field_name = 'full_name'

        if ArcComments.objects.filter(table_pk=table.table_pk[0], field_name=name_field_name,
                                      flagged=True).count() == 1:
            log = ArcComments.objects.get(table_pk=table.table_pk[0], field_name=name_field_name)
            for row in table.get_row_list():
                if row.data_name == name_field_name:
                    row.error = log.comment
                    break

        # Append any dynamic errors to respective child addresses

        if ChildAddress.objects.filter(application_id=application_id, child=child_index).exists():
            child_address = ChildAddress.objects.get(application_id=application_id, child=child_index)
            address_field_name = 'address'

            if ArcComments.objects.filter(table_pk=child_address.child_address_id, field_name=address_field_name,
                                          flagged=True).exists():
                log = ArcComments.objects.get(table_pk=child_address.child_address_id, field_name=address_field_name,
                                              flagged=True)
                for row in table.get_row_list():
                    if row.data_name == address_field_name:
                        row.error = log.comment
                        break


def __your_children_summary_post_handler(request):
    """
    View handler for actioning the summary page of the "Your children" task
    :param request: inbound HTTP request object
    :return: redirect to the Task List with a status update marked on the "Your children" task
    """
    application_id = request.POST["id"]
    status.update(application_id, 'your_children_status', 'COMPLETED')
    return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id)
