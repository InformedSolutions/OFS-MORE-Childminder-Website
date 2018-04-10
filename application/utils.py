"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- utils.py --

@author: Informed Solutions
"""

from .models import Application, Reference, CriminalRecordCheck, EYFS, HealthDeclarationBooklet, ChildInHome, \
    ChildcareType, FirstAidTraining, ApplicantPersonalDetails, ApplicantName, ApplicantHomeAddress, AdultInHome


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


def can_cancel(application):
    """
    This method checks to see if the application status is in Drafting to see if it can be can be cancelled.
    :param application: application object
    :return: Boolean
    """
    if application.application_status == 'DRAFTING':
        can_cancel = True
    else:
        can_cancel = False

    return can_cancel
