import calendar
import collections
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from application.forms.PITH_forms.PITH_check_your_answers_form import PITHCheckYourAnswersForm
from application.models import AdultInHome, Application, ChildInHome, Child, ChildcareType
from application.summary_page_data import other_child_name_dict, \
    other_child_link_dict, other_adult_summary_name_dict, other_adult_summary_link_dict, other_child_summary_name_dict, \
    other_child_summary_link_dict, other_child_not_in_the_home_summary_name_dict, \
    other_child_not_in_the_home_summary_link_dict, child_not_in_the_home_link_dict, child_not_in_the_home_name_dict, \
    other_adult_name_dict, other_adult_link_dict
from application.table_util import create_tables, Table, submit_link_setter
from application.views.PITH_views import PITHTemplateView, get_id
from .. import status
from ...business_logic import (show_resend_and_change_email, get_application_object)
from application.views.your_children import __create_child_table as create_child_table

logger = logging.getLogger()


class PITHCheckYourAnswersView(PITHTemplateView):
    """
    View handling the People In The Home (PITH) Check Your Answers (cya) page.
    """
    template_name = 'generic-summary-template.html'

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        application = get_application_object(application_id)

        adults_list, children_list, children_not_in_home_list = self.get_lists(application_id)

        # Header tables
        adults_header_table = self.get_adults_header_table(application_id, adults_list)
        children_header_table = self.get_children_header_table(application_id, children_list)
        children_not_in_home_header_table = self.get_children_not_in_home_header_table(application_id,
                                                                                       children_not_in_home_list)

        # Data tables
        adults_table = self.get_adults_table(application_id, application, adults_list)
        children_table = self.get_children_table(application_id, children_list)
        children_not_in_home_table = self.get_children_not_in_home_table(application_id, children_not_in_home_list)

        # Form
        form = PITHCheckYourAnswersForm()

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = "There was a problem"

        # Update application status
        # Set People in home status to Done if all adult health check statuses have been completed
        if all(adult for adult in adults_list if adult.health_check_status == 'Done'):
            status.update(application_id, 'people_in_home_status', 'COMPLETED')

        # Create Table List
        table_list = adults_header_table + adults_table + children_header_table + children_table
        if application.own_children_not_in_home is not None:
            table_list += children_not_in_home_header_table + children_not_in_home_table

        context = {
            'page_title': 'Check your answers: people in the home',
            'form': form,
            'application_id': application_id,
            'table_list': table_list,
            'turning_16': application.children_turning_16,
            'people_in_home_status': application.people_in_home_status,
            'display_buttons_list': self.get_display_buttons_list(adults_list),
            'sending_emails': self.should_resend_emails(application, adults_list),
            'num_children_not_in_home': len(children_not_in_home_list)
        }
        context = submit_link_setter(context, table_list, 'people_in_home', application_id)

        return context

    def post(self, request, *args, **kwargs):
        # TODO: Refactor me!
        application_id_local = request.POST["id"]
        application = Application.objects.get(application_id=application_id_local)

        # If reaching the summary page for the first time
        if application.people_in_home_status == 'IN_PROGRESS' or application.people_in_home_status == 'WAITING':
            adults_list = AdultInHome.objects.filter(application_id=application_id_local).order_by('adult')
            if any(adult.health_check_status == 'To do' for adult in adults_list):
                status.update(application_id_local, 'people_in_home_status', 'WAITING')

            if application.adults_in_home is True and any(
                    [adult.email_resent_timestamp is None for adult in adults_list]):
                status.update(application_id_local, 'people_in_home_status', 'WAITING')
                return HttpResponseRedirect(
                    reverse('Other-People-Email-Confirmation-View') + '?id=' + application_id_local)
            elif application.adults_in_home is False:
                status.update(application_id_local, 'people_in_home_status', 'COMPLETED')
                return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
            else:
                return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)
        else:
            return HttpResponseRedirect(reverse('Task-List-View') + '?id=' + application_id_local)

    def get_lists(self, app_id):
        """
        Business logic function
        :return: A tuple of list objects containing adults, children and children_not_in_home records.
        """
        adults_list = AdultInHome.objects.filter(application_id=app_id).order_by('adult')
        children_list = ChildInHome.objects.filter(application_id=app_id).order_by('child')
        children_not_in_home_list = Child.objects.filter(application_id=app_id).order_by('child')

        return adults_list, children_list, children_not_in_home_list

    def get_adults_header_table(self, app_id, adults_list):
        adults_in_home = bool(adults_list)

        adult_table = {
            'table_object': Table([app_id]),
            'fields': {'adults_in_home': adults_in_home},
            'title': 'Adults in the home',
            'error_summary_title': 'There was a problem'
        }

        return create_tables([adult_table], other_adult_summary_name_dict, other_adult_summary_link_dict)

    def get_children_header_table(self, app_id, children_list):
        children_in_home = bool(children_list)

        child_table = {
            'table_object': Table([app_id]),
            'fields': {'children_in_home': children_in_home},
            'title': 'Children in the home',
            'error_summary_title': 'There was a problem'
        }
        return create_tables([child_table], other_child_summary_name_dict, other_child_summary_link_dict)

    def get_children_not_in_home_header_table(self, app_id, children_not_in_home_list):
        children_not_in_home = bool(children_not_in_home_list)

        not_child_table = {
            'table_object': Table([app_id]),
            'fields': {'own_children_not_in_the_home': children_not_in_home},
            'title': 'Children not in the home',
            'error_summary_title': 'There was a problem'
        }
        return create_tables([not_child_table], other_child_not_in_the_home_summary_name_dict,
                             other_child_not_in_the_home_summary_link_dict)

    def get_adults_table(self, app_id, application, adults_list):
        # TODO: Move me to a Business Logic Function
        childcare_record = ChildcareType.objects.get(application_id=app_id)

        adults_table_list = []
        for index, adult in enumerate(adults_list):

            name = ' '.join([adult.first_name, (adult.middle_names or ''), adult.last_name])
            birth_date = ' '.join([str(adult.birth_day), calendar.month_name[adult.birth_month], str(adult.birth_year)])

            base_adult_fields = [
                ('full_name', name),
                ('date_of_birth', birth_date),
                ('relationship', adult.relationship),
                ('email', adult.email),
                ('lived_abroad', adult.lived_abroad),
                ('dbs_certificate_number', adult.dbs_certificate_number),
            ]

            if adult.capita is not None:
                base_adult_fields.append(('capita', adult.capita))

            if adult.on_update is not None:
                base_adult_fields.append(('on_update', adult.on_update))

            if childcare_record.zero_to_five is True:
                # Append military_base
                base_adult_fields.append(('military_base', adult.military_base))

            if application.people_in_home_status == 'IN_PROGRESS' and any(
                    [adult.email_resent_timestamp is None for adult in adults_list]):
                adult_fields = collections.OrderedDict(base_adult_fields)
            else:
                # Prepend health_check_status
                adult_fields = collections.OrderedDict(
                    [('health_check_status', adult.health_check_status)] + base_adult_fields)

            # If the adult health check status is marked as flagged, set the email resend limit to 0
            if adult.health_check_status == 'Started':
                adult.email_resent = 0
                adult.save()

            # Counter for table object to correctly set link in generic-error-summary template for flagged health check.
            table = Table([adult.pk])
            table.loop_counter = index + 1

            other_adult_table = collections.OrderedDict({
                'table_object': table,
                'fields': adult_fields,
                'title': name,
                'error_summary_title': ('There was a problem with {0}\'s details'.format(name))
            })

            adults_table_list.append(other_adult_table)

        back_link_addition = '&adults={0}&remove=0'.format(str(len(adults_table_list)))

        for table in adults_table_list:
            table['other_people_numbers'] = back_link_addition

        return create_tables(adults_table_list, other_adult_name_dict, other_adult_link_dict)

    def get_children_table(self, app_id, children_list):
        child_table_list = []
        for child in children_list:
            name = ' '.join([child.first_name, (child.middle_names or ''), child.last_name])

            other_child_fields = collections.OrderedDict([
                ('full_name', name),
                ('date_of_birth', ' '.join([str(child.birth_day), calendar.month_name[child.birth_month],
                                            str(child.birth_year)])),
                ('relationship', child.relationship)
            ])

            other_child_table = collections.OrderedDict({
                'table_object': Table([child.pk]),
                'fields': other_child_fields,
                'title': name,
                'error_summary_title': ('There was a problem with {0}\'s details'.format(name))
            })

            child_table_list.append(other_child_table)

        back_link_addition = '&children=' + str(len(child_table_list)) + '&remove=0'

        for table in child_table_list:
            table['other_people_numbers'] = back_link_addition
        return create_tables(child_table_list, other_child_name_dict, other_child_link_dict)

    def get_children_not_in_home_table(self, app_id, children_not_in_home_list):
        # Populating Children not in the Home:
        children_not_in_the_home_table_list = [self.__create_child_not_in_the_home_table(child) for child in
                                               children_not_in_home_list]
        return create_tables(children_not_in_the_home_table_list,
                             child_not_in_the_home_name_dict, child_not_in_the_home_link_dict)

    @staticmethod
    def __create_child_not_in_the_home_table(child):
        child_table = create_child_table(child)
        child_table['table_object'].other_people_numbers = '&children=' + str(child.child) + '&remove=0'

        return child_table

    def should_resend_emails(self, application, adults_list):
        return application.adults_in_home is True and any(
            [adult.email_resent_timestamp is None for adult in adults_list])

    def get_display_buttons_list(self, adults_list):
        return [show_resend_and_change_email(adult.health_check_status) for adult in adults_list]
