"""
Method returning the template for the account selection page
and navigating to the account: email page when clicking on
the Create an account button, which triggers the creation
of a new application
"""

from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from timeline_logger.models import TimelineLog

from ..models import Application, UserDetails
from ..forms import AccountForm


def account_selection(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered account selection template
    """
    if request.method == 'POST':

        application = Application.objects.create(
            application_type='CHILDMINDER',
            #login_id=user,
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='NOT_STARTED',
            personal_details_status='NOT_STARTED',
            childcare_type_status='NOT_STARTED',
            first_aid_training_status='NOT_STARTED',
            eyfs_training_status='COMPLETED',
            criminal_record_check_status='NOT_STARTED',
            health_status='NOT_STARTED',
            references_status='NOT_STARTED',
            people_in_home_status='NOT_STARTED',
            declarations_status='NOT_STARTED',
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_accepted=None,
            order_code=None
        )
        user = UserDetails.objects.create(application_id=application)

        app_id = str(application.application_id)

        TimelineLog.objects.create(
           content_object=application,
           user=None,
           template='timeline_logger/application_action.txt',
           extra_data={'user_type': 'applicant', 'action': 'created'}
        )

        return HttpResponseRedirect(
            reverse('Contact-Email-View') + '?id=' + app_id)

    form = AccountForm()
    variables = {
        'form': form
    }

    return render(request, 'account-account.html', variables)
