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

        application_id_local = request.GET["id"]
        form = QuestionForm(id=application_id_local)
        form.check_flag()
        application = Application.objects.get(pk=application_id_local)

    if request.method == 'POST':

        application_id_local = request.POST["id"]
        form = QuestionForm(request.POST, id=application_id_local)
        form.remove_flag()
        application = Application.objects.get(pk=application_id_local)

        # If form is not empty
        if form.is_valid():

            # Save security question and answer
            login_id = application.login_id.login_id
            acc = UserDetails.objects.get(login_id=login_id)
            security_answer = form.clean_security_answer()
            security_question = form.clean_security_question()
            acc.security_question = security_question
            acc.security_answer = security_answer
            acc.save()
            reset_declaration(application)
            return HttpResponseRedirect(
                reverse('Contact-Summary-View') + '?id=' + application_id_local)

    variables = {
        'form': form,
        'application_id': application_id_local,
        'login_details_status': application.login_details_status,
        'childcare_type_status': application.childcare_type_status
    }
    return render(request, 'contact-question.html', variables)
