"""
Method returning the template for the Type of childcare: guidance page (for a given application) and navigating
to the Type of childcare: childcare ages page when successfully completed
"""

from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from .. import status
from ..business_logic import reset_declaration, childcare_type_logic
from ..forms import TypeOfChildcareGuidanceForm, TypeOfChildcareAgeGroupsForm, TypeOfChildcareRegisterForm
from ..models import Application, ChildcareType


def type_of_childcare_guidance(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: guidance template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = TypeOfChildcareGuidanceForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_type_status': application.childcare_type_status,
            'login_details_status': application.login_details_status,
        }
        if application.childcare_type_status != 'COMPLETED':
            status.update(app_id, 'childcare_type_status', 'IN_PROGRESS')

        return render(request, 'childcare-guidance.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TypeOfChildcareGuidanceForm(request.POST)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            if application.childcare_type_status != 'COMPLETED':
                status.update(app_id, 'childcare_type_status', 'IN_PROGRESS')

            return HttpResponseRedirect(
                reverse('Type-Of-Childcare-Age-Groups-View') + '?id=' + app_id)

        variables = {
            'form': form,
            'application_id': app_id
        }
        return render(request, 'childcare-guidance.html', variables)


"""
Method returning the template for the Type of childcare: age groups page (for a given application) and navigating
to the task list when successfully completed; business logic is applied to either create or update the
associated Childcare_Type record
"""


def type_of_childcare_age_groups(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: age groups template
    """

    current_date = datetime.today()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = TypeOfChildcareAgeGroupsForm(id=app_id)
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_type_status': application.childcare_type_status,
            'login_details_status': application.login_details_status,

        }

        return render(request, 'childcare-age-groups.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TypeOfChildcareAgeGroupsForm(request.POST, id=app_id)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            # Create or update Childcare_Type record
            childcare_type_record = childcare_type_logic(app_id, form)
            childcare_type_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            status.update(app_id, 'childcare_type_status', 'COMPLETED')

            return HttpResponseRedirect(reverse('Type-Of-Childcare-Register-View') + '?id=' + app_id)
        else:

            variables = {
                'form': form,
                'application_id': app_id,
                'childcare_type_status': application.childcare_type_status
            }
            return render(request, 'childcare-age-groups.html', variables)


"""
Method returning the template for the correct Type of childcare: register page (for a given application)
and navigating to the task list when successfully confirmed
"""


def type_of_childcare_register(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the correct rendered Type of childcare: register template
    """

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = TypeOfChildcareRegisterForm()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_type_status': application.childcare_type_status,
            'login_details_status': application.login_details_status,
        }

        # Move into separate method - check business logic too
        childcare_record = ChildcareType.objects.get(application_id=app_id)
        zero_to_five_status = childcare_record.zero_to_five
        five_to_eight_status = childcare_record.five_to_eight
        eight_plus_status = childcare_record.eight_plus

        if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
            return render(request, 'childcare-register-EYR-CR-both.html', variables)
        elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
            return render(request, 'childcare-register-EYR-CR-compulsory.html', variables)
        elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
            return render(request, 'childcare-register-EYR-CR-voluntary.html', variables)
        elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
            return render(request, 'childcare-register-EYR.html', variables)

        elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
            return HttpResponseRedirect(reverse('Local-Authority-View') + '?id=' + app_id)
        elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
            return HttpResponseRedirect(reverse('Local-Authority-View') + '?id=' + app_id)
        elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
            return HttpResponseRedirect(reverse('Local-Authority-View') + '?id=' + app_id)

        ###

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TypeOfChildcareRegisterForm(request.POST)
        application = Application.get_id(app_id=app_id)
        if form.is_valid():
            if application.childcare_type_status != 'COMPLETED':
                status.update(app_id, 'childcare_type_status', 'COMPLETED')

            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + app_id)
        else:
            variables = {
                'form': form,
                'application_id': app_id
            }

            return render(request, 'childcare-guidance.html', variables)


def local_authority_links(request):
    """

    :param request:
    :return:
    """
    if request.method == 'GET':

        app_id = request.GET["id"]
        variables = {
            'application_id': app_id
        }
        return render(request, 'local-authority.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.get_id(app_id=app_id)
        if application.childcare_type_status != 'COMPLETED':
            status.update(app_id, 'childcare_type_status', 'COMPLETED')
        if 'Cancel application' in request.POST.keys():
            return render(request, 'cancellation-guidance.html', )
        else:
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + app_id)

