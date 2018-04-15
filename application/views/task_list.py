"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- task_list.py --

@author: Informed Solutions

Handler for returning a list of tasks to be completed by a user when applying, coupled with the relevant status value
based on whether they have previously completed the task or not.
"""

from django.shortcuts import render

from application.models import (
    Application,
    ChildcareType,
    Arc)


# noinspection PyTypeChecker
from application.utils import can_cancel


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
        childcare_record = ChildcareType.objects.get(application_id=application_id)
        zero_to_five_status = childcare_record.zero_to_five
        five_to_eight_status = childcare_record.five_to_eight
        eight_plus_status = childcare_record.eight_plus

        #Instantiate arc_comment
        arc_comment = None

        # If an ARC review has been undertaken
        if Arc.objects.filter(application_id=application_id):
            arc = Arc.objects.get(application_id=application_id)
            arc_comment = arc.comments

        # See childcare_type move to seperate method/file

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

        ##




        """
        Variables which are passed to the template
        """

        context = {
            'id': application_id,
            'all_complete': False,
            'registers': registers,
            'arc_comment': arc_comment,
            'fee': fee,
            'can_cancel': can_cancel(application),
            'tasks': [
                {
                    'name': 'account_details',  # This is CSS class (Not recommended to store it here)
                    'status': application.login_details_status,
                    'description': "Your login details",
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
                    'description': "Type of childcare",
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
                    'description': "Your personal details",
                    'status_url': None,
                    'status_urls': [
                        {'status': 'COMPLETED', 'url': 'Personal-Details-Summary-View'},
                        {'status': 'FLAGGED', 'url': 'Personal-Details-Summary-View'},
                        {'status': 'OTHER', 'url': 'Personal-Details-Guidance-View'}
                    ],
                },
                {
                    'name': 'first_aid',
                    'status': application.first_aid_training_status,
                    'description': "First aid training",
                    'status_url': None,
                    'status_urls': [
                        {'status': 'COMPLETED', 'url': 'First-Aid-Training-Summary-View'},
                        {'status': 'FLAGGED', 'url': 'First-Aid-Training-Summary-View'},
                        {'status': 'OTHER', 'url': 'First-Aid-Training-Guidance-View'}
                    ],
                },
                {
                    'name': 'health',
                    'status': application.health_status,
                    'description': "Health declaration booklet",
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
                    'description': "Criminal record (DBS) check",
                    'status_url': None,
                    'status_urls': [
                        {'status': 'COMPLETED', 'url': 'DBS-Check-Summary-View'},
                        {'status': 'FLAGGED', 'url': 'DBS-Check-Summary-View'},
                        {'status': 'OTHER', 'url': 'DBS-Check-Guidance-View'}
                    ],
                },
                {
                    'name': 'other_people',
                    'status': application.people_in_home_status,
                    'description': "People in your home",
                    'status_url': None,
                    'status_urls': [
                        {'status': 'COMPLETED', 'url': 'Other-People-Summary-View'},
                        {'status': 'FLAGGED', 'url': 'Other-People-Summary-View'},
                        {'status': 'OTHER', 'url': 'Other-People-Guidance-View'}
                    ],
                },
                {
                    'name': 'references',
                    'status': application.references_status,
                    'description': "References",
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
                    'description': "Declaration and payment",
                    'status_url': None,
                    'status_urls': [
                        {'status': 'COMPLETED', 'url': 'Declaration-Declaration-View'},
                        {'status': 'OTHER', 'url': 'Declaration-Summary-View'}
                    ],
                },
            ]
        }

    # Declaratations state

    if len([task for task in context['tasks'] if task['status'] in ['IN_PROGRESS', 'NOT_STARTED']]) < 1:
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
