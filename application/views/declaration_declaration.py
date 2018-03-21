"""
Method returning the template for the Declaration page (for a given application) and navigating to
the task list when successfully completed
"""

from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..models import Application
from ..forms import DeclarationDeclarationForm, DeclarationDeclarationForm2

from .. import status


def declaration_declaration(request):
    """
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Declaration template
    """
    current_date = datetime.today()

    if request.method == 'GET':

        app_id = request.GET["id"]
        form = DeclarationDeclarationForm(id=app_id)
        form2 = DeclarationDeclarationForm2(id=app_id)
        application = Application.objects.get(pk=app_id)
        variables = {
            'form': form,
            'form2': form2,
            'application_id': app_id,
            'declarations_status': application.declarations_status
        }
        return render(request, 'declaration-declaration.html', variables)

    if request.method == 'POST':

        app_id = request.POST["id"]
        application = Application.objects.get(application_id=app_id)
        form = DeclarationDeclarationForm(request.POST, id=app_id)
        form.error_summary_title = 'There is a problem with this form (I am happy for Ofsted to)'
        form2 = DeclarationDeclarationForm2(request.POST, id=app_id)
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
                status.update(app_id,
                              'declarations_status', 'COMPLETED')
                return HttpResponseRedirect(reverse('Payment-View') + '?id=' + app_id)

    variables = {
        'form': form,
        'form2': form2,
        'application_id': app_id
    }

    return render(request, 'declaration-declaration.html', variables)
