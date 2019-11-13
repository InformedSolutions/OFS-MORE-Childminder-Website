"""
Method returning the template for the Type of childcare: guidance page (for a given application) and navigating
to the Type of childcare: childcare ages page when successfully completed
"""
import collections

from django.utils import timezone

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import View

from ..table_util import Table, Row
from .. import status
from ..business_logic import reset_declaration, childcare_timing_logic
from ..forms import TimingOfChildcareGroupsForm
from ..models import Application, ChildcareTiming


def timing_of_childcare_groups(request):
    """
    Method returning the template for the Type of childcare: age groups page (for a given application) and navigating
    to the task list when successfully completed; business logic is applied to either create or update the
    associated Childcare_Type record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Type of childcare: age groups template
    """

    current_date = timezone.now()

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = TimingOfChildcareGroupsForm(id=app_id)
        application = Application.get_id(app_id=app_id)

        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'

        variables = {
            'form': form,
            'application_id': app_id,
            'childcare_timing_status': application.childcare_timing_status,
            'login_details_status': application.login_details_status,
        }

        return render(request, 'childcare-timing-groups.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        form = TimingOfChildcareGroupsForm(request.POST, id=app_id)
        application = Application.get_id(app_id=app_id)

        if form.is_valid():

            # Create or update Childcare_Type record
            childcare_timing_record = childcare_timing_logic(app_id, form)

            # Check to see if the type of childcare training has been changed
            if ChildcareTiming.objects.filter(application_id=app_id).count() > 0:
                existing_record = ChildcareTiming.objects.get(application_id=app_id)
                if existing_record.weekday_before_school != childcare_timing_record.weekday_before_school or \
                        existing_record.weekday_after_school != childcare_timing_record.weekday_after_school or \
                        existing_record.weekday_pm != childcare_timing_record.weekday_pm or \
                        existing_record.weekday_all_day != childcare_timing_record.weekday_all_day or \
                        existing_record.weekend_am != childcare_timing_record.weekend_am or \
                        existing_record.weekend_pm != childcare_timing_record.weekend_pm or \
                        existing_record.weekend_all_day != childcare_timing_record.weekend_all_day:
                    application.childcare_timing_status = 'NOT_STARTED'

            childcare_timing_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)

            return HttpResponseRedirect(reverse('Childcare-Timing-Summary-View') + '?id=' + app_id)
        else:

            if application.application_status == 'FURTHER_INFORMATION':

                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'

            variables = {
                'form': form,
                'application_id': app_id,
                'childcare_timing_status': application.childcare_timing_status
            }
            return render(request, 'childcare-age-groups.html', variables)


class ChildcareTimingSummaryView(View):
    template_name = 'generic-summary-template.html'
    success_url = 'Task-List-View'

    def get(self, request):
        context = self.get_context_data(application_id=request.GET['id'])
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        application_id = self.request.GET['id']
        status.update(application_id, 'childcare_timing_status', 'COMPLETED')
        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)

    @staticmethod
    def get_context_data(application_id):  # Static method for use in Master-Summary-View.
        context = dict()
        context['application_id'] = application_id
        context['page_title'] = 'Check your answers: childcare timing'

        childcare_timing_record = ChildcareTiming.objects.get(application_id=application_id)

        context['table_list'] = ChildcareTimingSummaryView.childcare_timing_table_list(childcare_timing_record)

        return context

    @staticmethod
    def childcare_timing_table_list(childcare_timing_record):
        """
        Method to create a table list containing summary data for the childcare register applicants.
        :param childcare_training_record: Childcare Training record from which to grab data.
        :return: list of tables to be rendered on summary page.
        """
        childcare_timing_list = childcare_timing_record.get_field_names()
        row_value = ''
        for time in childcare_timing_list:
            if time:
                row_value += '\ndifferent time'
            else:
                row_value = 'None'


        # if childcare_timing_record.weekday_before_school:
        #     row_value = 'Weekday (before school)'
        # elif childcare_timing_record.weekday_after_school:
        #     row_value = 'Weekday (after school)'
        # elif childcare_timing_record.weekday_am:
        #     row_value = 'Weekday (morning)'
        # elif childcare_timing_record.weekday_pm:
        #     row_value = 'Weekday (afternoon)'
        # elif childcare_timing_record.weekday_all_day:
        #     row_value = 'Weekday (all day)'
        # elif childcare_timing_record.weekend_am:
        #     row_value = 'Weekend (morning)'
        # elif childcare_timing_record.weekend_pm:
        #     row_value = 'Weekend (afternoon)'
        # elif childcare_timing_record.weekend_all_day:
        #     row_value = 'Weekend (all day)'
        # else:
        #     row_value = 'None'

        childcare_timing_row = Row('time_of_childcare', 'At what time will the childcare occur?',
                                     row_value, 'Childcare-Timing-Summary-View','')

        childcare_timing_summary_table = Table([childcare_timing_record.pk])
        childcare_timing_summary_table.row_list = [childcare_timing_row]
        childcare_timing_summary_table.get_errors()
        childcare_timing_summary_table.error_summary_title = 'There was a problem'
        return [childcare_timing_summary_table]
