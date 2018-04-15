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
        return True
    else:
        return False

    return can_cancel


def date_formatter(day, month, year):
    """

    :param day: The day of the date to be formatted (should be integer on arrival)
    :param month: The month of the date to be formatted (should be integer on arrival)
    :param year: The year of the date to be formatted (should be integer on arrival)
    :return: The day, month, and year all formatted as strings with formatting specified in [CCN3-784]
    """

    output_day = str(day).zfill(2)
    output_month = str(month).zfill(2)
    output_year = str(year)

    return output_day, output_month, output_year
