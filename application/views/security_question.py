"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- security_question.py --

@author: Informed Solutions
"""

from django.shortcuts import render

from application.forms import SecurityQuestionForm, SecurityDateForm
from application.utils import date_combiner
from application import login_redirect_helper
from application.middleware import CustomAuthenticationHandler
from application.models import Application, UserDetails, ApplicantHomeAddress, ApplicantPersonalDetails, AdultInHome, \
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
        valid_forms = [form.is_valid() for form in forms]

        if all(valid_forms):
            response = login_redirect_helper.redirect_by_status(application)
            # Create session issue custom cookie to user
            CustomAuthenticationHandler.create_session(response, acc.email)

            # Forward back onto application
            return response

        variables = {
            'forms': forms,
            'question': question,
            'application_id': app_id,
            'label': get_label(question)
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
        dates = AdultInHome.objects.filter(application_id=app)
        date = get_oldest(dates)
        day = str(date['birth_day'])
        month = str(date['birth_month'])
        year = str(date['birth_year'])
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

    return form_list


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
        dates = AdultInHome.objects.filter(application_id=app)
        date = get_oldest(dates)
        form_list.append(SecurityDateForm(day=date['birth_day'], month=date['birth_month'], year=date['birth_year']))
    if 'dbs' in question:
        dbs = CriminalRecordCheck.objects.get(application_id=app)
        form_list.append(SecurityQuestionForm(answer=dbs.dbs_certificate_number))

    return form_list


def get_security_question(app_id):
    app = Application.objects.get(pk=app_id)
    acc = UserDetails.objects.get(application_id=app_id)
    question = ''
    if app.criminal_record_check_status == 'COMPLETED':
        question = 'dbs'
    elif app.people_in_home_status == 'COMPLETED':
        question = 'oldest'
    elif app.personal_details_status == 'COMPLETED':
        question = 'postcode'
    elif len(acc.mobile_number) != 0:
        question = 'mobile'
    return question


def get_oldest(list):
    oldest = {'birth_day': list[0].birth_day, 'birth_month': list[0].birth_month, 'birth_year': list[0].birth_year}
    for i in list:
        if i.birth_year <= oldest['birth_year']:
            if i.birth_month <= oldest['birth_month']:
                if i.birth_day < oldest['birth_day']:
                    oldest['birth_day'] = i.birth_day
                    oldest['birth_month'] = i.birth_month
                    oldest['birth_year'] = i.birth_year

    return oldest
