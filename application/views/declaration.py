from django.utils import timezone
import calendar

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from timeline_logger.models import TimelineLog

from .. import status
from ..forms import (DeclarationIntroForm,
                     DeclarationConfirmationOfUnderstandingForm,
                     DeclarationConfirmationOfDeclarationForm,
                     DeclarationConsentToSharingForm,
                     DeclarationSummaryForm)
from ..models import (AdultInHome,
                      ApplicantHomeAddress,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      ChildInHome,
                      ChildcareType,
                      CriminalRecordCheck,
                      EYFS,
                      FirstAidTraining,
                      Reference,
                      UserDetails)


def declaration_summary(request, print=False):
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
        login_record = UserDetails.objects.get(application_id=application)
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
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        eyfs_course_date = ' '.join(
            [str(eyfs_record.eyfs_course_date_day), calendar.month_name[eyfs_record.eyfs_course_date_month],
             str(eyfs_record.eyfs_course_date_year)])
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
            'send_hdb_declare': True,
            'eyfs_course_name': eyfs_record.eyfs_course_name,
            'eyfs_course_date': eyfs_course_date,
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
            'print': print
        }
        if application.declarations_status != 'COMPLETED':
            status.update(application_id_local,
                          'declarations_status', 'NOT_STARTED')
        if print:
            return variables
        return render(request, 'master-summary.html', variables)
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
            return render(request, 'master-summary.html', variables)


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


@never_cache
def declaration_declaration(request):
    """
    Method returning the template for the Declaration page (for a given application) and navigating to
    the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration template
    """
    current_date = timezone.now()

    if request.method == 'GET':

        application_id_local = request.GET["id"]
        confirmation_of_understanding_form = DeclarationConfirmationOfUnderstandingForm(id=application_id_local)
        confirmation_of_declaration_form = DeclarationConfirmationOfDeclarationForm(id=application_id_local)
        consent_to_sharing_form = DeclarationConsentToSharingForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)

        # If application is already submitted redirect them to the awaiting review page
        if application.application_status == 'SUBMITTED' and application.order_code is not None:
            variables = {
                'application_id': application_id_local,
                'order_code': application.order_code,
            }
            return render(request, 'payment-confirmation.html', variables)

        variables = {
            'confirmation_of_understanding_form': confirmation_of_understanding_form,
            'confirmation_of_declaration_form': confirmation_of_declaration_form,
            'consent_to_sharing_form': consent_to_sharing_form,
            'application_id': application_id_local,
            'declarations_status': application.declarations_status,
            'is_resubmission': application.application_status == 'FURTHER_INFORMATION',
        }
        return render(request, 'declaration-declaration.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        application = Application.objects.get(
            application_id=application_id_local)

        confirmation_of_understanding_form = DeclarationConfirmationOfUnderstandingForm(
            request.POST, id=application_id_local)
        confirmation_of_understanding_form.error_summary_title = 'There is a problem with ' \
                                                                 'this form (I understand that Ofsted will)'

        confirmation_of_declaration_form = DeclarationConfirmationOfDeclarationForm(
            request.POST, id=application_id_local)
        confirmation_of_declaration_form.error_summary_title = 'There is a problem with this form (I declare that)'

        consent_to_sharing_form = DeclarationConsentToSharingForm(request.POST, id=application_id_local)

        # Validate both forms (sets of checkboxes)
        if confirmation_of_understanding_form.is_valid():
            share_info_declare = confirmation_of_understanding_form.cleaned_data.get('share_info_declare')
            application.share_info_declare = share_info_declare
            application.save()
            application.date_updated = current_date
            application.save()

            if consent_to_sharing_form.is_valid():
                display_contact_details_on_web = consent_to_sharing_form.cleaned_data.get(
                    'display_contact_details_on_web')
                application.display_contact_details_on_web = display_contact_details_on_web
                application.save()
                application.date_updated = current_date
                application.save()

            if confirmation_of_declaration_form.is_valid():
                information_correct_declare = confirmation_of_declaration_form.cleaned_data.get(
                    'information_correct_declare')
                application.information_correct_declare = information_correct_declare
                change_declare = confirmation_of_declaration_form.cleaned_data.get(
                    'change_declare')
                application.change_declare = change_declare
                application.save()
                application.date_updated = current_date
                application.save()
                status.update(application_id_local,
                              'declarations_status', 'COMPLETED')

                if application.application_status == 'FURTHER_INFORMATION':
                    # In cases where a resubmission is being made,
                    # payment is no a valid trigger so this becomes the appropriate trigger resubmission audit
                    TimelineLog.objects.create(
                        content_object=application,
                        user=None,
                        template='timeline_logger/application_action.txt',
                        extra_data={'user_type': 'applicant', 'action': 're-submitted by', 'entity': 'application'}
                    )

                    updated_list = generate_list_of_updated_tasks(application_id_local)

                    # If a resubmission return application status to submitted and forward to the confirmation page
                    application.application_status = "SUBMITTED"
                    application.save()

                    variables = {
                        'application_id': application_id_local,
                        'order_code': application.order_code,
                        'updated_list': updated_list
                    }

                    return render(request, 'payment-confirmation-resubmitted.html', variables)

                return HttpResponseRedirect(settings.URL_PREFIX + '/payment?id=' + application_id_local)

            else:
                variables = {
                    'confirmation_of_understanding_form': confirmation_of_understanding_form,
                    'confirmation_of_declaration_form': confirmation_of_declaration_form,
                    'consent_to_sharing_form': consent_to_sharing_form,
                    'application_id': application_id_local
                }
                return render(request, 'declaration-declaration.html', variables)
        else:

            variables = {
                'confirmation_of_understanding_form': confirmation_of_understanding_form,
                'confirmation_of_declaration_form': confirmation_of_declaration_form,
                'consent_to_sharing_form': consent_to_sharing_form,
                'application_id': application_id_local
            }
            return render(request, 'declaration-declaration.html', variables)


def generate_list_of_updated_tasks(application_id):
    """
    Method to generate a list of flagged tasks that have been updated
    :param application_id:
    :return: a list of updated tasks
    """

    application = Application.objects.get(pk=application_id)

    # Determine which tasks have been updated
    updated_list = []

    if application.login_details_arc_flagged is True:
        updated_list.append('Your sign in details')
    if application.childcare_type_arc_flagged is True:
        updated_list.append('Type of childcare')
    if application.personal_details_arc_flagged is True:
        updated_list.append('Your personal details')
    if application.first_aid_training_arc_flagged is True:
        updated_list.append('First aid training')
    if application.criminal_record_check_arc_flagged is True:
        updated_list.append('Criminal record (DBS) check')
    if application.eyfs_training_arc_flagged is True:
        updated_list.append('Early years training')
    if application.health_arc_flagged is True:
        updated_list.append('Health declaration booklet')
    if application.people_in_home_arc_flagged is True:
        updated_list.append('People in your home')
    if application.references_arc_flagged is True:
        updated_list.append('References')

    return updated_list
