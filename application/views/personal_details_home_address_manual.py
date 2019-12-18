"""
Method returning the template for the Your personal details:
home address manual page (for a given application)
and navigating to the Your personal details: location of care page when successfully completed;
business logic is applied to either create or update the associated Applicant_Name record
"""

from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .. import status
from ..models import Application, ApplicantPersonalDetails
from ..forms import PersonalDetailsHomeAddressManualForm
from ..business_logic import reset_declaration, personal_home_address_logic


def personal_details_home_address_manual(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Your personal details: home address template
    """
    current_date = timezone.now()

    if request.method == 'GET':
        application_id_local = request.GET["id"]
        application = Application.objects.get(pk=application_id_local)
        form = PersonalDetailsHomeAddressManualForm(id=application_id_local)
        form.check_flag()
        if application.application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem'
        variables = {
            'form': form,
            'application_id': application_id_local,
            'personal_details_status': application.personal_details_status
        }
        return render(request, 'personal-details-home-address-manual.html', variables)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        application = Application.objects.get(pk=application_id_local)

        form = PersonalDetailsHomeAddressManualForm(request.POST, id=application_id_local)
        form.remove_flag()

        if form.is_valid():

            home_address_record = personal_home_address_logic(application_id_local, form)
            home_address_record.save()
            moved_in_day, moved_in_month, moved_in_year = form.cleaned_data.get('moved_in_date')
            application = Application.objects.get(pk=application_id_local)
            application.date_updated = current_date
            application.save()
            personal_detail_record = ApplicantPersonalDetails.get_id(app_id=application_id_local)

            personal_detail_record.moved_in_day = moved_in_day
            personal_detail_record.moved_in_month = moved_in_month
            personal_detail_record.moved_in_year = moved_in_year
            personal_detail_record.save()

            if Application.objects \
                    .get(pk=application_id_local) \
                    .personal_details_status != 'COMPLETED':
                status.update(application_id_local, 'personal_details_status', 'IN_PROGRESS')

            reset_declaration(application)
            return HttpResponseRedirect(
                reverse('Personal-Details-Location-Of-Care-View') + '?id=' + application_id_local)
        else:
            form.error_summary_title = 'There was a problem with your address'
            if application.application_status == 'FURTHER_INFORMATION':
                form.error_summary_template_name = 'returned-error-summary.html'
                form.error_summary_title = 'There was a problem'
            variables = {
                'form': form,
                'application_id': application_id_local,
                'personal_details_status': application.personal_details_status
            }
            return render(request, 'personal-details-home-address-manual.html', variables)
