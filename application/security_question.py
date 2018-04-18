"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- security_question.py --

@author: Informed Solutions
"""

from django.shortcuts import render

from application.forms import SecurityQuestionForm, SecurityDateForm
from application.utils import date_combiner
from . import login_redirect_helper
from .middleware import CustomAuthenticationHandler
from .models import Application, UserDetails, ApplicantHomeAddress, ApplicantPersonalDetails, AdultInHome, \
    CriminalRecordCheck


def question(request):
    """
    Method returning the template for the security question verification page
    and navigating to the corresponding task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered security question verification template
    """
    if request.method == 'GET':
        app_id = request.GET['id']
        question = get_security_question(app_id)
        forms = get_forms(app_id, question)

        variables = {
            'forms': forms,
            'question': question,
            'application_id': app_id,
            'label': get_label(question)
        }

        return render(request, 'security-question.html', variables)

    if request.method == 'POST':
        app_id = request.POST['id']
        question = get_security_question(app_id)
        forms = post_forms(question, request.POST, app_id)
        application = Application.objects.get(pk=app_id)
        acc = UserDetails.objects.get(application_id=application)
        security_question = acc.security_question
        if forms == True:

            response = login_redirect_helper.redirect_by_status(application)
            # Create session issue custom cookie to user
            CustomAuthenticationHandler.create_session(response, acc.email)

            # Forward back onto application
            return response
        else:
            error_message = ''
            if 'wrong' in str(forms):
                error_message = 'Your answer must match what you told us in your application'
            if 'empty' in str(forms):
                error_message = 'Please give an answer'

            variables = {
                'forms': get_forms(app_id, question),
                'question': question,
                'application_id': app_id,
                'label': get_label(question),
                'error': error_message
            }
            return render(request, 'security-question.html', variables)


def get_label(q):
    if 'mobile' in q:
        return 'Mobile Number'
    if 'postcode' in q:
        return 'Postcode'
    if 'oldest' in q:
        return ''
    if 'dbs' in q:
        return 'DBS certificate number'


def get_answer(question, app_id):
    date = []
    app = Application.objects.get(application_id=app_id)
    acc = UserDetails.objects.get(application_id=app)
    if 'mobile' in question:
        question = acc.mobile_number
    if 'postcode' in question:
        home = ApplicantHomeAddress.objects.get(application_id=app, current_address=True)
        date = ApplicantPersonalDetails.objects.get(application_id=app)
        question = home.postcode
        day = str(date.birth_day)
        month = str(date.birth_month)
        year = str(date.birth_year)
        date = [day, month, year]
    if 'oldest' in question:
        date = AdultInHome.objects.get(application_id=app)
        day = str(date.birth_day)
        month = str(date.birth_month)
        year = str(date.birth_year)
        date = [day, month, year]
    if 'dbs' in question:
        dbs = CriminalRecordCheck.objects.get(application_id=app)
        question = dbs.dbs_certificate_number

    return {'question': question, 'date': date}


def post_forms(question, r, app_id):
    form_list = []
    answer = get_answer(question, app_id)
    field_answer = answer['question']
    date_answer = answer['date']
    if 'mobile' in question:
        form_list.append(SecurityQuestionForm(r, answer=field_answer))
    if 'postcode' in question:
        day = date_answer[0]
        month = date_answer[1]
        year = date_answer[2]
        form_list.append(SecurityQuestionForm(r, answer=field_answer))
        form_list.append(SecurityDateForm(r, day=day, month=month, year=year))
    if 'oldest' in question:
        day = date_answer[0]
        month = date_answer[1]
        year = date_answer[2]
        form_list.append(SecurityDateForm(r, day=day, month=month, year=year))
    if 'dbs' in question:
        form_list.append(SecurityQuestionForm(r, answer=field_answer))

    return validate_forms(form_list)


def validate_forms(forms):
    for i in forms:
        if i.is_valid():
            try:
                i.clean_security_answer()
            except Exception as ex:
                return ex
        elif hasattr(i, 'error'):
            return i.error
        else:
            return 'empty'
    return True


def get_forms(app_id, question):
    form_list = []
    app = Application.objects.get(application_id=app_id)
    acc = UserDetails.objects.get(application_id=app)
    if 'mobile' in question:
        form_list.append(SecurityQuestionForm(answer=acc.mobile_number))
    if 'postcode' in question:
        home = ApplicantHomeAddress.objects.get(application_id=app, current_address=True)
        date = ApplicantPersonalDetails.objects.get(application_id=app)
        form_list.append(SecurityQuestionForm(answer=home.postcode))
        form_list.append(SecurityDateForm(day=date.birth_day, month=date.birth_month, year=date.birth_year))
    if 'oldest' in question:
        date = AdultInHome.objects.get(application_id=app)
        form_list.append(SecurityDateForm(day=date.birth_day, month=date.birth_month, year=date.birth_year))
    if 'dbs' in question:
        dbs = CriminalRecordCheck.objects.get(application_id=app)
        form_list.append(SecurityQuestionForm(answer=dbs.dbs_certificate_number))

    return form_list


def get_security_question(app_id):
    app = Application.objects.get(pk=app_id)
    acc = UserDetails.objects.get(application_id=app_id)
    question = ''
    if len(acc.mobile_number) != 0:
        question = 'mobile'
        if app.personal_details_status == 'COMPLETED':
            # set form to ask for birth day and postcode
            question = 'postcode'
            if app.people_in_home_status == 'COMPLETED':
                question = 'oldest'
            elif app.criminal_record_check_status == 'COMPLETED':
                question = 'dbs'
    return question
