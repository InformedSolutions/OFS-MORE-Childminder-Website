from django.shortcuts import render
from timeline_logger.models import TimelineLog

from application.business_logic import get_childcare_register_type
from ..models import (Application, ApplicantName, UserDetails, CriminalRecordCheck)
from .. import status

from application.notify import send_email


def payment_confirmation(request):
    """
    Method returning the template for the Payment confirmation page (for a given application)
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment confirmation template
    """
    application_id_local = request.GET['id']
    try:
        criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
        conviction = CriminalRecordCheck.objects.get(application_id=application_id_local).cautions_convictions
    except CriminalRecordCheck.DoesNotExist:
        criminal_record_check = None
        conviction = False

    local_app = Application.objects.get(
        application_id=application_id_local)

    childcare_register_type, childcare_register_cost = get_childcare_register_type(application_id_local)

    template = get_template(criminal_record_check, application_id_local, local_app, childcare_register_cost)

    local_app.application_status = 'SUBMITTED'
    local_app.save()
    status.update(application_id_local, 'declarations_status', 'COMPLETED')

    # Payment presents the first true trigger for submission so is logged as submitted at this point
    TimelineLog.objects.create(
        content_object=local_app,
        user=None,
        template='timeline_logger/application_action.txt',
        extra_data={'user_type': 'applicant', 'action': 'submitted by', 'entity': 'application'}
    )

    variables = {
        'application_id': application_id_local,
        'order_code': request.GET["orderCode"],
        'conviction': conviction,
        'health_status': Application.objects.get(application_id=application_id_local).health_status,
        'cost': childcare_register_cost
    }

    return render(request, template, variables)

def get_template(crc, app_id, application, cost):
    lived_abroad = crc.lived_abroad
    capita = crc.capita
    if capita:
        cautions_convictions = crc.cautions_convictions
    else:
        cautions_convictions = False

    applicant_name = ApplicantName.objects.get(application_id=app_id)
    user_details = UserDetails.objects.get(application_id=app_id)

    reference_number = application.application_reference
    first_name = applicant_name.first_name
    email = user_details.email
    cost = str(35)

    personalisation = {'ref': reference_number,
                       'firstName': first_name,
                       'cost': cost}

    if (capita and not cautions_convictions) and lived_abroad:
        send_payment_email(email, personalisation, '36720ba3-165e-40cd-a6d2-320daa9d6e4a', application)
        return 'payment-confirmation-lived-abroad.html'

    elif (not capita or cautions_convictions) and lived_abroad:
        send_payment_email(email, personalisation, 'c82b8ffd-f67c-4019-a724-d57ab559f08e', application)
        return 'payment-confirmation-health-dbs.html'

    elif (not capita or cautions_convictions) and not lived_abroad:
        send_payment_email(email, personalisation, '02c01f75-1f9d-428f-a862-4effac03ebd3', application)
        return 'payment-confirmation-dbs-only.html'

    elif not lived_abroad and not cautions_convictions:
        send_payment_email(email, personalisation, '8ca4eb7c-f4c9-417a-85e6-f4c10672f41a', application)
        return 'payment-confirmation-no-documents.html'

    else:
        raise ValueError("""
        The following combination is not covered in if block: 
        lived_abroad as {0}, 
        cautions_convictions as {1}, 
        capita as {2} """.format(lived_abroad, cautions_convictions, capita))


def send_payment_email(email, personalisation, template_id, application):
    """
    Sends an email if
    :param email: Applicant's email string
    :param personalisation: Applicant's details dictionary, presumed firstName and ref
    :param template_id: Template id of the email
    :param application: Application model instance
    :return: Void
    """
    if application.application_status == 'DRAFTING':
        send_email(email, personalisation, template_id)
        
