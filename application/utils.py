import json
from datetime import datetime

from .models import Application, Reference, CriminalRecordCheck, EYFS, HealthDeclarationBooklet, ChildInHome, \
    ChildcareType, FirstAidTraining, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, AdultInHome, \
    AuditLog


def get_app_task_models(app_id):
    """

    :param self:
    :return:
    """

    if app_id:

        models = [
            Application, Reference, CriminalRecordCheck, EYFS, HealthDeclarationBooklet, ChildInHome,
            ChildcareType, FirstAidTraining, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress,
            AdultInHome
        ]
        app_id_models = dict()

        for model in models:
            app_id_models[model.__name__] = getattr(model, 'get_id', None)

        return app_id_models

    return False


def trigger_audit_log(application_id, status):
    message = ''
    mydata = {'user': ''}
    if status == 'SUBMITTED':
        message = 'Submitted by applicant'
        mydata['user'] = 'Applicant'
    elif status == 'RESUBMITTED':
        message = 'Resubmitted - multiple tasks'
        mydata['user'] = 'Applicant'
    elif status == 'CREATED':
        message = 'Application has been created'
        mydata['user'] = 'Applicant'
    mydata['message'] = message
    mydata['date'] = str(datetime.today().strftime("%d/%m/%Y"))
    if AuditLog.objects.filter(application_id=application_id).count() == 1:
        log = AuditLog.objects.get(application_id=application_id)
        log.audit_message = log.audit_message[:-1] + ',' + json.dumps(mydata) + ']'
        log.save()
    else:
        log = AuditLog.objects.create(
            application_id=application_id, audit_message='[' + json.dumps(mydata) + ']')
