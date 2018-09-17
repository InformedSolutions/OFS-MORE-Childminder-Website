import collections
import datetime

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms import YourChildrenGuidanceForm, YourChildrenDetailsForm, YourChildrenLivingWithYouForm, ChildAddressForm, \
    YourChildrenSummaryForm, YourChildrenAddressLookupForm, YourChildManualAddressForm
from ..models import Application, Child, ChildAddress
from .. import status, address_helper
from ..business_logic import remove_child, rearrange_children, your_children_details_logic, reset_declaration


def your_children_guidance(request):
    """
    Method for handling submissions to the "Your Children" task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered guidance page template
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

    app_id = request.GET["id"]
    form = YourChildrenGuidanceForm()
    application = Application.get_id(app_id=app_id)
    variables = {
        'form': form,
        'application_id': app_id,
        'your_children_status': application.childcare_type_status,
    }

    if application.your_children_status != 'COMPLETED':
        status.update(app_id, 'your_children_status', 'IN_PROGRESS')

    return render(request, 'your-children-guidance.html', variables)


def __your_children_guidance_post_handler(request):
    """
    Private POST method handler for the "Your Children" task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: a redirect to a page asking for details of the children
    """

    app_id = request.POST["id"]

    return HttpResponseRedirect(
        reverse('Your-Children-Details-View') + '?id=' + app_id)


















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
    Method for handling a request to view the "Your children details" page
    """
    application_id_local = request.GET["id"]

    number_of_children_present_in_querystring = request.GET.get('children') is not None

    if number_of_children_present_in_querystring:
        number_of_children = int(request.GET["children"])
    else:
        number_of_children = Child.objects.filter(application_id=application_id_local).count()

    remove_querystring_present = request.GET.get('remove') is not None

    remove_person = 0

    remove_button = True

    if remove_querystring_present:
        remove_person = int(request.GET.get('remove'))

    # If there are no adults in the database
    if number_of_children == 0:
        # Set the number of adults to 1 to initialise one instance of the form
        number_of_children = 1
    # If there is only one adult in the database
    if number_of_children == 1:
        # Disable the remove person button
        remove_button = False
    application = Application.objects.get(pk=application_id_local)
    # Remove specific adult if remove button is pressed
    remove_child(application_id_local, remove_person)
    # Rearrange adult numbers if there are gaps
    rearrange_children(number_of_children, application_id_local)
    # Generate a list of forms to iterate through in the HTML
    form_list = []

    for i in range(1, number_of_children + 1):
        form = YourChildrenDetailsForm(
            id=application_id_local, child=i, prefix=i)

        form.check_flag()
        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem (Child " + str(i) + ")"
            is_review = True
        else:
            is_review = False

        form_list.append(form)

    variables = {
        'form_list': form_list,
        'application_id': application_id_local,
        'number_of_children': number_of_children,
        'add_child': number_of_children + 1,
        'remove_child': number_of_children - 1,
        'remove_button': remove_button,
        'your_children_status': application.your_children_status
    }
    status.update(application_id_local, 'your_children_status', 'IN_PROGRESS')
    return render(request, 'your-children-details.html', variables)


def __your_children_details_post_handler(request):
    application_id_local = request.POST["id"]
    number_of_children = request.POST["children"]
    current_date = timezone.now()

    remove_button = True

    # Initialize page with an empty child representation
    if number_of_children == 0:
        number_of_children = 1

    if number_of_children == 1:
        remove_button = False

    application = Application.objects.get(pk=application_id_local)

    form_list = []
    valid_list = []

    for i in range(1, int(number_of_children) + 1):

        form = YourChildrenDetailsForm(
            request.POST, id=application_id_local, child=i, prefix=i)
        form.remove_flag()
        form_list.append(form)
        form.error_summary_title = 'There was a problem with the details (Child ' + str(
            i) + ')'

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem (Child " + str(i) + ")"

        if form.is_valid():
            child_record = your_children_details_logic(
                application_id_local, form, i)
            child_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            valid_list.append(True)
        else:
            valid_list.append(False)

    if 'submit' in request.POST:
        return __your_children_details_post_handler_for_submissions(request, application_id_local,
                                                                    valid_list, form_list, number_of_children,
                                                                    remove_button, application)

    if 'add_person' in request.POST:
        return __your_children_details_post_handler_for_adding_children(request, application_id_local,
                                                                    valid_list, form_list, number_of_children,
                                                                    remove_button, application)


def __your_children_details_post_handler_for_submissions(request, application_id_local, valid_list, form_list,
                                                         number_of_children, remove_button, application):
    if False not in valid_list:
        return HttpResponseRedirect(reverse('Your-Children-Living-With-You-View') + '?id=' + application_id_local)

    # If there is an invalid form
    elif False in valid_list:
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'add_child': int(number_of_children) + 1,
            'remove_child': int(number_of_children) - 1,
            'remove_button': remove_button,
            'your_children_status': application.your_children_status
        }
        return render(request, 'your-children-details.html', variables)


def __your_children_details_post_handler_for_adding_children(request, application_id_local, valid_list, form_list,
                                                             number_of_children, remove_button, application):
    if False not in valid_list:
        variables = {
            'application_id': application_id_local,
            'your_children_status': application.your_children_status
        }
        add_child = int(number_of_children) + 1
        add_child_string = str(add_child)
        # Reset task status to IN_PROGRESS if adults are updated
        status.update(application_id_local, 'your_children_status', 'IN_PROGRESS')
        return HttpResponseRedirect(reverse('Your-Children-Details-View') + '?id=' +
                                    application_id_local + '&children=' + add_child_string + '&remove=0#person'
                                    + add_child_string, variables)
    # If there is an invalid form
    elif False in valid_list:
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_children,
            'add_adult': int(number_of_children) + 1,
            'remove_adult': int(number_of_children) - 1,
            'remove_button': remove_button,
            'your_children_status': application.your_children_status
        }

        return render(request, 'your-children-details.html', variables)
























def your_children_living_with_you(request):
    """
    View handler for the "Your children addresses" page
    """
    if request.method == 'GET':
        return __your_children_living_with_you_get_handler(request)
    if request.method == 'POST':
        return __your_children_living_with_you_post_handler(request)


def __your_children_living_with_you_get_handler(request):
    """
    Method for handling a request to view the "Your children addresses" page
    """

    application_id_local = request.GET["id"]
    form = YourChildrenLivingWithYouForm(id=application_id_local)

    variables = {
        'form': form,
        'application_id': application_id_local,
    }

    return render(request, 'your-children-living-with-you.html', variables)


def __your_children_living_with_you_post_handler(request):
    """
    Method for handling a submission to the "Your children addresses" page
    """

    application_id_local = request.GET["id"]
    form = YourChildrenLivingWithYouForm(request.POST, id=application_id_local)

    if not form.is_valid():
        variables = {
            'form': form,
            'application_id': application_id_local,
        }

        return render(request, 'your-children-living-with-you.html', variables)

    # Mark children listed as living in the home

    children = Child.objects.filter(application_id=application_id_local)

    for child in children:
        child.lives_with_childminder = \
            str(child.child) in form.cleaned_data['children_living_with_childminder_selection']
        child.save()

    if Child.objects.filter(application_id=application_id_local, lives_with_childminder=False).count() > 0:
        first_child_living_outside_home \
            = Child.objects.filter(application_id=application_id_local, lives_with_childminder=False)\
            .order_by('child').first()

        return HttpResponseRedirect(reverse('Your-Children-Address-View') + '?id=' +
                                    application_id_local + '&child=' + str(first_child_living_outside_home.child))
    else:
        return HttpResponseRedirect(reverse('Your-Children-Summary-View') + '?id=' +
                                    application_id_local)























def your_children_address_capture(request):
    if request.method == 'GET':
        return __your_children_address_capture_get_handler(request)
    if request.method == 'POST':
        return __your_children_address_capture_post_handler(request)


def __your_children_address_capture_get_handler(request):
    application_id_local = request.GET["id"]
    child = request.GET["child"]
    form = ChildAddressForm(id=application_id_local, child=child)

    child_record = Child.objects.get(application_id=application_id_local, child=child)

    variables = {
        'form': form,
        'name': child_record.get_full_name(),
        'application_id': application_id_local,
        'child': child,
    }

    return render(request, 'your-children-address-lookup.html', variables)


def __your_children_address_capture_post_handler(request):
    application_id_local = request.GET["id"]
    child = request.POST["child"]
    form = ChildAddressForm(request.POST, id=application_id_local, child=child)

    application = Application.objects.get(application_id=application_id_local)

    if 'postcode-search' in request.POST:

        if form.is_valid():
            # If postcode search triggered instantiate address record with postcode saved
            postcode = form.cleaned_data.get('postcode')

            # Create or update address record based on presence test
            if ChildAddress.objects.filter(application_id=application_id_local, child=child).count() == 0:
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
                child_address_record = ChildAddress.objects.get(application_id=application_id_local, child=child)
                child_address_record.postcode = postcode
                child_address_record.save()

            if Application.get_id(app_id=application_id_local).personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'your_children_status', 'IN_PROGRESS')

            return HttpResponseRedirect(reverse('Your-Children-Address-Select-View')
                                        + '?id=' + application_id_local + '&child=' + str(child))
        else:
            form.error_summary_title = 'There was a problem with your postcode'

            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            child_record = Child.objects.get(application_id=application_id_local, child=child)

            variables = {
                'form': form,
                'name': child_record.get_full_name(),
                'application_id': application_id_local,
                'child': child,
            }

            return render(request, 'your-children-address-lookup.html', variables)




def your_children_address_selection(request):
    if request.method == 'GET':
        return __your_children_address_selection_get_handler(request)
    if request.method == 'POST':
        return __your_children_address_selection_post_handler(request)




def __your_children_address_selection_get_handler(request):
    app_id = request.GET["id"]
    child = request.GET["child"]
    application = Application.get_id(app_id=app_id)

    child_record = Child.objects.get(application_id=app_id, child=child)
    child_address_record = ChildAddress.objects.get(application_id=app_id, child=child)
    postcode = child_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)

    if len(addresses) != 0:
        form = YourChildrenAddressLookupForm(id=app_id, choices=addresses)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'postcode': postcode,
            'name': child_record.get_full_name(),
            'child': child,
            'your_children_status': application.childcare_type_status,
        }

        return render(request, 'your-childs-address.html', variables)

    else:
        form = ChildAddressForm(id=app_id, child=child)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'child': child,
            'your_children_status': application.childcare_type_status,
        }

        return render(request, 'your-children-address-lookup.html', variables)


def __your_children_address_selection_post_handler(request):
    app_id = request.POST["id"]
    child = request.POST["child"]
    application = Application.get_id(app_id=app_id)
    child_record = Child.objects.get(application_id=app_id, child=str(child))
    child_address_record = ChildAddress.objects.get(application_id=app_id, child=str(child))
    postcode = child_address_record.postcode
    addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
    form = YourChildrenAddressLookupForm(request.POST, id=app_id, choices=addresses)

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

        if Application.get_id(app_id=app_id).your_children_status != 'COMPLETED':
            status.update(app_id, 'your_children_status', 'IN_PROGRESS')
        return HttpResponseRedirect(reverse('Personal-Details-Location-Of-Care-View') + '?id=' + app_id)
    else:

        form.error_summary_title = 'There was a problem finding your address'

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'postcode': postcode,
            'form': form,
            'application_id': app_id,
            'child': child,
            'name': child_record.get_full_name(),
            'your_children_status': application.childcare_type_status,
        }

        return render(request, 'your-childs-address.html', variables)


def your_children_address_manual(request):
    if request.method == 'GET':
        return __your_children_address_manual_get_handler(request)
    if request.method == 'POST':
        return _your_children_address_manual_post_handler(request)

def __your_children_address_manual_get_handler(request):
    application_id_local = request.GET["id"]
    child = request.GET["child"]

    child_record = Child.objects.get(application_id=application_id_local, child=child)
    application = Application.objects.get(pk=application_id_local)
    form = YourChildManualAddressForm(id=application_id_local, child=child)
    form.check_flag()

    if application.application_status == 'FURTHER_INFORMATION':
        form.error_summary_template_name = 'returned-error-summary.html'
        form.error_summary_title = 'There was a problem'

    variables = {
        'form': form,
        'child': child,
        'name': child_record.get_full_name(),
        'application_id': application_id_local,
        'your_children_status': application.childcare_type_status,
    }

    return render(request, 'your-children-address-manual.html', variables)


def _your_children_address_manual_post_handler(request):
    return None
















































def your_children_summary(request):
    """
    View method for rendering the Your Children task summary page.
    """
    if request.method == "GET":
        return __your_children_summary_get_handler(request)


def __your_children_summary_get_handler(request):
    application_id_local = request.GET["id"]
    form = YourChildrenSummaryForm()

    children_table = []
    children = Child.objects.filter(application_id=application_id_local)

    for child in children:
        dob = datetime.date(child.birth_year, child.birth_month, child.birth_day)
        child_details = collections.OrderedDict([
            ('child_number', child.child),
            ('full_name', child.get_full_name()),
            ('dob', dob),
            ('lives_with_childminder', child.lives_with_childminder),
        ])
        children_table.append(child_details)

    variables = {
        'page_title': 'Check your answers: your children',
        'form': form,
        'application_id': application_id_local,
        'children': children_table,
    }

    return render(request, 'your-children-summary.html', variables)
