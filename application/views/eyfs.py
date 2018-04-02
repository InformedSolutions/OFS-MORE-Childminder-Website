from django.utils import timezone

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .. import status
from ..business_logic import (eyfs_knowledge_logic,
                              eyfs_questions_logic,
                              eyfs_training_logic,
                              reset_declaration)
from ..forms import (EYFSGuidanceForm,
                     EYFSKnowledgeForm,
                     EYFSQuestionsForm,
                     EYFSSummaryForm,
                     EYFSTrainingForm)
from ..models import (Application,
                      EYFS)


def eyfs_guidance(request):
    """
    Method returning the template for the Early Years knowledge guidance page (for a given application) and navigating
    to the EYFS knowledge page when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: guidance template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSGuidanceForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        if application.eyfs_training_status != 'COMPLETED':
            status.update(application_id_local,
                          'eyfs_training_status', 'IN_PROGRESS')
        return render(request, 'eyfs-guidance.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSGuidanceForm(request.POST)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/knowledge?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-guidance.html', variables)


def eyfs_knowledge(request):
    """
    Method returning the template for the Early Years knowledge: knowledge page (for a given application)
    and navigating to the Early Years knowledge: training or question page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: knowledge template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSKnowledgeForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-knowledge.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSKnowledgeForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            # Create or update EYFS record
            eyfs_record = eyfs_knowledge_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            eyfs_understand = form.cleaned_data['eyfs_understand']
            if eyfs_understand == 'True':
                eyfs_record = EYFS.objects.get(
                    application_id=application_id_local)
                eyfs_record.eyfs_training_declare = False
                eyfs_record.save()
                reset_declaration(application)
                return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/questions?id=' + application_id_local)
            elif eyfs_understand == 'False':
                return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/training?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-knowledge.html', variables)


def eyfs_training(request):
    """
    Method returning the template for the Early Years knowledge: training page (for a given application)
    and navigating to the Early Years knowledge: question page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: training template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSTrainingForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-training.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSTrainingForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'IN_PROGRESS')
            # Create or update EYFS record
            eyfs_record = eyfs_training_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/questions?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-training.html', variables)


def eyfs_questions(request):
    """
    Method returning the template for the Early Years knowledge: questions page (for a given application)
    and navigating to the Early Years knowledge: summary page when successfully completed;
    business logic is applied to either create or update the associated EYFS record
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early Years knowledge: questions template
    """
    current_date = timezone.now()
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        form = EYFSQuestionsForm(id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_training_declare': eyfs_record.eyfs_training_declare,
            'eyfs_training_status': application.eyfs_training_status
        }
        return render(request, 'eyfs-questions.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSQuestionsForm(request.POST, id=application_id_local)
        application = Application.objects.get(pk=application_id_local)
        if form.is_valid():
            # Create or update EYFS record
            eyfs_record = eyfs_questions_logic(application_id_local, form)
            eyfs_record.save()
            application.date_updated = current_date
            application.save()
            reset_declaration(application)
            if application.eyfs_training_status != 'COMPLETED':
                status.update(application_id_local,
                              'eyfs_training_status', 'COMPLETED')
            return HttpResponseRedirect(settings.URL_PREFIX + '/eyfs/summary?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-questions.html', variables)


def eyfs_summary(request):
    """
    Method returning the template for the Early Years knowledge: summary page (for a given application)
    displaying entered data for this task and navigating to the task list when successfully completed
    :param request: a request object used to generate the HttpResponse
    :return: an HttpResponse object with the rendered Early years knowledge: summary template
    """
    if request.method == 'GET':
        application_id_local = request.GET["id"]
        eyfs_record = EYFS.objects.get(application_id=application_id_local)
        eyfs_understand = eyfs_record.eyfs_understand
        eyfs_training_declare = eyfs_record.eyfs_training_declare
        share_info_declare = eyfs_record.share_info_declare
        form = EYFSSummaryForm()
        application = Application.objects.get(pk=application_id_local)
        variables = {
            'form': form,
            'application_id': application_id_local,
            'eyfs_understand': eyfs_understand,
            'eyfs_training_declare': eyfs_training_declare,
            'share_info_declare': share_info_declare,
            'eyfs_training_status': application.eyfs_training_status,
        }
        return render(request, 'eyfs-summary.html', variables)
    if request.method == 'POST':
        application_id_local = request.POST["id"]
        form = EYFSSummaryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(settings.URL_PREFIX + '/task-list?id=' + application_id_local)
        else:
            variables = {
                'form': form,
                'application_id': application_id_local
            }
            return render(request, 'eyfs-summary.html', variables)
