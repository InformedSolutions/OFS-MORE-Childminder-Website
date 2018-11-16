import logging

from django.shortcuts import render
from timeline_logger.models import TimelineLog

from application.business_logic import get_childcare_register_type
from application.notify import send_email
from .. import status
from ..models import (Application, ApplicantName, UserDetails, CriminalRecordCheck)

log = logging.getLogger()


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

    template, is_early_years_register = get_template(criminal_record_check, application_id_local, local_app,
                                                     childcare_register_cost, childcare_register_type)

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
        'id': application_id_local,
        'order_code': request.GET["orderCode"],
        'conviction': conviction,
        'health_status': Application.objects.get(application_id=application_id_local).health_status,
        'cost': childcare_register_cost,
        'is_early_years_register': is_early_years_register
    }

    return render(request, template, variables)


def get_template(crc, app_id, application, cost, cr_type):
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
    cost = str(cost)
    early_years_register = 'EYR' in cr_type

    personalisation = {'ref': reference_number,
                       'firstName': first_name,
                       'cost': cost}

    log.debug(
        'Attempting to send a payment confirmation email with early_years_register: {0}; cr_type: {1}; cost: {2}; capita: {3}; cautions_convictions: {4}; lived_abroad: {5}'.format(
            early_years_register, cr_type, cost, capita, cautions_convictions, lived_abroad))
    if (capita and not cautions_convictions) and lived_abroad:
        if early_years_register:
            log.debug('Attempting send of email "Confirmation with HDB - lived abroad only email"')
        else:
            log.debug('Attempting send of email "Confirmation - lived abroad only"')

        email_template = '36720ba3-165e-40cd-a6d2-320daa9d6e4a' if early_years_register else 'f5a2998c-7322-4e32-8a85-72741bfec4a5'
        view_template = 'payment-confirmation-lived-abroad.html'

    elif (not capita or cautions_convictions) and lived_abroad:
        if early_years_register:
            log.debug('Attempting send of email "Confirmation with HDB - DBS & lived abroad"')
        else:
            log.debug('Attempting send of email "Confirmation - DBS & lived abroad"')

        email_template = 'c82b8ffd-f67c-4019-a724-d57ab559f08e' if early_years_register else '94190a2d-d1c7-46c6-8144-da38141aa027'
        view_template = 'payment-confirmation-health-dbs.html'

    elif (not capita or cautions_convictions) and not lived_abroad:
        if early_years_register:
            log.debug('Attempting send of email "Confirmation with HDB - DBS only"')
        else:
            log.debug('Attempting send of email "Confirmation - DBS only"')

        email_template = '02c01f75-1f9d-428f-a862-4effac03ebd3' if early_years_register else '294f2710-c507-4d30-ae64-b5451c59a45c'
        view_template = 'payment-confirmation-dbs-only.html'

    elif not lived_abroad and not cautions_convictions:
        if early_years_register:
            log.debug('Attempting send of email "Confirmation with HDB - no docs to send"')
        else:
            log.debug('Attempting send of email "Confirmation - no docs to send"')

        email_template = '8ca4eb7c-f4c9-417a-85e6-f4c10672f41a' if early_years_register else '75325ea2-c9b4-408c-9d89-c16ebbd7bd32'
        view_template = 'payment-confirmation-no-documents.html'

    else:
        raise ValueError("""
        The following combination is not covered in if block: 
        lived_abroad as {0}, 
        cautions_convictions as {1}, 
        capita as {2} """.format(lived_abroad, cautions_convictions, capita))

    send_payment_email(email, personalisation, email_template, application)
    send_survey_email(email, personalisation, application)

    return view_template, early_years_register


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


def send_survey_email(email, personalisation, application):
    """
    Sends an email if
    :param email: Applicant's email string
    :param personalisation: Applicant's details dictionary, presumed firstName and ref
    :param application: Application model instance
    :return: Void
    """
    survey_template_id = '90580388-f10d-440a-b900-4d5f948112a5'

    if application.application_status == 'DRAFTING':
        send_email(email, personalisation, survey_template_id)
