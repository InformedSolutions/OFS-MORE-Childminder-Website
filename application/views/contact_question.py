"""
Method returning the template for the Your login and contact details
Question page (for a given application) and navigating to the Your login
and contact details: summary page when successfully completed
"""

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..forms import QuestionForm
from ..models import Application, UserDetails
from ..business_logic import reset_declaration


def contact_question(request):
    """
    :param request: a request object used to generate the HttpResponse

    :return: an HttpResponse object with the rendered
    Your login and contact details: question template
    """

    if request.method == 'GET':
        app_id = request.GET["id"]
        form = QuestionForm(id=app_id)
        form.check_flag()
        application = Application.get_id(app_id=app_id)
        variables = {
            'form': form,
            'application_id': app_id,
            'login_details_status': application.login_details_status,
            'childcare_type_status': application.childcare_type_status
        }

        return render(request, 'contact-question.html', variables)
    if request.method == 'POST':

        app_id = request.POST["id"]
        form = QuestionForm(request.POST, id=app_id)
        form.remove_flag()
        application = Application.get_id(app_id=app_id)

        # If form is not empty
        if form.is_valid():
            # Save security question and answer
            acc = UserDetails.get_id(app_id=app_id)
            security_answer = form.clean_security_answer()
            security_question = form.clean_security_question()
            acc.security_question = security_question
            acc.security_answer = security_answer
            acc.save()
            reset_declaration(application)

            return HttpResponseRedirect(
                reverse('Contact-Summary-View') + '?id=' + app_id)

        else:
            variables = {
                'form': form,
                'application_id': app_id,
                'login_details_status': application.login_details_status,
                'childcare_type_status': application.childcare_type_status
            }

            return render(request, 'contact-question.html', variables)
