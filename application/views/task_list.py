"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- task_list.py --

@author: Informed Solutions

Handler for returning a list of tasks to be completed by a user when applying, coupled with the relevant status value
based on whether they have previously completed the task or not.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from ..models import (ApplicantPersonalDetails, Application, ChildcareType, ApplicantHomeAddress)
# noinspection PyTypeChecker
from ..utils import can_cancel


def show_hide_tasks(context, application):
    """
    Method hiding or showing the Your children and/or People in your home tasks based on whether the applicant has
    children and/or works in another childminder's home
    :param context: a dictionary containing all tasks for the task list
    :param context: Application object
    :return: dictionary object
    """

    for task in context['tasks']:
        if task['name'] == 'your_children':
            personal_detail_id = ApplicantPersonalDetails.get_id(app_id=application.application_id)
            applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                             current_address=True)
            location_of_childcare = applicant_home_address_record.childcare_address

            if location_of_childcare is False and application.own_children is True:
                task['hidden'] = False
            else:
                task['hidden'] = True
        if task['name'] == 'other_people':
            if application.working_in_other_childminder_home is True:
                task['hidden'] = True
            else:
                task['hidden'] = False
    return context


@never_cache
def task_list(request):
    """
    Method returning the template for the task-list (with current task status) for an applicant's application;
    logic is built in to enable the Declarations and Confirm your details tasks when all other tasks are complete
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered task list template
    """

    if request.method == 'GET':
        application_id = request.GET["id"]

    application = Application.objects.get(pk=application_id)

    # Add handlers to prevent a user re-accessing their application details and modifying post-submission
    if application.application_status == 'ARC_REVIEW' or application.application_status == 'SUBMITTED':
        return HttpResponseRedirect(
            reverse('Awaiting-Review-View') + '?id=' + str(application.application_id)
        )

    if application.application_status == 'ACCEPTED':
        return HttpResponseRedirect(
            reverse('Accepted-View') + '?id=' + str(application.application_id)
        )

    try:
        childcare_record = ChildcareType.objects.get(application_id=application_id)
    except Exception as e:
        return HttpResponseRedirect(reverse("Type-Of-Childcare-Guidance-View") + '?id=' + application_id)

    if application.personal_details_status == 'NOT_STARTED' or application.personal_details_status == 'IN_PROGRESS':
        return HttpResponseRedirect(reverse("Personal-Details-Name-View") + '?id=' + application_id)

    zero_to_five_status = childcare_record.zero_to_five
    five_to_eight_status = childcare_record.five_to_eight
    eight_plus_status = childcare_record.eight_plus

    # See childcare_type move to separate method/file

    if (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is True):
        registers = 'Early Years and Childcare Register (both parts)'
        fee = '£35'
    elif (zero_to_five_status is True) & (five_to_eight_status is True) & (eight_plus_status is False):
        registers = 'Early Years and Childcare Register (compulsory part)'
        fee = '£35'
    elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is True):
        registers = 'Early Years and Childcare Register (voluntary part)'
        fee = '£35'
    elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is True):
        registers = 'Childcare Register (both parts)'
        fee = '£103'
    elif (zero_to_five_status is True) & (five_to_eight_status is False) & (eight_plus_status is False):
        registers = 'Early Years Register'
        fee = '£35'
    elif (zero_to_five_status is False) & (five_to_eight_status is True) & (eight_plus_status is False):
        registers = 'Childcare Register (compulsory part)'
        fee = '£103'
    elif (zero_to_five_status is False) & (five_to_eight_status is False) & (eight_plus_status is True):
        registers = 'Childcare Register (voluntary part)'
        fee = '£103'

    """
    Variables which are passed to the template
    """

    context = {
        'id': application_id,
        'all_complete': False,
        'registers': registers,
        'fee': fee,
        'can_cancel': can_cancel(application),
        'application_status': application.application_status,
        'tasks': [
            {
                'name': 'account_details',  # This is CSS class (Not recommended to store it here)
                'status': application.login_details_status,
                'arc_flagged': application.login_details_arc_flagged,
                'description': "Your sign in details",
                'hidden': False,
                'status_url': None,  # Will be filled later
                'status_urls': [  # Available urls for each status
                    {'status': 'COMPLETED', 'url': 'Contact-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'Contact-Summary-View'},
                    {'status': 'OTHER', 'url': 'Contact-Email-View'},  # For all other statuses
                ],
            },
            {
                'name': 'children',
                'status': application.childcare_type_status,
                'arc_flagged': application.childcare_type_arc_flagged,
                'description': "Type of childcare",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Type-Of-Childcare-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'Type-Of-Childcare-Summary-View'},
                    {'status': 'OTHER', 'url': 'Type-Of-Childcare-Guidance-View'}
                ],
            },
            {
                'name': 'personal_details',
                'status': application.personal_details_status,
                'arc_flagged': application.personal_details_arc_flagged,
                'description': "Your personal details",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Personal-Details-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'Personal-Details-Summary-View'},
                    {'status': 'OTHER', 'url': 'Personal-Details-Name-View'}
                ],
            },
            {
                'name': 'your_children',
                'status': application.your_children_status,
                'arc_flagged': application.your_children_arc_flagged,
                'description': "Your children",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Your-Children-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'Your-Children-Summary-View'},
                    {'status': 'OTHER', 'url': 'Your-Children-Guidance-View'}
                ],
            },
            {
                'name': 'first_aid',
                'status': application.first_aid_training_status,
                'arc_flagged': application.first_aid_training_arc_flagged,
                'description': "First aid training",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'First-Aid-Training-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'First-Aid-Training-Summary-View'},
                    {'status': 'OTHER', 'url': 'First-Aid-Training-Guidance-View'}
                ],
            },
            {
                'name': 'eyfs',
                'status': application.childcare_training_status,
                'arc_flagged': application.childcare_training_arc_flagged,
                'description': 'Childcare training',
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Childcare-Training-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'Childcare-Training-Summary-View'},
                    {'status': 'OTHER', 'url': 'Childcare-Training-Guidance-View'}
                ],
            },
            {
                'name': 'health',
                'status': application.health_status,
                'arc_flagged': application.health_arc_flagged,
                'description': "Health declaration booklet",
                'hidden': True if not zero_to_five_status else False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Health-Check-Answers-View'},
                    {'status': 'FLAGGED', 'url': 'Health-Check-Answers-View'},
                    {'status': 'OTHER', 'url': 'Health-Intro-View'}
                ],
            },
            {
                'name': 'dbs',
                'status': application.criminal_record_check_status,
                'arc_flagged': application.criminal_record_check_arc_flagged,
                'description': "Criminal record checks",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'DBS-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'DBS-Summary-View'},
                    {'status': 'OTHER', 'url': 'DBS-Guidance-View'}
                ],
            },
            {
                'name': 'other_people',
                'status': application.people_in_home_status,
                'arc_flagged': application.people_in_home_arc_flagged,
                'description': "People in the home",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'PITH-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'PITH-Summary-View'},
                    {'status': 'WAITING', 'url': 'PITH-Summary-View'},
                    {'status': 'OTHER', 'url': 'PITH-Guidance-View'}
                ],
            },
            {
                'name': 'references',
                'status': application.references_status,
                'arc_flagged': application.references_arc_flagged,
                'description': "References",
                'hidden': True if not zero_to_five_status else False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'References-Summary-View'},
                    {'status': 'FLAGGED', 'url': 'References-Summary-View'},
                    {'status': 'OTHER', 'url': 'References-Intro-View'}
                ],
            },
            {
                'name': 'review',
                'status': None,
                'arc_flagged': application.application_status,
                # If application is being resubmitted (i.e. is not drafting,
                # set declaration task name to read "Declaration" only)
                'description':
                    "Declaration and payment" if application.application_status == 'DRAFTING' else "Declaration",
                'hidden': False,
                'status_url': None,
                'status_urls': [
                    {'status': 'COMPLETED', 'url': 'Declaration-Declaration-View'},
                    {'status': 'OTHER', 'url': 'Declaration-Summary-View'}
                ],
            },
        ]
    }

    # Show/hide Your children and People in your home tasks
    context = show_hide_tasks(context, application)

    unfinished_tasks = [task for task in context['tasks'] if not task['hidden'] and task['status'] in
                        ['IN_PROGRESS', 'NOT_STARTED', 'FLAGGED', 'WAITING']]

    if len(unfinished_tasks) < 1:
        context['all_complete'] = True
    else:
        task_names = [task['name'] for task in unfinished_tasks]
        if (not zero_to_five_status) and len(task_names) == 2 and 'health' in task_names and 'references' in task_names:
            context['all_complete'] = True
        else:
            context['all_complete'] = False

    if context['all_complete']:
        # Set declaration status to NOT_STARTED
        for task in context['tasks']:
            if task['name'] == 'review':
                if task['status'] is None:
                    task['status'] = application.declarations_status

    # Prepare task links
    for task in context['tasks']:

        # Iterating through tasks

        for url in task.get('status_urls'):  # Iterating through task available urls
            if url['status'] == task['status']:  # Match current task status with url which is in status_urls
                task['status_url'] = url['url']  # Set main task primary url to the one which matched

        if not task['status_url']:  # In case no matches were found by task status
            for url in task.get('status_urls'):  # Search for link with has status "OTHER"
                if url['status'] == "OTHER":
                    task['status_url'] = url['url']

    return render(request, 'task-list.html', context)
