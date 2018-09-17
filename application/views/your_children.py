import collections
import datetime

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..forms import YourChildrenGuidanceForm, YourChildrenDetailsForm, YourChildrenLivingWithYouForm, ChildAddressForm, \
    YourChildrenSummaryForm, YourChildManualAddressForm, YourChildrenHomeAddressLookupForm
from ..models import Application, Child
from .. import status
from ..business_logic import remove_child, rearrange_children, your_children_details_logic, reset_declaration


def your_children_guidance(request):
    """
    Method for rendering the your children task's guidance page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered guidance page template
    """
    if request.method == 'GET':

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

    if request.method == 'POST':
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
        return your_children_details_get_handler(request)

    if request.method == 'POST':
        return your_children_details_post_handler(request)


def your_children_details_get_handler(request):
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


def your_children_details_post_handler(request):
    application_id_local = request.POST["id"]
    number_of_children = request.POST["children"]
    current_date = timezone.now()

    remove_button = True
    # If there are no adults in the database
    if number_of_children == 0:
        # Set the number of adults to 1 to initialise one instance of the form
        number_of_children = 1
        # Disable the remove person button
        remove_button = False
    # If there is only one adult in the database
    if number_of_children == 1:
        # Disable the remove person button
        remove_button = False
    application = Application.objects.get(pk=application_id_local)
    # Generate a list of forms to iterate through in the HTML
    form_list = []
    # List to allow for the validation of each form
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
        # If all forms are valid
        if False not in valid_list:
            variables = {
                'application_id': application_id_local,
                'your_children_status': application.your_children_status
            }
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
    if 'add_person' in request.POST:
        # If all forms are valid
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
        return your_children_living_with_you_get_handler(request)
    if request.method == 'POST':
        return your_children_living_with_you_post_handler(request)


def your_children_living_with_you_get_handler(request):
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


def your_children_living_with_you_post_handler(request):
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
        return your_children_address_capture_get_handler(request)
    if request.method == 'POST':
        return your_children_address_capture_post_handler(request)


def your_children_address_capture_get_handler(request):
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


def your_children_address_capture_post_handler(request):
    application_id_local = request.POST["id"]
    child = request.POST["child"]

    if 'postcode-search' in request.POST:

        if Application.get_id(app_id=application_id_local).personal_details_status != 'COMPLETED':
            status.update(application_id_local, 'your_children_status', 'IN_PROGRESS')

        return HttpResponseRedirect(reverse('Your-Children-Address-Select-View')
                                    + '?id=' + application_id_local + '&child=' + str(child))


def your_children_summary(request):
    """
    View method for rendering the Your Children task summary page.
    """
    if request.method == "GET":
        return your_children_summary_get_handler(request)


def your_children_summary_get_handler(request):
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
