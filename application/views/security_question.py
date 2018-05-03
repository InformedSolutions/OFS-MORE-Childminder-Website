"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- security_question.py --

@author: Informed Solutions
"""

from django.shortcuts import render

from application.forms import SecurityQuestionForm, SecurityDateForm
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
    """
    Method to get the label that describes the type of question to be asked, given the question.
    :param q: Question to be asked.
    :return: str that describes the type of question.
    """
    if 'mobile' in q:
        return 'Mobile Number'
    if 'postcode' in q:
        return 'Postcode'
    if 'oldest' in q:
        return ''
    if 'dbs' in q:
        return 'DBS certificate number'


def get_answer(question, app_id):
    """
    Method to return the correct answer to the security question for a given applicant.
    :param question: Question to be asked.
    :param app_id: ID of the applicant of whom the security question is being asked.
    :return: dict object containing correct question answer and, if applicable, the correct date answer.
    """
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
    """
    Method to create list of forms instantiated with information entered by returning applicant and
    the correct answers for a given application. The form will later perform a validation to check if the answers
    are correct.
    :param question:
    :param r: request.POST object.
    :param app_id: ID for application of whom security question is being asked.
    :return: list of forms instantiated with corresponding information.
    """
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
    """
    Method to create list of forms instantiated with the correct answer to the security questions for a given appliacant.
    :param app_id: application ID of whom security question is being asked.
    :param question: Type of security question to be asked.
    :return: list of forms instantiated with the correct answer to each question.
    """
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
    """
    Method to determine security question to be asked, based on extent to which application is complete.
    :param app_id: ID of application of whom the secrity question is being asked.
    :return: str which identifies the type of question to be asked.
    """
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
    """
    Method to determine the oldest person in the house and return their date of birth.
    :param list: Lsit of objects representing the people in the house.
    :return: dict of date of birth for the oldest person.
    """
    oldest = {'birth_day': list[0].birth_day, 'birth_month': list[0].birth_month, 'birth_year': list[0].birth_year}
    for i in list:
        if i.birth_year <= oldest['birth_year']:
            if i.birth_month <= oldest['birth_month']:
                if i.birth_day < oldest['birth_day']:
                    oldest['birth_day'] = i.birth_day
                    oldest['birth_month'] = i.birth_month
                    oldest['birth_year'] = i.birth_year

    return oldest
