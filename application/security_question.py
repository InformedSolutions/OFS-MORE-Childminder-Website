"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- security_question.py --

@author: Informed Solutions
"""

from django.shortcuts import render

from . import login_redirect_helper
from .forms import VerifySecurityQuestionForm
from .middleware import CustomAuthenticationHandler
from .models import Application, UserDetails


def load(request):
    """
    Method returning the template for the security question verification page
    and navigating to the corresponding task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered security question verification template
    """
    if request.method == 'GET':
        application_id_local = request.GET['id']
        form = VerifySecurityQuestionForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        acc = UserDetails.objects.get(application_id=application)
        security_question = set_security_question(application_id_local)
        return render(request, 'security_question.html',
                      {'form': form, 'application_id': application_id_local, 'question': security_question})
    if request.method == 'POST':
        application_id_local = request.POST['id']
        form = VerifySecurityQuestionForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        acc = UserDetails.objects.get(application_id=application)
        security_question = acc.security_question
        if form.is_valid():
            if acc.security_answer == form.clean_security_answer():
                response = login_redirect_helper.redirect_by_status(application)

                # Create session issue custom cookie to user
                CustomAuthenticationHandler.create_session(response, acc.email)

                # Forward back onto application
                return response
        else:
            variables = {
                'form': form,
                'application_id': application_id_local,
                'question': security_question
            }
            return render(request, 'security_question.html', variables)


def set_security_question(app_id):
    app = Application.objects.get(pk=app_id)
    acc = UserDetails.objects.get(application_id=app_id)
    form = None

    if len(acc.mobile_number) != 0:
        # set form to the phone number security question
        if app.personal_details_status == 'COMPLETED':
            # set form to ask for birth day and postcode
            if app.people_in_home_status == 'COMPLETED':

                if app.criminal_record_check_status == 'COMPLETED':
                    pass
    return form


