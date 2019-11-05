from django.urls import reverse
from django.utils import timezone
import calendar
import collections
import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.decorators.cache import never_cache
from timeline_logger.models import TimelineLog

from application.views.magic_link import magic_link_resubmission_confirmation_email
from application import views
from application.business_logic import find_dbs_status, DBSStatus
from .. import status
from ..forms import (DeclarationIntroForm,
                     DeclarationForm,
                     DeclarationSummaryForm,
                     PublishingYourDetailsForm)
from ..models import (AdultInHome,
                      AdultInHomeAddress,
                      ApplicantHomeAddress,
                      ApplicantName,
                      ApplicantPersonalDetails,
                      Application,
                      Child,
                      ChildAddress,
                      ChildInHome,
                      ChildcareType,
                      CriminalRecordCheck,
                      ChildcareTraining,
                      FirstAidTraining,
                      Reference,
                      UserDetails)


def declaration_summary(request, print_mode=False):
    """
    Method returning the template for the Declaration: summary page (for a given application) and navigating to
    the Declaration: declaration page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration: summary template
    """

    def get_arc_flagged(application):
        """
        Iterate through db_task_names and get the related _arc_flagged database value
        :param application: application model instance for the user
        :return: Tuple containing all _arc_flagged values in order they appear within db_task_names
        """

        db_arc_flagged = ['login_details_arc_flagged',
                          'childcare_type_arc_flagged',
                          'personal_details_arc_flagged',
                          'first_aid_training_arc_flagged',
                          'health_arc_flagged',
                          'childcare_training_arc_flagged',
                          'criminal_record_check_arc_flagged',
                          'people_in_home_arc_flagged',
                          'references_arc_flagged']

        return (getattr(application, task) for task in db_arc_flagged)

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
        if ApplicantHomeAddress.objects.filter(personal_detail_id=personal_detail_id, childcare_address=True).exists():
            applicant_childcare_address_record = ApplicantHomeAddress.objects.get(personal_detail_id=personal_detail_id,
                                                                                  childcare_address=True)
            childcare_street_line1 = applicant_childcare_address_record.street_line1
            childcare_street_line2 = applicant_childcare_address_record.street_line2
            childcare_town = applicant_childcare_address_record.town
            childcare_county = applicant_childcare_address_record.county
            childcare_postcode = applicant_childcare_address_record.postcode
        else:
            applicant_childcare_address_record = 'Same as home address'
            childcare_street_line1 = ''
            childcare_street_line2 = ''
            childcare_town = ''
            childcare_county = ''
            childcare_postcode = ''

        first_aid_record = FirstAidTraining.objects.get(application_id=application_id_local)

        # Format first aid training dates
        if first_aid_record.course_day < 10:
            first_aid_course_day = '0' + str(first_aid_record.course_day)
        else:
            first_aid_course_day = str(first_aid_record.course_day)

        if first_aid_record.course_month < 10:
            first_aid_course_month = '0' + str(first_aid_record.course_month)
        else:
            first_aid_course_month = str(first_aid_record.course_month)

        dbs_record = CriminalRecordCheck.objects.get(application_id=application_id_local)

        childcare_training_table = \
            views.ChildcareTrainingSummaryView.get_context_data(application_id_local)['table_list'][0]
        criminal_record_check_context = views.DBSSummaryView.get_context_data_static(application_id_local)

        if childcare_record.zero_to_five:
            first_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=1)
            second_reference_record = Reference.objects.get(
                application_id=application_id_local, reference=2)

            references_vars = {
                'first_reference_title': first_reference_record.title,
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
                'second_reference_title': second_reference_record.title,
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
                'second_reference_email': second_reference_record.email
            }

        else:
            references_vars = {}

        # Retrieve lists of adults and children, ordered by adult/child number for iteration by the HTML
        adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
        children_list = ChildInHome.objects.filter(application_id=application_id_local).order_by('child')
        children_not_in_the_home_list = Child.objects.filter(application_id=application_id_local,
                                                             lives_with_childminder=False).order_by('child')
        # Generate lists of data for adults in your home, to be iteratively displayed on the summary page
        # The HTML will then parse through each list simultaneously, to display the correct data for each adult
        adult_title_list = []
        adult_name_list = []
        adult_birth_day_list = []
        adult_birth_month_list = []
        adult_birth_year_list = []
        adult_relationship_list = []
        adult_dbs_list = []
        adult_health_check_status_list = []
        adult_email_list = []
        adult_mobile_number_list = []
        adult_same_address_list = []
        adult_lived_abroad_list = []
        adult_military_base_list = []
        adult_enhanced_check_list = []
        adult_on_update_list = []

        application = Application.objects.get(pk=application_id_local)
        for adult in adults_list:

            # For each adult, append the correct attribute (e.g. name, relationship) to the relevant list
            # Concatenate the adult's name for display, displaying any middle names if present

            if not adult.PITH_same_address:
                adult_address_string = ' '.join([AdultInHomeAddress.objects.get(application_id=app_id,
                                                                                adult_id=adult.pk).street_line1,
                                                 (AdultInHomeAddress.objects.get(application_id=app_id,
                                                                                 adult_id=adult.pk).street_line2 or ''),
                                                 AdultInHomeAddress.objects.get(application_id=app_id,
                                                                                adult_id=adult.pk).town,
                                                 (AdultInHomeAddress.objects.get(application_id=app_id,
                                                                                 adult_id=adult.pk).county or ''),
                                                 AdultInHomeAddress.objects.get(application_id=app_id,
                                                                                adult_id=adult.pk).postcode])

            else:
                adult_address_string = 'Same as home address'

            if adult.middle_names != '':
                name = adult.first_name + ' ' + adult.middle_names + ' ' + adult.last_name
            elif adult.middle_names == '':
                name = adult.first_name + ' ' + adult.last_name

            if adult.birth_day < 10:
                adult_birth_day = '0' + str(adult.birth_day)
            else:
                adult_birth_day = str(adult.birth_day)

            if adult.birth_month < 10:
                adult_birth_month = '0' + str(adult.birth_month)
            else:
                adult_birth_month = str(adult.birth_month)

            adult_title_list.append(adult.title)
            adult_name_list.append(name)
            adult_birth_day_list.append(adult_birth_day)
            adult_birth_month_list.append(adult_birth_month)
            adult_birth_year_list.append(adult.birth_year)
            adult_relationship_list.append(adult.relationship)
            adult_dbs_list.append(adult.dbs_certificate_number)
            adult_health_check_status_list.append(adult.health_check_status)
            adult_email_list.append(adult.email)
            adult_mobile_number_list.append(adult.PITH_mobile_number)
            adult_same_address_list.append(adult_address_string)
            adult_lived_abroad_list.append(adult.lived_abroad)
            adult_military_base_list.append(adult.military_base)
            adult_enhanced_check_list.append(adult.enhanced_check)
            adult_on_update_list.append(adult.on_update)

        # Zip the appended lists together for the HTML to simultaneously parse
        adult_lists = zip(adult_title_list, adult_name_list, adult_birth_day_list, adult_birth_month_list,
                          adult_birth_year_list, adult_relationship_list, adult_dbs_list, adult_health_check_status_list
                          , adult_email_list, adult_mobile_number_list, adult_same_address_list,
                          adult_lived_abroad_list, adult_enhanced_check_list, adult_on_update_list,
                          adult_military_base_list)
        # Generate lists of data for children in your home, to be iteratively displayed on the summary page
        # The HTML will then parse through each list simultaneously, to display the correct data for each child
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
            if child.birth_day < 10:
                child_birth_day = '0' + str(child.birth_day)
            else:
                child_birth_day = str(child.birth_day)
            if child.birth_month < 10:
                child_birth_month = '0' + str(child.birth_month)
            else:
                child_birth_month = str(child.birth_month)
            child_birth_day_list.append(child_birth_day)
            child_birth_month_list.append(child_birth_month)
            child_birth_year_list.append(child.birth_year)
            child_relationship_list.append(child.relationship)
        # Zip the appended lists together for the HTML to simultaneously parse
        child_lists = zip(child_name_list, child_birth_day_list, child_birth_month_list, child_birth_year_list,
                          child_relationship_list)
        # Generate lists of data for children not in your home, to be iteratively displayed on the summary page
        # The HTML will then parse through each list simultaneously, to display the correct data for each child
        child_not_in_home_id_list = []
        child_not_in_home_name_list = []
        child_not_in_home_birth_day_list = []
        child_not_in_home_birth_month_list = []
        child_not_in_home_birth_year_list = []
        child_not_in_home_street_line1_list = []
        child_not_in_home_street_line2_list = []
        child_not_in_home_town_list = []
        child_not_in_home_county_list = []
        child_not_in_home_postcode_list = []
        child_not_in_home_country_list = []
        for child in children_not_in_the_home_list:
            # For each child, append the correct attribute (e.g. name, relationship) to the relevant list
            child_not_in_home_id = child.child
            child_not_in_home_id_list.append(child_not_in_home_id)
            # Concatenate the child's name for display, displaying any middle names if present
            if child.middle_names != '':
                name = child.first_name + ' ' + child.middle_names + ' ' + child.last_name
            elif child.middle_names == '':
                name = child.first_name + ' ' + child.last_name
            child_not_in_home_name_list.append(name)
            if child.birth_day < 10:
                child_birth_day = '0' + str(child.birth_day)
            else:
                child_birth_day = str(child.birth_day)
            if child.birth_month < 10:
                child_birth_month = '0' + str(child.birth_month)
            else:
                child_birth_month = str(child.birth_month)
            child_not_in_home_birth_day_list.append(child_birth_day)
            child_not_in_home_birth_month_list.append(child_birth_month)
            child_not_in_home_birth_year_list.append(child.birth_year)
            child_not_in_home_address = ChildAddress.objects.get(application_id=application_id_local, child=child.child)
            child_not_in_home_street_line1_list.append(child_not_in_home_address.street_line1)
            child_not_in_home_street_line2_list.append(child_not_in_home_address.street_line2)
            child_not_in_home_town_list.append(child_not_in_home_address.town)
            child_not_in_home_county_list.append(child_not_in_home_address.county)
            child_not_in_home_postcode_list.append(child_not_in_home_address.postcode)
            child_not_in_home_country_list.append(child_not_in_home_address.country)
        # Zip the appended lists together for the HTML to simultaneously parse
        child_not_in_home_lists = zip(child_not_in_home_id_list, child_not_in_home_name_list,
                                      child_not_in_home_birth_day_list, child_not_in_home_birth_month_list,
                                      child_not_in_home_birth_year_list, child_not_in_home_street_line1_list,
                                      child_not_in_home_street_line2_list, child_not_in_home_town_list,
                                      child_not_in_home_county_list, child_not_in_home_postcode_list,
                                      child_not_in_home_country_list)

        # Retrieve children living with childminder information
        children_table = []
        children_living_with_childminder = []
        children = Child.objects.filter(application_id=application_id_local).order_by('child')
        for child in children:

            dob = datetime.date(child.birth_year, child.birth_month, child.birth_day)

            # If the child does not live with the childminder, append their full address for display on the summary page
            full_address = None

            if not child.lives_with_childminder:
                full_address = ChildAddress.objects.get(application_id=application_id_local, child=child.child)

            child_details = collections.OrderedDict([
                ('child_number', child.child),
                ('full_name', child.get_full_name()),
                ('dob', dob),
                ('lives_with_childminder', child.lives_with_childminder),
                ('full_address', full_address),
            ])
            children_table.append(child_details)

            if child.lives_with_childminder:
                children_living_with_childminder.append(child.get_full_name())

        # For returned applications, display change links only if task has been returned
        if application.application_status == 'FURTHER_INFORMATION':
            arc_flagged_statuses = get_arc_flagged(application)

            sign_in_details_change, \
            type_of_childcare_change, \
            personal_details_change, \
            first_aid_training_change, \
            health_change, \
            early_years_training_change, \
            criminal_record_check_change, \
            people_in_your_home_change, \
            references_change = arc_flagged_statuses

        else:
            sign_in_details_change = True
            type_of_childcare_change = True
            personal_details_change = True
            first_aid_training_change = True
            health_change = True
            early_years_training_change = True
            criminal_record_check_change = True
            people_in_your_home_change = True
            references_change = True

        variables = {
            'form': form,
            'application_id': application_id_local,
            'login_details_email': login_record.email,
            'login_details_mobile_number': login_record.mobile_number,
            'login_details_alternative_phone_number': login_record.add_phone_number,
            'sign_in_details_change': sign_in_details_change,
            'childcare_type_zero_to_five': childcare_record.zero_to_five,
            'childcare_type_five_to_eight': childcare_record.five_to_eight,
            'childcare_type_eight_plus': childcare_record.eight_plus,
            'childcare_overnight': childcare_record.overnight_care,
            'type_of_childcare_change': type_of_childcare_change,
            'personal_details_title': applicant_name_record.title,
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
            'childcare_street_line1': childcare_street_line1,
            'childcare_street_line2': childcare_street_line2,
            'childcare_town': childcare_town,
            'childcare_county': childcare_county,
            'childcare_postcode': childcare_postcode,
            'location_of_childcare': applicant_home_address_record.childcare_address,
            'working_in_other_childminder_home': application.working_in_other_childminder_home,
            'own_children': application.own_children,
            'reasons_known_to_social_services': application.reasons_known_to_social_services,
            'personal_details_change': personal_details_change,
            'first_aid_training_organisation': first_aid_record.training_organisation,
            'first_aid_training_course': first_aid_record.course_title,
            'first_aid_certificate_day': first_aid_course_day,
            'first_aid_certificate_month': first_aid_course_month,
            'first_aid_certificate_year': first_aid_record.course_year,
            'first_aid_training_change': first_aid_training_change,
            'criminal_record_check_context': criminal_record_check_context,
            'criminal_record_check_change': criminal_record_check_change,
            'send_hdb_declare': True,
            'health_change': health_change,
            'childcare_training_table': childcare_training_table,
            'early_years_training_change': early_years_training_change,
            'references_change': references_change,
            'adults_in_home': application.adults_in_home,
            'children_in_home': application.children_in_home,
            'children_not_in_home': application.known_to_social_services_pith,
            'number_of_adults': adults_list.count(),
            'number_of_children': children_list.count(),
            'adult_lists': adult_lists,
            'child_lists': child_lists,
            'child_not_in_home_lists': child_not_in_home_lists,
            'turning_16': application.children_turning_16,
            'people_in_your_home_change': people_in_your_home_change,
            'print': print_mode,
            'children': children_table,
            'children_living_with_childminder': ", ".join(children_living_with_childminder),
            'known_to_social_services_pith': application.known_to_social_services_pith,
            'reasons_known_to_social_services_pith': application.reasons_known_to_social_services_pith
        }

        variables = {**variables, **references_vars}

        if application.declarations_status != 'COMPLETED':
            status.update(application_id_local, 'declarations_status', 'NOT_STARTED')
        if print_mode:
            return variables
        return render(request, 'master-summary.html', variables)

    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = DeclarationSummaryForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        childcare_type = ChildcareType.objects.get(application_id=application_id_local)
        if form.is_valid():
            if application.declarations_status != 'COMPLETED':
                status.update(application_id_local, 'declarations_status', 'IN_PROGRESS')
            if not childcare_type.zero_to_five:
                return HttpResponseRedirect(reverse('Declaration-Intro-View') + '?id=' + application_id_local)
            else:
                return HttpResponseRedirect(reverse('Declaration-Declaration-View') + '?id=' + application_id_local)
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
            return HttpResponseRedirect(reverse('Declaration-Declaration-View') + '?id=' + application_id_local)
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
        declaration_form = DeclarationForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        childcare_type = ChildcareType.objects.get(application_id=application_id_local)

        # If application is already submitted redirect them to the awaiting review page
        if application.application_status == 'SUBMITTED' and application.application_reference is not None:
            criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
            variables = {
                'application_id': application_id_local,
                'order_code': application.application_reference,
                'conviction': criminal_record_check.cautions_convictions,
                'health_status': Application.objects.get(application_id=application_id_local).health_status
            }
            return render(request, 'payment-confirmation.html', variables)

        variables = {
            'declaration_form': declaration_form,
            'form': declaration_form,
            'application_id': application_id_local,
            'declarations_status': application.declarations_status,
            'is_resubmission': application.application_status == 'FURTHER_INFORMATION',
            'registers': not childcare_type.zero_to_five
        }
        return render(request, 'declaration-declaration.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        application = Application.objects.get(application_id=application_id_local)

        declaration_form = DeclarationForm(request.POST, id=application_id_local)
        declaration_form.error_summary_title = 'There was a problem with your declaration'

        if declaration_form.is_valid():
            # get new values out of form data
            declaration_confirmation = declaration_form.cleaned_data.get('declaration_confirmation')

            # save them down to application
            application.declaration_confirmation = declaration_confirmation
            application.date_updated = current_date
            application.save()

            if application.application_status == 'FURTHER_INFORMATION':
                # In cases where a resubmission is being made,
                # payment is no a valid trigger so this becomes the appropriate trigger resubmission audit
                TimelineLog.objects.create(
                    content_object=application,
                    user=None,
                    template='timeline_logger/application_action.txt',
                    extra_data={'user_type': 'applicant', 'action': 'resubmitted by', 'entity': 'application'}
                )

                updated_list = generate_list_of_updated_tasks(application_id_local)

                # If a resubmission return application status to submitted and forward to the confirmation page
                application.application_status = "SUBMITTED"
                application.save()

                criminal_record_check = CriminalRecordCheck.objects.get(application_id=application_id_local)
                variables = {
                    'application_id': application_id_local,
                    'id': application_id_local,
                    'order_code': application.application_reference,
                    'conviction': criminal_record_check.cautions_convictions,
                    'health_status': Application.objects.get(application_id=application_id_local).health_status,
                    'updated_list': updated_list
                }

                user_details = UserDetails.objects.get(application_id=application_id_local)
                applicant_name = ApplicantName.objects.get(application_id=application_id_local)
                magic_link_resubmission_confirmation_email(
                    email=user_details.email,
                    first_name=applicant_name.first_name,
                    application_reference=application.application_reference,
                    updated_tasks=updated_list
                )

                clear_arc_flagged_statuses(application_id_local)
                status.update(application_id_local, 'declarations_status', 'COMPLETED')

                return render(request, 'payment-confirmation-resubmitted.html', variables)

            clear_arc_flagged_statuses(application_id_local)

            return HttpResponseRedirect(reverse('Publishing-Your-Details-View') + '?id=' + application_id_local)

        else:
            childcare_type = ChildcareType.objects.get(application_id=application_id_local)
            variables = {
                'form': declaration_form,
                'application_id': application_id_local,
                'registers': not childcare_type.zero_to_five
            }
            return render(request, 'declaration-declaration.html', variables)


def publishing_your_details(request):
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = PublishingYourDetailsForm(id=application_id_local)
        variables = {
            'application_id': application_id_local,
            'form': form
        }
        return render(request, 'publishing-your-details.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        # extract form data
        form = PublishingYourDetailsForm(request.POST, id=application_id_local)
        if form.is_valid():
            publish_details = not form.cleaned_data.get('publish_details')
            # save down form data
            application = Application.objects.get(application_id=application_id_local)
            application.publish_details = publish_details
            application.save()
            return HttpResponseRedirect(reverse('Payment-Details-View') + '?id=' + application_id_local)


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
    if application.childcare_training_arc_flagged is True:
        updated_list.append('Early years training')
    if application.health_arc_flagged is True:
        updated_list.append('Health declaration booklet')
    if application.people_in_home_arc_flagged is True:
        updated_list.append('People in your home')
    if application.references_arc_flagged is True:
        updated_list.append('References')

    return updated_list


def clear_arc_flagged_statuses(application_id):
    """
    Method to clear flagged statues from Application fields.
    """
    application = Application.objects.get(pk=application_id)

    flagged_fields_to_check = (
        "childcare_type_arc_flagged",
        "criminal_record_check_arc_flagged",
        "childcare_training_arc_flagged",
        "first_aid_training_arc_flagged",
        "health_arc_flagged",
        "login_details_arc_flagged",
        "people_in_home_arc_flagged",
        "personal_details_arc_flagged",
        "references_arc_flagged"
    )

    for field in flagged_fields_to_check:
        setattr(application, field, False)

    return application.save()
