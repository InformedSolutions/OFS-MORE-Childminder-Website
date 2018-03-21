"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- views.py --

@author: Informed Solutions
"""

import datetime
import json
import re
import time
import logging
from datetime import date
from uuid import UUID

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from .. import address_helper, magic_link, payment, status
from ..business_logic import (childcare_type_logic,
                              dbs_check_logic,
                              eyfs_knowledge_logic,
                              eyfs_questions_logic,
                              eyfs_training_logic,
                              first_aid_logic,
                              health_check_logic,
                              login_contact_logic,
                              login_contact_logic_phone,
                              multiple_childcare_address_logic,
                              other_people_adult_details_logic,
                              other_people_children_details_logic,
                              personal_dob_logic,
                              personal_home_address_logic,
                              personal_location_of_care_logic,
                              personal_name_logic,
                              rearrange_adults,
                              rearrange_children,
                              references_first_reference_logic,
                              references_second_reference_logic,
                              remove_adult,
                              remove_child,
                              reset_declaration)

from ..forms import (AccountForm,
                     ApplicationSavedForm,
                     ContactEmailForm,
                     ContactPhoneForm,
                     ContactSummaryForm,
                     DBSCheckDBSDetailsForm,
                     DBSCheckGuidanceForm,
                     DBSCheckSummaryForm,
                     DBSCheckUploadDBSForm,
                     DeclarationIntroForm,
                     DeclarationDeclarationForm,
                     DeclarationDeclarationForm2,
                     DeclarationSummaryForm,
                     DocumentsNeededForm,
                     EYFSGuidanceForm,
                     EYFSKnowledgeForm,
                     EYFSQuestionsForm,
                     EYFSSummaryForm,
                     EYFSTrainingForm,
                     FirstAidTrainingDeclarationForm,
                     FirstAidTrainingDetailsForm,
                     FirstAidTrainingGuidanceForm,
                     FirstAidTrainingRenewForm,
                     FirstAidTrainingSummaryForm,
                     FirstAidTrainingTrainingForm,
                     FirstReferenceForm,
                     HealthBookletForm,
                     HealthIntroForm,
                     HomeReadyForm,
                     OtherPeopleAdultDBSForm,
                     OtherPeopleAdultDetailsForm,
                     OtherPeopleAdultPermissionForm,
                     OtherPeopleAdultQuestionForm,
                     OtherPeopleApproaching16Form,
                     OtherPeopleChildrenDetailsForm,
                     OtherPeopleChildrenQuestionForm,
                     OtherPeopleGuidanceForm,
                     OtherPeopleSummaryForm,
                     PaymentDetailsForm,
                     PaymentForm,
                     PersonalDetailsChildcareAddressForm,
                     PersonalDetailsChildcareAddressLookupForm,
                     PersonalDetailsChildcareAddressManualForm,
                     PersonalDetailsDOBForm,
                     PersonalDetailsGuidanceForm,
                     PersonalDetailsHomeAddressForm,
                     PersonalDetailsHomeAddressLookupForm,
                     PersonalDetailsHomeAddressManualForm,
                     PersonalDetailsLocationOfCareForm,
                     PersonalDetailsNameForm,
                     PersonalDetailsSummaryForm,
                     PrepareForInterviewForm,
                     QuestionForm,
                     ReferenceFirstReferenceAddressForm,
                     ReferenceFirstReferenceAddressLookupForm,
                     ReferenceFirstReferenceAddressManualForm,
                     ReferenceFirstReferenceContactForm,
                     ReferenceIntroForm,
                     ReferenceSecondReferenceAddressForm,
                     ReferenceSecondReferenceAddressLookupForm,
                     ReferenceSecondReferenceAddressManualForm,
                     ReferenceSecondReferenceContactForm,
                     ReferenceSummaryForm,
                     SecondReferenceForm,
                     TypeOfChildcareAgeGroupsForm,
                     TypeOfChildcareGuidanceForm,
                     TypeOfChildcareRegisterForm)

from ..middleware import CustomAuthenticationHandler
from ..models import (AdultInHome,
                      ApplicantHomeAddress,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      AuditLog,
                      ChildInHome,
                      ChildcareType,
                      CriminalRecordCheck,
                      EYFS,
                      FirstAidTraining,
                      HealthDeclarationBooklet,
                      Reference,
                      UserDetails)

# initiate logging
log = logging.getLogger('django.server')


def error_404(request):
    """
    Method returning the 404 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 404 error template
    """
    data = {}
    return render(request, '404.html', data)


def error_500(request):
    """
    Method returning the 500 error template
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 500 error template
    """
    data = {}
    return render(request, '500.html', data)


def start_page(request):
    """
    Method returning the template for the start page
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered start page template
    """
    return render(request, 'start-page.html')


def first_aid_training_guidance(request):
    """
    Method returning the template for the First aid training: guidance page (for a given application)
    and navigating to the First aid training: details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingGuidanceForm()
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingGuidanceForm(request.POST)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.first_aid_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'first_aid_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/details?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-training-guidance.html', variables)


def first_aid_training_details(request):
    """
    Method returning the template for the First aid training: details page (for a given application)
    and navigating to the First aid training: renew, declaration or training page depending on
    the age of the first aid training certificate when successfully completed;
    business logic is applied to either create or update the associated First_Aid_Training record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDetailsForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'first_aid_training_status', 'IN_PROGRESS')

        form = FirstAidTrainingDetailsForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update First_Aid_Training record
            first_aid_training_record = first_aid_logic(
                application_id_local, form)
            first_aid_training_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # Calculate certificate age and determine which page to navigate to
            certificate_day = form.cleaned_data.get('course_date')[0]
            certificate_month = form.cleaned_data.get('course_date')[1]
            certificate_year = form.cleaned_data.get('course_date')[2]
            certificate_date = date(
                certificate_year, certificate_month, certificate_day)
            today = date.today()
            certificate_date_difference = today - certificate_date
            certificate_age = certificate_date_difference.days / 365
            if certificate_age < 2.5:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/certificate?id=' + application_id_local)
            elif 2.5 <= certificate_age < 3:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/renew?id=' + application_id_local)
            elif certificate_age >= 3:
                return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/update?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with your course details'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-details.html', variables)


def first_aid_training_declaration(request):
    """
    Method returning the template for the First aid training: declaration page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: declaration template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingDeclarationForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-declaration.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingDeclarationForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            declaration = form.cleaned_data.get('declaration')
            first_aid_record = FirstAidTraining.objects.get(
                application_id=application_id_local)
            first_aid_record.show_certificate = declaration
            first_aid_record.renew_certificate = False
            first_aid_record.save()
            status.update(application_id_local,
                          'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-declaration.html', variables)


def first_aid_training_renew(request):
    """
    Method returning the template for the First aid training: renew page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: renew template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingRenewForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-renew.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingRenewForm(request.POST, id=application_id_local)
        form.remove_flag()
        if form.is_valid():
            renew = form.cleaned_data.get('renew')
            first_aid_record = FirstAidTraining.objects.get(
                application_id=application_id_local)
            first_aid_record.renew_certificate = renew
            first_aid_record.show_certificate = False
            first_aid_record.save()
            status.update(application_id_local,
                          'first_aid_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-renew.html', variables)


def first_aid_training_training(request):
    """
    Method returning the template for the First aid training: training page (for a given application)
    and navigating to the First aid training: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: training template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstAidTrainingTrainingForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-training.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingTrainingForm(request.POST)
        if form.is_valid():
            first_aid_record = FirstAidTraining.objects.get(
                application_id=application_id_local)
            first_aid_record.show_certificate = False
            first_aid_record.renew_certificate = False
            first_aid_record.save()
            status.update(application_id_local,
                          'first_aid_training_status', 'NOT_STARTED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/first-aid/check-answers?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-training.html', variables)


def first_aid_training_summary(request):
    """
    Method returning the template for the First aid training: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered First aid training: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_aid_record = FirstAidTraining.objects.get(
            application_id=application_id_local)
        form = FirstAidTrainingSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'training_organisation': first_aid_record.training_organisation,
            'training_course': first_aid_record.course_title,
            'certificate_day': first_aid_record.course_day,
            'certificate_month': first_aid_record.course_month,
            'certificate_year': first_aid_record.course_year,
            'renew_certificate': first_aid_record.renew_certificate,
            'show_certificate': first_aid_record.show_certificate,
            'first_aid_training_status': application.first_aid_training_status
        }
        return render(request, 'first-aid-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstAidTrainingSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'first-aid-summary.html', variables)


def eyfs_guidance(request):
    """
    Method returning the template for the Early Years knowledge guidance page (for a given application) and navigating
    to the EYFS knowledge page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        if application.eyfs_training_status != 'COMPLETED':
            status.update(application_id_local,
                          'eyfs_training_status', 'IN_PROGRESS')
        return render(request, 'eyfs-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/knowledge?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-guidance.html', variables)


def eyfs_knowledge(request):
    """
    Method returning the template for the Early Years knowledge: knowledge page (for a given application)
    and navigating to the Early Years knowledge: training or question page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: knowledge template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSKnowledgeForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-knowledge.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSKnowledgeForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            # Create or update EYFS record
            eyfs_record = eyfs_knowledge_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            eyfs_understand = form.cleaned_data['eyfs_understand']
            if eyfs_understand == 'True':
                eyfs_record = EYFS.objects.get(
                    application_id=application_id_local)
                eyfs_record.eyfs_training_declare = False
                eyfs_record.save()
                reset_declaration(application)
                return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/questions?id=' + application_id_local)
            elif eyfs_understand == 'False':
                return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/training?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-knowledge.html', variables)


def eyfs_training(request):
    """
    Method returning the template for the Early Years knowledge: training page (for a given application)
    and navigating to the Early Years knowledge: question page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: training template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSTrainingForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-training.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSTrainingForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            # Create or update EYFS record
            eyfs_record = eyfs_training_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/questions?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-training.html', variables)


def eyfs_questions(request):
    """
    Method returning the template for the Early Years knowledge: questions page (for a given application)
    and navigating to the Early Years knowledge: summary page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: questions template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSQuestionsForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_declare': eyfs_record.eyfs_training_declare,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-questions.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSQuestionsForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update EYFS record
            eyfs_record = eyfs_questions_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-questions.html', variables)


def eyfs_summary(request):
    """
    Method returning the template for the Early Years knowledge: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early years knowledge: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        eyfs_understand = eyfs_record.eyfs_understand
        eyfs_training_declare = eyfs_record.eyfs_training_declare
        share_info_declare = eyfs_record.share_info_declare
        form = EYFSSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_understand': eyfs_understand,
            'eyfs_training_declare': eyfs_training_declare,
            'share_info_declare': share_info_declare,
            'eyfs_training_status': application.eyfs_training_status,
        }
        return render(request, 'eyfs-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-summary.html', variables)


def dbs_check_guidance(request):
    """
    Method returning the template for the Your criminal record (DBS) check: guidance page (for a given application)
    and navigating to the Your criminal record (DBS) check: details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DBSCheckGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local,
                              'criminal_record_check_status', 'IN_PROGRESS')
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/criminal-record/your-details?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-guidance.html', variables)


def dbs_check_dbs_details(request):
    """
    Method returning the template for the Your criminal record (DBS) check: details page (for a given application)
    and navigating to the Your criminal record (DBS) check: upload DBS or summary page when successfully completed;
    business logic is applied to either create or update the associated Criminal_Record_Check record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckDBSDetailsForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-dbs-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'criminal_record_check_status', 'IN_PROGRESS')

        form = DBSCheckDBSDetailsForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update Criminal_Record_Check record
            dbs_check_record = dbs_check_logic(application_id_local, form)
            dbs_check_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            cautions_convictions = form.cleaned_data['convictions']
            if cautions_convictions == 'True':
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/criminal-record/post-certificate?id=' + application_id_local)
            elif cautions_convictions == 'False':
                if application.criminal_record_check_status != 'COMPLETED':
                    status.update(application_id_local,
                                  'criminal_record_check_status', 'COMPLETED')
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/criminal-record/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with your DBS details'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-dbs-details.html', variables)


def dbs_check_upload_dbs(request):
    """
    Method returning the template for the Your criminal record (DBS) check: upload DBS page (for a given application)
    and navigating to the Your criminal record (DBS) check: summary page when successfully completed;
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: upload DBS template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DBSCheckUploadDBSForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'criminal_record_check_status': application.criminal_record_check_status
        }
        return render(request, 'dbs-check-upload-dbs.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DBSCheckUploadDBSForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            declare = form.cleaned_data['declaration']
            dbs_check_record = CriminalRecordCheck.objects.get(
                application_id=application_id_local)
            dbs_check_record.send_certificate_declare = declare
            dbs_check_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.criminal_record_check_status != 'COMPLETED':
                status.update(application_id_local,
                              'criminal_record_check_status', 'COMPLETED')
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/criminal-record/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem on this page'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-upload-dbs.html', variables)


def dbs_check_summary(request):
    """
    Method returning the template for the Your criminal record (DBS) check: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your criminal record (DBS) check: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        criminal_record_check = CriminalRecordCheck.objects.get(
            application_id=application_id_local)
        dbs_certificate_number = criminal_record_check.dbs_certificate_number
        cautions_convictions = criminal_record_check.cautions_convictions
        send_certificate_declare = criminal_record_check.send_certificate_declare
        form = DBSCheckSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'dbs_certificate_number': dbs_certificate_number,
            'cautions_convictions': cautions_convictions,
            'criminal_record_check_status': application.criminal_record_check_status,
            'declaration': send_certificate_declare
        }
        return render(request, 'dbs-check-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DBSCheckSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'dbs-check-summary.html', variables)


def health_intro(request):
    """
    Method returning the template for the Your health: intro page (for a given application)
    and navigating to the Your health: intro page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: intro template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = HealthIntroForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }
        return render(request, 'health-intro.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthIntroForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.health_status != 'COMPLETED':
                status.update(application_id_local,
                              'health_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/booklet?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-intro.html', variables)


def health_booklet(request):
    """
    Method returning the template for the Your health: booklet page (for a given application)
    and navigating to the Your health: answers page when successfully completed;
    business logic is applied to either create or update the associated Health_Declaration_Booklet record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: booklet template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = HealthBookletForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'health_status': application.health_status
        }
        return render(request, 'health-booklet.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthBookletForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update Health_Declaration_Booklet record
            hdb_record = health_check_logic(application_id_local, form)
            hdb_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.health_status != 'COMPLETED':
                status.update(application_id_local,
                              'health_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/health/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with this page.'
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-booklet.html', variables)


def health_check_answers(request):
    """
    Method returning the template for the Your health: answers page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your health: answers template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        send_hdb_declare = HealthDeclarationBooklet.objects.get(
            application_id=application_id_local).send_hdb_declare
        form = HealthBookletForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'send_hdb_declare': send_hdb_declare,
            'health_status': application.health_status,
        }
        return render(request, 'health-check-answers.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = HealthBookletForm(request.POST, id=application_id_local)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'health-check-answers.html', variables)


def references_intro(request):
    """
    Method returning the template for the 2 references: intro page (for a given application)
    and navigating to the Your health: intro page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: intro template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceIntroForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-intro.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceIntroForm(request.POST)
        application = Application.objects.get(pk=application_id_local)

        # Default status to in progress irrespective of choices made
        status.update(application_id_local, 'references_status', 'IN_PROGRESS')

        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-intro.html', variables)


def references_first_reference(request):
    """
    Method returning the template for the 2 references: first reference page (for a given application)
    and navigating to the 2 references: first reference address page when successfully completed;
    business logic is applied to either create or update the associated Reference record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = FirstReferenceForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = FirstReferenceForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            # Create or update Reference record
            references_record = references_first_reference_logic(
                application_id_local, form)
            references_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-address?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-first-reference.html', variables)


def references_first_reference_address(request):
    """
    Method returning the template for the 2 references: first reference address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            postcode = form.cleaned_data.get('postcode')
            first_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=1)
            first_reference_record.postcode = postcode
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/select-first-reference-address/?id='
                                            + application_id_local)
            if 'submit' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/enter-first-reference-address/?id='
                                            + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's postcode"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address.html', variables)


def references_first_reference_address_select(request):
    """
    Method returning the template for the 2 references: first reference select address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference select address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        postcode = first_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(
            postcode)
        if len(addresses) != 0:
            form = ReferenceFirstReferenceAddressLookupForm(
                id=application_id_local, choices=addresses)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'postcode': postcode,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-lookup.html', variables)
        else:
            form = ReferenceFirstReferenceAddressForm(id=application_id_local)
            form.check_flag()
            form.errors['postcode'] = {'Please enter a valid postcode.': 'invalid'}
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'references-first-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        postcode = first_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = ReferenceFirstReferenceAddressLookupForm(request.POST, id=application_id_local, choices=addresses)
        form.remove_flag()
        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            first_reference_record.street_line1 = line1
            first_reference_record.street_line2 = line2
            first_reference_record.town = town
            first_reference_record.county = ''
            first_reference_record.postcode = postcode
            first_reference_record.country = 'United Kingdom'
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local, 'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem finding the referee's address"
            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-lookup.html', variables)


def references_first_reference_address_manual(request):
    """
    Method returning the template for the 2 references: first reference manual address page (for a given application)
    and navigating to the 2 references: first reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference manual address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressManualForm(id=application_id_local)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceFirstReferenceAddressManualForm(request.POST, id=application_id_local)
        form.remove_flag()
        if form.is_valid():
            street_name_and_number = form.cleaned_data.get(
                'street_name_and_number')
            street_name_and_number2 = form.cleaned_data.get(
                'street_name_and_number2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
            first_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=1)
            first_reference_record.street_line1 = street_name_and_number
            first_reference_record.street_line2 = street_name_and_number2
            first_reference_record.town = town
            first_reference_record.county = county
            first_reference_record.postcode = postcode
            first_reference_record.country = country
            first_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/first-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's address"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-first-reference-address-manual.html', variables)


def references_first_reference_contact_details(request):
    """
    Method returning the template for the 2 references: first reference contact details page (for a given application)
    and navigating to the 2 references: second reference page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: first reference contact details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceFirstReferenceContactForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-first-reference-contact-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceFirstReferenceContactForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')
            references_first_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                              reference=1)
            references_first_reference_address_record.phone_number = phone_number
            references_first_reference_address_record.email = email_address
            references_first_reference_address_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference?id=' + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's contact details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-first-reference-contact-details.html', variables)


def references_second_reference(request):
    """
    Method returning the template for the 2 references: second reference page (for a given application)
    and navigating to the 2 references: second reference address page when successfully completed;
    business logic is applied to either create or update the associated Reference record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = SecondReferenceForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = SecondReferenceForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            # Create or update Reference record
            references_record = references_second_reference_logic(
                application_id_local, form)
            references_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-address?id=' +
                                        application_id_local + '&manual=False&lookup=False')
        else:
            form.error_summary_title = "There was a problem with the referee's details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-second-reference.html', variables)


def references_second_reference_address(request):
    """
    Method returning the template for the 2 references: second reference address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressForm(id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressForm(
            request.POST, id=application_id_local)
        if form.is_valid():
            postcode = form.cleaned_data.get('postcode')
            second_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=2)
            second_reference_record.postcode = postcode
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if 'postcode-search' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/select-second-reference-address/?id='
                                            + application_id_local)
            if 'submit' in request.POST:
                return HttpResponseRedirect(settings.URL_PREFIX + '/references/enter-second-reference-address/?id='
                                            + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's postcode"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address.html', variables)


def references_second_reference_address_select(request):
    """
    Method returning the template for the 2 references: second reference select address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference select address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        postcode = second_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(
            postcode)
        if len(addresses) != 0:
            form = ReferenceSecondReferenceAddressLookupForm(
                id=application_id_local, choices=addresses)
            variables = {
                'form': form,
                'application_id': application_id_local,
                'postcode': postcode,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-lookup.html', variables)
        else:
            form = ReferenceSecondReferenceAddressForm(id=application_id_local)
            form.check_flag()
            form.errors['postcode'] = {'Please enter a valid postcode.': 'invalid'}
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'references-second-reference-address.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        postcode = second_reference_record.postcode
        addresses = address_helper.AddressHelper.create_address_lookup_list(postcode)
        form = ReferenceSecondReferenceAddressLookupForm(request.POST, id=application_id_local, choices=addresses)
        form.remove_flag()
        if form.is_valid():
            selected_address_index = int(request.POST["address"])
            selected_address = address_helper.AddressHelper.get_posted_address(
                selected_address_index, postcode)
            line1 = selected_address['line1']
            line2 = selected_address['line2']
            town = selected_address['townOrCity']
            postcode = selected_address['postcode']
            second_reference_record.street_line1 = line1
            second_reference_record.street_line2 = line2
            second_reference_record.town = town
            second_reference_record.county = ''
            second_reference_record.postcode = postcode
            second_reference_record.country = 'United Kingdom'
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            if Application.objects.get(pk=application_id_local).references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem finding the referee's address"
            variables = {
                'postcode': postcode,
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-lookup.html', variables)


def references_second_reference_address_manual(request):
    """
    Method returning the template for the 2 references: second reference manual address page (for a given application)
    and navigating to the 2 references: second reference contact details page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference manual address template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressManualForm(id=application_id_local)
        form.check_flag()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-address-manual.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)
        form = ReferenceSecondReferenceAddressManualForm(request.POST, id=application_id_local)
        form.remove_flag()
        if form.is_valid():
            street_name_and_number = form.cleaned_data.get(
                'street_name_and_number')
            street_name_and_number2 = form.cleaned_data.get(
                'street_name_and_number2')
            town = form.cleaned_data.get('town')
            county = form.cleaned_data.get('county')
            postcode = form.cleaned_data.get('postcode')
            country = form.cleaned_data.get('country')
            second_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=2)
            second_reference_record.street_line1 = street_name_and_number
            second_reference_record.street_line2 = street_name_and_number2
            second_reference_record.town = town
            second_reference_record.county = county
            second_reference_record.postcode = postcode
            second_reference_record.country = country
            second_reference_record.save()
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.references_status != 'COMPLETED':
                status.update(application_id_local,
                              'references_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/second-reference-contact-details?id=' +
                                        application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's address"
            variables = {
                'form': form,
                'application_id': application_id_local,
                'references_status': application.references_status
            }
            return render(request, 'references-second-reference-address-manual.html', variables)


def references_second_reference_contact_details(request):
    """
    Method returning the template for the 2 references: second reference contact details page (for a given application)
    and navigating to the 2 references: summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: second reference contact details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = ReferenceSecondReferenceContactForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'references_status': application.references_status
        }
        return render(request, 'references-second-reference-contact-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceSecondReferenceContactForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            status.update(application_id_local,
                          'references_status', 'COMPLETED')
            email_address = form.cleaned_data.get('email_address')
            phone_number = form.cleaned_data.get('phone_number')
            references_second_reference_address_record = Reference.objects.get(application_id=application_id_local,
                                                                               reference=2)
            references_second_reference_address_record.phone_number = phone_number
            references_second_reference_address_record.email = email_address
            references_second_reference_address_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/references/check-answers?id=' + application_id_local)
        else:
            form.error_summary_title = "There was a problem with the referee's contact details"
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-second-reference-contact-details.html', variables)


def references_summary(request):
    """
    Method returning the template for the 2 references: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered 2 references: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        first_reference_first_name = first_reference_record.first_name
        first_reference_last_name = first_reference_record.last_name
        first_reference_relationship = first_reference_record.relationship
        first_reference_years_known = first_reference_record.years_known
        first_reference_months_known = first_reference_record.months_known
        first_reference_street_line1 = first_reference_record.street_line1
        first_reference_street_line2 = first_reference_record.street_line2
        first_reference_town = first_reference_record.town
        first_reference_county = first_reference_record.county
        first_reference_country = first_reference_record.country
        first_reference_postcode = first_reference_record.postcode
        first_reference_phone_number = first_reference_record.phone_number
        first_reference_email = first_reference_record.email
        second_reference_first_name = second_reference_record.first_name
        second_reference_last_name = second_reference_record.last_name
        second_reference_relationship = second_reference_record.relationship
        second_reference_years_known = second_reference_record.years_known
        second_reference_months_known = second_reference_record.months_known
        second_reference_street_line1 = second_reference_record.street_line1
        second_reference_street_line2 = second_reference_record.street_line2
        second_reference_town = second_reference_record.town
        second_reference_county = second_reference_record.county
        second_reference_country = second_reference_record.country
        second_reference_postcode = second_reference_record.postcode
        second_reference_phone_number = second_reference_record.phone_number
        second_reference_email = second_reference_record.email
        form = ReferenceSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        status.update(application_id_local, 'references_status', 'COMPLETED')
        variables = {
            'form': form,
            'application_id': application_id_local,
            'first_reference_first_name': first_reference_first_name,
            'first_reference_last_name': first_reference_last_name,
            'first_reference_relationship': first_reference_relationship,
            'first_reference_years_known': first_reference_years_known,
            'first_reference_months_known': first_reference_months_known,
            'first_reference_street_line1': first_reference_street_line1,
            'first_reference_street_line2': first_reference_street_line2,
            'first_reference_town': first_reference_town,
            'first_reference_county': first_reference_county,
            'first_reference_country': first_reference_country,
            'first_reference_postcode': first_reference_postcode,
            'first_reference_phone_number': first_reference_phone_number,
            'first_reference_email': first_reference_email,
            'second_reference_first_name': second_reference_first_name,
            'second_reference_last_name': second_reference_last_name,
            'second_reference_relationship': second_reference_relationship,
            'second_reference_years_known': second_reference_years_known,
            'second_reference_months_known': second_reference_months_known,
            'second_reference_street_line1': second_reference_street_line1,
            'second_reference_street_line2': second_reference_street_line2,
            'second_reference_town': second_reference_town,
            'second_reference_county': second_reference_county,
            'second_reference_country': second_reference_country,
            'second_reference_postcode': second_reference_postcode,
            'second_reference_phone_number': second_reference_phone_number,
            'second_reference_email': second_reference_email,
            'references_status': application.references_status
        }
        return render(request, 'references-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = ReferenceSummaryForm()
        if form.is_valid():
            status.update(application_id_local,
                          'references_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'references-summary.html', variables)


def other_people_guidance(request):
    """
    Method returning the template for the People in your home: guidance page (for a given application)
    and navigating to the People in your home: adult question page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-question?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-guidance.html', variables)


def other_people_adult_question(request):
    """
    Method returning the template for the People in your home: adult question page (for a given application) and
    navigating to the People in your home: adult details or People in your home: children details page when
    successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult question template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleAdultQuestionForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'people_in_home_status', 'IN_PROGRESS')

        form = OtherPeopleAdultQuestionForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        number_of_adults = AdultInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            adults_in_home = form.cleaned_data.get('adults_in_home')
            application.adults_in_home = adults_in_home
            application.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            # If adults live in your home, navigate to adult details page
            if adults_in_home == 'True':
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-details?id=' +
                                            application_id_local + '&adults=' + str(number_of_adults) + '&remove=0')
            # If adults do not live in your home, navigate to children question page
            elif adults_in_home == 'False':
                # Delete any existing adults
                adults = AdultInHome.objects.filter(
                    application_id=application_id_local)
                for adult in adults:
                    adult.delete()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-question?id=' +
                                            application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-adult-question.html', variables)


def other_people_adult_details(request):
    """
    Method returning the template for the People in your home: adult details page (for a given application) and
    navigating to the People in your home: adult DBS page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        remove_person = int(request.GET["remove"])
        remove_button = True
        # If there are no adults in the database
        if number_of_adults == 0:
            # Set the number of adults to 1 to initialise one instance of the form
            number_of_adults = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one adult in the database
        if number_of_adults == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Remove specific adult if remove button is pressed
        remove_adult(application_id_local, remove_person)
        # Rearrange adult numbers if there are gaps
        rearrange_adults(number_of_adults, application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_adults + 1):
            form = OtherPeopleAdultDetailsForm(
                id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'remove_adult': number_of_adults - 1,
            'remove_button': remove_button,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        remove_button = True
        # If there are no adults in the database
        if number_of_adults == 0:
            # Set the number of adults to 1 to initialise one instance of the form
            number_of_adults = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one adult in the database
        if number_of_adults == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        for i in range(1, int(number_of_adults) + 1):
            form = OtherPeopleAdultDetailsForm(
                request.POST, id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
            if form.is_valid():
                adult_record = other_people_adult_details_logic(
                    application_id_local, form, i)
                adult_record.save()
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
                    'people_in_home_status': application.people_in_home_status
                }
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-dbs?id=' + application_id_local +
                                            '&adults=' + number_of_adults, variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_adults': number_of_adults,
                    'add_adult': int(number_of_adults) + 1,
                    'remove_adult': int(number_of_adults) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-adult-details.html', variables)
        if 'add_person' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                add_adult = int(number_of_adults) + 1
                add_adult_string = str(add_adult)
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/other-people/adult-details?id=' +
                    application_id_local + '&adults=' + add_adult_string + '&remove=0',
                    variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_adults': number_of_adults,
                    'add_adult': int(number_of_adults) + 1,
                    'remove_adult': int(number_of_adults) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-adult-details.html', variables)


def other_people_adult_dbs(request):
    """
    Method returning the template for the People in your home: adult DBS page (for a given application) and
    navigating to the People in your home: adult permission page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult DBS template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_adults + 1):
            adult = AdultInHome.objects.get(
                application_id=application_id_local, adult=i)
            if adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            elif adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            form = OtherPeopleAdultDBSForm(
                id=application_id_local, adult=i, prefix=i, name=name)
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-dbs.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        for i in range(1, int(number_of_adults) + 1):
            adult = AdultInHome.objects.get(
                application_id=application_id_local, adult=i)
            # Generate name to pass to form, for display in HTML
            if adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            elif adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            form = OtherPeopleAdultDBSForm(
                request.POST, id=application_id_local, adult=i, prefix=i, name=name)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
            if form.is_valid():
                adult_record = AdultInHome.objects.get(
                    application_id=application_id_local, adult=i)
                adult_record.dbs_certificate_number = form.cleaned_data.get(
                    'dbs_certificate_number')
                adult_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                valid_list.append(True)
            else:
                valid_list.append(False)
        # If all forms are valid
        if False not in valid_list:
            variables = {
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/adult-permission?id=' +
                                        application_id_local + '&adults=' + number_of_adults, variables)
        # If there is an invalid form
        elif False in valid_list:
            variables = {
                'form_list': form_list,
                'application_id': application_id_local,
                'number_of_adults': number_of_adults,
                'add_adult': int(number_of_adults) + 1,
                'people_in_home_status': application.people_in_home_status
            }
            return render(request, 'other-people-adult-dbs.html', variables)


def other_people_adult_permission(request):
    """
    Method returning the template for the People in your home: adult permission page (for a given application) and
    navigating to the People in your home: children question page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: adult permission template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_adults = int(request.GET["adults"])
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_adults + 1):
            form = OtherPeopleAdultPermissionForm(
                id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'add_adult': number_of_adults + 1,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-adult-permission.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_adults = request.POST["adults"]
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        for i in range(1, int(number_of_adults) + 1):
            form = OtherPeopleAdultPermissionForm(
                request.POST, id=application_id_local, adult=i, prefix=i)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Person ' + str(
                i) + ')'
            if form.is_valid():
                adult_record = AdultInHome.objects.get(
                    application_id=application_id_local, adult=i)
                adult_record.permission_declare = form.cleaned_data.get(
                    'permission_declare')
                adult_record.save()
                application.date_updated = current_date
                application.save()
                reset_declaration(application)
                valid_list.append(True)
            else:
                valid_list.append(False)
        # If all forms are valid
        if False not in valid_list:
            variables = {
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-question?id=' +
                                        application_id_local, variables)
        # If there is an invalid form
        elif False in valid_list:
            variables = {
                'form_list': form_list,
                'application_id': application_id_local,
                'number_of_adults': number_of_adults,
                'add_adult': int(number_of_adults) + 1,
                'people_in_home_status': application.people_in_home_status
            }
            return render(request, 'other-people-adult-permission.html', variables)


def other_people_children_question(request):
    """
    Method returning the template for the People in your home: children question page (for a given application) and
    navigating to the People in your home: children details page or summary page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: children question template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleChildrenQuestionForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        number_of_adults = AdultInHome.objects.filter(
            application_id=application_id_local).count()
        adults_in_home = application.adults_in_home
        variables = {
            'form': form,
            'application_id': application_id_local,
            'number_of_adults': number_of_adults,
            'adults_in_home': adults_in_home,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-children-question.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]

        # Reset status to in progress as question can change status of overall task
        status.update(application_id_local,
                      'people_in_home_status', 'IN_PROGRESS')

        form = OtherPeopleChildrenQuestionForm(
            request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            children_in_home = form.cleaned_data.get('children_in_home')
            application.children_in_home = children_in_home
            application.children_turning_16 = False
            application.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if children_in_home == 'True':
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/children-details?id=' +
                                            application_id_local + '&children=' + str(number_of_children) + '&remove=0')
            elif children_in_home == 'False':
                # Delete any existing children from database
                children = ChildInHome.objects.filter(
                    application_id=application_id_local)
                for child in children:
                    child.delete()
                reset_declaration(application)
                return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-children-question.html', variables)


def other_people_children_details(request):
    """
    Method returning the template for the People in your home: children details page (for a given application) and
    navigating to the People in your home: approaching 16 page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: children details template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        number_of_children = int(request.GET["children"])
        remove_person = int(request.GET["remove"])
        remove_button = True
        # If there are no adults in the database
        if number_of_children == 0:
            # Set the number of children to 1 to initialise one instance of the form
            number_of_children = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one child in the database
        if number_of_children == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        remove_child(application_id_local, remove_person)
        rearrange_children(number_of_children, application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        for i in range(1, number_of_children + 1):
            form = OtherPeopleChildrenDetailsForm(
                id=application_id_local, child=i, prefix=i)
            form_list.append(form)
        variables = {
            'form_list': form_list,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'add_child': number_of_children + 1,
            'remove_button': remove_button,
            'remove_child': number_of_children - 1,
            'people_in_home_status': application.people_in_home_status
        }
        if application.people_in_home_status != 'COMPLETED':
            status.update(application_id_local,
                          'people_in_home_status', 'IN_PROGRESS')
        return render(request, 'other-people-children-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        number_of_children = request.POST["children"]
        remove_button = True
        # If there are no adults in the database
        if number_of_children == 0:
            # Set the number of children to 1 to initialise one instance of the form
            number_of_children = 1
            # Disable the remove person button
            remove_button = False
        # If there is only one child in the database
        if number_of_children == 1:
            # Disable the remove person button
            remove_button = False
        application = Application.objects.get(pk=application_id_local)
        # Generate a list of forms to iterate through in the HTML
        form_list = []
        # List to allow for the validation of each form
        valid_list = []
        # List to allow for the age verification of each form
        age_list = []
        for i in range(1, int(number_of_children) + 1):
            form = OtherPeopleChildrenDetailsForm(
                request.POST, id=application_id_local, child=i, prefix=i)
            form_list.append(form)
            form.error_summary_title = 'There is a problem with this form (Child ' + str(
                i) + ')'
            if form.is_valid():
                child_record = other_people_children_details_logic(
                    application_id_local, form, i)
                child_record.save()
                reset_declaration(application)
                valid_list.append(True)
                # Calculate child's age
                birth_day = form.cleaned_data.get('date_of_birth')[0]
                birth_month = form.cleaned_data.get('date_of_birth')[1]
                birth_year = form.cleaned_data.get('date_of_birth')[2]
                applicant_dob = date(birth_year, birth_month, birth_day)
                today = date.today()
                age = today.year - applicant_dob.year - (
                        (today.month, today.day) < (applicant_dob.month, applicant_dob.day))
                if 15 <= age < 16:
                    age_list.append(True)
                elif age < 15:
                    age_list.append(False)
            else:
                valid_list.append(False)
        if 'submit' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                }
                # If a child is approaching 16, navigate to approaching 16 page
                if True in age_list:
                    application.children_turning_16 = True
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                    return HttpResponseRedirect(settings.URL_PREFIX + '/other-people/approaching-16?id=' +
                                                application_id_local, variables)
                # If no child is approaching 16, navigate to summary page
                elif True not in age_list:
                    application.children_turning_16 = False
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                    return HttpResponseRedirect(
                        settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local,
                        variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-children-details.html', variables)
        if 'add_child' in request.POST:
            # If all forms are valid
            if False not in valid_list:
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status,
                }
                # If a child is approaching 16, navigate to approaching 16 page
                if True in age_list:
                    application.children_turning_16 = True
                    application.date_updated = current_date
                    application.save()
                    reset_declaration(application)
                variables = {
                    'application_id': application_id_local,
                    'people_in_home_status': application.people_in_home_status
                }
                add_child = int(number_of_children) + 1
                add_child_string = str(add_child)
                return HttpResponseRedirect(
                    settings.URL_PREFIX + '/other-people/children-details?id=' +
                    application_id_local + '&children=' + add_child_string + '&remove=0',
                    variables)
            # If there is an invalid form
            elif False in valid_list:
                variables = {
                    'form_list': form_list,
                    'application_id': application_id_local,
                    'number_of_children': number_of_children,
                    'add_child': int(number_of_children) + 1,
                    'remove_child': int(number_of_children) - 1,
                    'remove_button': remove_button,
                    'people_in_home_status': application.people_in_home_status
                }
                return render(request, 'other-people-children-details.html', variables)


def other_people_approaching_16(request):
    """
    Method returning the template for the People in your home: approaching 16 page (for a given application)
    and navigating to the People in your home: number of children page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: approaching 16 template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = OtherPeopleApproaching16Form()
        application = Application.objects.get(pk=application_id_local)
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        variables = {
            'form': form,
            'application_id': application_id_local,
            'number_of_children': number_of_children,
            'people_in_home_status': application.people_in_home_status
        }
        return render(request, 'other-people-approaching-16.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleApproaching16Form(request.POST)
        application = Application.objects.get(pk=application_id_local)
        number_of_children = ChildInHome.objects.filter(
            application_id=application_id_local).count()
        if form.is_valid():
            if application.people_in_home_status != 'COMPLETED':
                status.update(application_id_local,
                              'people_in_home_status', 'IN_PROGRESS')
            variables = {
                'form': form,
                'number_of_children': number_of_children,
                'application_id': application_id_local,
                'people_in_home_status': application.people_in_home_status
            }
            return HttpResponseRedirect(
                settings.URL_PREFIX + '/other-people/summary?id=' + application_id_local, variables)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-approaching-16.html', variables)


def other_people_summary(request):
    """
    Method returning the template for the People in your home: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered People in your home: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        adults_list = AdultInHome.objects.filter(
            application_id=application_id_local).order_by('adult')
        adult_name_list = []
        adult_birth_day_list = []
        adult_birth_month_list = []
        adult_birth_year_list = []
        adult_relationship_list = []
        adult_dbs_list = []
        adult_permission_list = []
        children_list = ChildInHome.objects.filter(
            application_id=application_id_local).order_by('child')
        child_name_list = []
        child_birth_day_list = []
        child_birth_month_list = []
        child_birth_year_list = []
        child_relationship_list = []
        form = OtherPeopleSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        for adult in adults_list:
            if adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            elif adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            adult_name_list.append(name)
            adult_birth_day_list.append(adult.birth_day)
            adult_birth_month_list.append(adult.birth_month)
            adult_birth_year_list.append(adult.birth_year)
            adult_relationship_list.append(adult.relationship)
            adult_dbs_list.append(adult.dbs_certificate_number)
            adult_permission_list.append(adult.permission_declare)
        adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                          adult_relationship_list, adult_dbs_list, adult_permission_list)
        for child in children_list:
            if child.middle_names != '':
                name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
            elif child.middle_names == '':
                name = child.first_name + ' ' + child.last_name
            child_name_list.append(name)
            child_birth_day_list.append(child.birth_day)
            child_birth_month_list.append(child.birth_month)
            child_birth_year_list.append(child.birth_year)
            child_relationship_list.append(child.relationship)
        child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                          child_relationship_list)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'adults_in_home': application.adults_in_home,
            'children_in_home': application.children_in_home,
            'number_of_adults': adults_list.count(),
            'number_of_children': children_list.count(),
            'adult_lists': adult_lists,
            'child_lists': child_lists,
            'turning_16': application.children_turning_16,
            'people_in_home_status': application.people_in_home_status
        }
        status.update(application_id_local,
                      'people_in_home_status', 'COMPLETED')
        return render(request, 'other-people-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = OtherPeopleSummaryForm()
        if form.is_valid():
            status.update(application_id_local,
                          'people_in_home_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'other-people-summary.html', variables)


def declaration_summary(request):
    """
    Method returning the template for the Declaration: summary page (for a given application) and navigating to
    the Declaration: declaration page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DeclarationSummaryForm()
        # Retrieve all information related to the application from the database
        application = Application.objects.get(
            application_id=application_id_local)
        login_detail_id = application.login_id.login_id
        login_record = UserDetails.objects.get(login_id=login_detail_id)
        childcare_record = ChildcareType.objects.get(
            application_id=application_id_local)
        applicant_record = ApplicantPersonalDetails.objects.get(
            application_id=application_id_local)
        personal_detail_id = applicant_record.personal_detail_id
        applicant_name_record = ApplicantName.objects.get(
            personal_detail_id=personal_detail_id)
        applicant_home_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                         current_address=True)
        applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                              childcare_address=True)
        first_aid_record = FirstAidTraining.objects.get(
            application_id=application_id_local)
        dbs_record = CriminalRecordCheck.objects.get(
            application_id=application_id_local)
        hdb_record = HealthDeclarationBooklet.objects.get(
            application_id=application_id_local)
        # eyfs_record = EYFS.objects.get(application_id=application_id_local)
        first_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=1)
        second_reference_record = Reference.objects.get(
            application_id=application_id_local, reference=2)
        # Retrieve lists of adults and children, ordered by adult/child number for iteration by the HTML
        adults_list = AdultInHome.objects.filter(
            application_id=application_id_local).order_by('adult')
        children_list = ChildInHome.objects.filter(
            application_id=application_id_local).order_by('child')
        # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
        # The HTML will then parse through each list simultaneously, to display the correct data for each adult
        adult_name_list = []
        adult_birth_day_list = []
        adult_birth_month_list = []
        adult_birth_year_list = []
        adult_relationship_list = []
        adult_dbs_list = []
        adult_permission_list = []
        application = Application.objects.get(pk=application_id_local)
        for adult in adults_list:
            # For each adult, append the correct attribute (e.g. name, relationship) to the relevant list
            # Concatenate the adult's name for display, displaying any middle names if present
            if adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            elif adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name
            adult_name_list.append(name)
            adult_birth_day_list.append(adult.birth_day)
            adult_birth_month_list.append(adult.birth_month)
            adult_birth_year_list.append(adult.birth_year)
            adult_relationship_list.append(adult.relationship)
            adult_dbs_list.append(adult.dbs_certificate_number)
            adult_permission_list.append(adult.permission_declare)
        # Zip the appended lists together for the HTML to simultaneously parse
        adult_lists = zip(adult_name_list, adult_birth_day_list, adult_birth_month_list, adult_birth_year_list,
                          adult_relationship_list, adult_dbs_list, adult_permission_list)
        # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
        # The HTML will then parse through each list simultaneously, to display the correct data for each adult
        child_name_list = []
        child_birth_day_list = []
        child_birth_month_list = []
        child_birth_year_list = []
        child_relationship_list = []
        for child in children_list:
            # For each child, append the correct attribute (e.g. name, relationship) to the relevant list
            # Concatenate the child's name for display, displaying any middle names if present
            if child.middle_names != '':
                name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
            elif child.middle_names == '':
                name = child.first_name + ' ' + child.last_name
            child_name_list.append(name)
            child_birth_day_list.append(child.birth_day)
            child_birth_month_list.append(child.birth_month)
            child_birth_year_list.append(child.birth_year)
            child_relationship_list.append(child.relationship)
        # Zip the appended lists together for the HTML to simultaneously parse
        child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                          child_relationship_list)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'login_details_email': login_record.email,
            'login_details_mobile_number': login_record.mobile_number,
            'login_details_alternative_phone_number': login_record.add_phone_number,
            'childcare_type_zero_to_five': childcare_record.zero_to_five,
            'childcare_type_five_to_eight': childcare_record.five_to_eight,
            'childcare_type_eight_plus': childcare_record.eight_plus,
            'personal_details_first_name': applicant_name_record.first_name,
            'personal_details_middle_names': applicant_name_record.middle_names,
            'personal_details_last_name': applicant_name_record.last_name,
            'personal_details_birth_day': applicant_record.birth_day,
            'personal_details_birth_month': applicant_record.birth_month,
            'personal_details_birth_year': applicant_record.birth_year,
            'home_address_street_line1': applicant_home_address_record.street_line1,
            'home_address_street_line2': applicant_home_address_record.street_line2,
            'home_address_town': applicant_home_address_record.town,
            'home_address_county': applicant_home_address_record.county,
            'home_address_postcode': applicant_home_address_record.postcode,
            'childcare_street_line1': applicant_childcare_address_record.street_line1,
            'childcare_street_line2': applicant_childcare_address_record.street_line2,
            'childcare_town': applicant_childcare_address_record.town,
            'childcare_county': applicant_childcare_address_record.county,
            'childcare_postcode': applicant_childcare_address_record.postcode,
            'location_of_childcare': applicant_home_address_record.childcare_address,
            'first_aid_training_organisation': first_aid_record.training_organisation,
            'first_aid_training_course': first_aid_record.course_title,
            'first_aid_certificate_day': first_aid_record.course_day,
            'first_aid_certificate_month': first_aid_record.course_month,
            'first_aid_certificate_year': first_aid_record.course_year,
            'dbs_certificate_number': dbs_record.dbs_certificate_number,
            'cautions_convictions': dbs_record.cautions_convictions,
            'declaration': dbs_record.send_certificate_declare,
            'send_hdb_declare': hdb_record.send_hdb_declare,
            # 'eyfs_understand': eyfs_record.eyfs_understand,
            # 'eyfs_training_declare': eyfs_record.eyfs_training_declare,
            # 'share_info_declare': eyfs_record.share_info_declare,
            'first_reference_first_name': first_reference_record.first_name,
            'first_reference_last_name': first_reference_record.last_name,
            'first_reference_relationship': first_reference_record.relationship,
            'first_reference_years_known': first_reference_record.years_known,
            'first_reference_months_known': first_reference_record.months_known,
            'first_reference_street_line1': first_reference_record.street_line1,
            'first_reference_street_line2': first_reference_record.street_line2,
            'first_reference_town': first_reference_record.town,
            'first_reference_county': first_reference_record.county,
            'first_reference_postcode': first_reference_record.postcode,
            'first_reference_country': first_reference_record.country,
            'first_reference_phone_number': first_reference_record.phone_number,
            'first_reference_email': first_reference_record.email,
            'second_reference_first_name': second_reference_record.first_name,
            'second_reference_last_name': second_reference_record.last_name,
            'second_reference_relationship': second_reference_record.relationship,
            'second_reference_years_known': second_reference_record.years_known,
            'second_reference_months_known': second_reference_record.months_known,
            'second_reference_street_line1': second_reference_record.street_line1,
            'second_reference_street_line2': second_reference_record.street_line2,
            'second_reference_town': second_reference_record.town,
            'second_reference_county': second_reference_record.county,
            'second_reference_postcode': second_reference_record.postcode,
            'second_reference_country': second_reference_record.country,
            'second_reference_phone_number': second_reference_record.phone_number,
            'second_reference_email': second_reference_record.email,
            'adults_in_home': application.adults_in_home,
            'children_in_home': application.children_in_home,
            'number_of_adults': adults_list.count(),
            'number_of_children': children_list.count(),
            'adult_lists': adult_lists,
            'child_lists': child_lists,
            'turning_16': application.children_turning_16,
        }
        if application.declarations_status != 'COMPLETED':
            status.update(application_id_local,
                          'declarations_status', 'NOT_STARTED')
        return render(request, 'declaration-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DeclarationSummaryForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.declarations_status != 'COMPLETED':
                status.update(application_id_local,
                              'declarations_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/declaration/declaration?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'declaration-summary.html', variables)


def declaration_intro(request):
    """
    Method returning the template for the Declaration intro page (for a given application) and navigating to
    the declaration page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration intro template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DeclarationIntroForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'declarations_status': application.declarations_status
        }
        return render(request, 'declaration-intro.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(application_id=application_id_local)
        form = DeclarationIntroForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/your-declaration?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'declarations_status': application.declarations_status
            }
            return render(request, 'declaration-intro.html', variables)


def declaration_declaration(request):
    """
    Method returning the template for the Declaration page (for a given application) and navigating to
    the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration template
    """
    current_date = datetime.datetime.today()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = DeclarationDeclarationForm(id=application_id_local)
        form2 = DeclarationDeclarationForm2(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'form2': form2,
            'application_id': application_id_local,
            'declarations_status': application.declarations_status
        }
        return render(request, 'declaration-declaration.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        application = Application.objects.get(
            application_id=application_id_local)
        form = DeclarationDeclarationForm(
            request.POST, id=application_id_local)
        form.error_summary_title = 'There is a problem with this form (I am happy for Ofsted to)'
        form2 = DeclarationDeclarationForm2(
            request.POST, id=application_id_local)
        form2.error_summary_title = 'There is a problem with this form (I declare that)'
        # Validate both forms (sets of checkboxes)
        if form.is_valid():
            background_check_declare = form.cleaned_data.get(
                'background_check_declare')
            inspect_home_declare = form.cleaned_data.get(
                'inspect_home_declare')
            interview_declare = form.cleaned_data.get('interview_declare')
            share_info_declare = form.cleaned_data.get('share_info_declare')
            application.background_check_declare = background_check_declare
            application.inspect_home_declare = inspect_home_declare
            application.interview_declare = interview_declare
            application.share_info_declare = share_info_declare
            application.save()
            application.date_updated = current_date
            application.save()
            if form2.is_valid():
                information_correct_declare = form2.cleaned_data.get(
                    'information_correct_declare')
                application.information_correct_declare = information_correct_declare
                application.save()
                application.date_updated = current_date
                application.save()
                status.update(application_id_local,
                              'declarations_status', 'COMPLETED')
                return HttpResponseRedirect(settings.URL_PREFIX + '/payment?id=' + application_id_local)
            else:
                variables = {
                    'form': form,
                    'form2': form2,
                    'application_id': application_id_local
                }
                return render(request, 'declaration-declaration.html', variables)
        else:
            variables = {
                'form': form,
                'form2': form2,
                'application_id': application_id_local
            }
            return render(request, 'declaration-declaration.html', variables)


@never_cache
def card_payment_details(request):
    """
    Method returning the template for the Card payment details page (for a given application) and navigating to
    the payment confirmation page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Card payment details template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        paid = Application.objects.get(pk=application_id_local).order_code
        if paid is None:
            form = PaymentDetailsForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'payment-details.html', variables)
        elif paid is not None:
            variables = {
                'application_id': application_id_local,
                'order_code': paid
            }
            return render(request, 'paid.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = PaymentDetailsForm(request.POST)
        if form.is_valid():
            card_number = re.sub('[ -]+', '', request.POST["card_number"])
            cardholders_name = request.POST["cardholders_name"]
            card_security_code = str(request.POST["card_security_code"])
            expiry_month = request.POST["expiry_date_0"]
            expiry_year = request.POST["expiry_date_1"]
            # Make payment
            payment_response = payment.make_payment(3500, cardholders_name, card_number, card_security_code,
                                                    expiry_month, expiry_year, 'GBP', application_id_local,
                                                    application_id_local)
            parsed_payment_response = json.loads(payment_response.text)
            # If the payment is successful
            if payment_response.status_code == 201:

                application = Application.objects.get(pk=application_id_local)
                # when functionality to resubmit an application is added this trigger must be added
                # trigger_audit_log(application_id_local, 'RESUBMITTED')
                trigger_audit_log(application_id_local, 'SUBMITTED')
                application.date_submitted = datetime.datetime.today()
                login_id = application.login_id.login_id
                login_record = UserDetails.objects.get(pk=login_id)
                personal_detail_id = ApplicantPersonalDetails.objects.get(
                    application_id=application_id_local).personal_detail_id
                applicant_name_record = ApplicantName.objects.get(
                    personal_detail_id=personal_detail_id)
                payment.payment_email(login_record.email,
                                      applicant_name_record.first_name)
                print('Email sent')
                order_code = parsed_payment_response["orderCode"]
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'order_code': order_code
                }
                application.order_code = UUID(order_code)
                application.save()
                return HttpResponseRedirect(settings.URL_PREFIX + '/confirmation/?id=' + application_id_local +
                                            '&orderCode=' + order_code, variables)
            else:
                variables = {
                    'form': form,
                    'application_id': application_id_local,
                    'error_flag': 1,
                    'error_message': parsed_payment_response["message"],
                }
            return HttpResponseRedirect(settings.URL_PREFIX + '/payment-details/?id=' + application_id_local, variables)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'payment-details.html', variables)


def paypal_payment_completion(request):
    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = request.GET['orderCode']
        # If the payment has been successfully processed
        if payment.check_payment(order_code) == 200:
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
            }

            application = Application.objects.get(pk=application_id_local)
            application.date_submitted = datetime.datetime.today()
            application.order_code = UUID(order_code)
            application.save()

            return HttpResponseRedirect(settings.URL_PREFIX + '/confirmation/?id=' + application_id_local +
                                        '&orderCode=' + order_code, variables)
        else:
            print('HELP')
            return render(request, '500.html')


def payment_confirmation(request):
    """
    Method returning the template for the Payment confirmation page (for a given application)
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Payment confirmation template
    """
    if request.method == 'GET':
        application_id_local = request.GET['id']
        order_code = request.GET['orderCode']
        # If the payment has been successfully processed
        if payment.check_payment(order_code) == 200:
            variables = {
                'application_id': application_id_local,
                'order_code': request.GET["orderCode"],
            }
            local_app = Application.objects.get(
                application_id=application_id_local)
            local_app.application_status = 'SUBMITTED'
            local_app.save()
            return render(request, 'payment-confirmation.html', variables)
        else:
            form = PaymentForm()
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return HttpResponseRedirect(settings.URL_PREFIX + '/payment/?id=' + application_id_local, variables)


def awaiting_review(request):
    """
    Method for returning a confirmation view that an application is awaiting ARC review
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered awaiting review saved template
    """
    application_id_local = request.GET["id"]
    variables = {
        'application_id': application_id_local
    }
    return render(request, 'awaiting-review.html', variables)


def application_accepted(request):
    """
    Method for returning a confirmation view that an application has been fully submitted
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered application submitted saved template
    """
    application_id_local = request.GET["id"]
    variables = {
        'application_id': application_id_local
    }
    return render(request, 'application-accepted.html', variables)


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
    mydata['date'] = str(datetime.datetime.today().strftime("%d/%m/%Y"))
    if AuditLog.objects.filter(application_id=application_id).count() == 1:
        log = AuditLog.objects.get(application_id=application_id)
        log.audit_message = log.audit_message[:-1] + ',' + json.dumps(mydata) + ']'
        log.save()
    else:
        log = AuditLog.objects.create(
            application_id=application_id, audit_message='[' + json.dumps(mydata) + ']')
