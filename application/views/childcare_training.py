import collections

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import FormView, View

from ..table_util import Table, create_tables, submit_link_setter, Row
from ..summary_page_data import eyfs_name_dict, eyfs_link_dict, eyfs_change_link_description_dict

from .. import status
from ..business_logic import (childcare_register_type,
                              childcare_training_course_logic,)
from ..forms import EYFSDetailsForm, TypeOfChildcareTrainingForm
from ..models import Application, ChildcareTraining


class ChildcareTrainingGuidanceView(View):
    template_name = 'childcare-training-guidance.html'

    def get(self, request):
        return render(request, template_name=self.template_name, context=self.get_context_data())

    def post(self, request):
        application_id = request.GET['id']
        application = Application.objects.get(pk=application_id)

        if application.childcare_training_status != 'COMPLETED':
            status.update(application_id, 'childcare_training_status', 'IN_PROGRESS')

        register = childcare_register_type(application_id)

        if register == 'childcare_register_only':
            success_url = 'Type-Of-Childcare-Training-View'
        elif register == 'early_years_register':
            success_url = 'Childcare-Training-Details-View'

        return HttpResponseRedirect(reverse(success_url) + '?id=' + application_id)

    def get_context_data(self):
        context = dict()
        application_id = self.request.GET['id']
        context['application_id'] = application_id
        context['register'] = childcare_register_type(application_id)
        return context


class ChildcareTrainingDetailsView(FormView):
    template_name = 'childcare-training-details.html'
    form_class = EYFSDetailsForm
    success_url = 'Childcare-Training-Certificate-View'

    def get_context_data(self, **kwargs):
        context = super(ChildcareTrainingDetailsView, self).get_context_data(**kwargs)
        context['application_id'] = self.request.GET['id']
        return context

    def get_form_kwargs(self):
        kwargs = super(ChildcareTrainingDetailsView, self).get_form_kwargs()
        kwargs['id'] = self.request.GET['id']
        return kwargs

    def get_form(self, form_class=None):
        form = super(ChildcareTrainingDetailsView, self).get_form(form_class=None)
        if self.request.method == 'GET':
            form.check_flag()
        elif self.request.method == 'POST':
            form.remove_flag()
        return form

    def form_valid(self, form):
        application_id = self.request.GET['id']
        application = Application.objects.get(pk=application_id)

        if application.childcare_training_status != 'COMPLETED':
            status.update(application_id, 'childcare_training_status', 'IN_PROGRESS')

        training_record = childcare_training_course_logic(application_id, form)
        training_record.save()

        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)


class TypeOfChildcareTrainingView(FormView):
    template_name = 'childcare-training-type.html'
    form_class = TypeOfChildcareTrainingForm
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(TypeOfChildcareTrainingView, self).get_context_data(**kwargs)
        context['application_id'] = self.request.GET['id']
        return context

    def get_form_kwargs(self):
        kwargs = super(TypeOfChildcareTrainingView, self).get_form_kwargs()
        kwargs['id'] = self.request.GET['id']
        return kwargs

    def get_form(self, form_class=None):
        form = super(TypeOfChildcareTrainingView, self).get_form(form_class=None)
        if self.request.method == 'GET':
            form.check_flag()
        elif self.request.method == 'POST':
            form.remove_flag()
        return form

    def form_valid(self, form):
        application_id = self.request.GET['id']
        application = Application.objects.get(pk=application_id)

        if application.childcare_training_status != 'COMPLETED':
            status.update(application_id, 'childcare_training_status', 'IN_PROGRESS')

        training_record = childcare_training_course_logic(application_id, form)
        training_record.save()

        if 'no_training' in form.cleaned_data['childcare_training']:
            self.success_url = 'Childcare-Training-Course-Required-View'
        else:
            self.success_url = 'Childcare-Training-Certificate-View'

        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)


class ChildcareTrainingCourseRequiredView(View):
    template_name = 'childcare-training-course-required.html'
    success_url = 'Task-List-View'

    def get(self, request):
        return render(request, template_name=self.template_name, context=self.get_context_data())

    def post(self, request):
        application_id = self.request.GET['id']
        status.update(application_id, 'childcare_training_status', 'IN_PROGRESS')
        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)

    def get_context_data(self, **kwargs):
        context = dict()
        context['application_id'] = self.request.GET['id']
        return context


class ChildcareTrainingCertificateView(View):
    template_name = 'childcare-training-certificate.html'
    success_url = 'Childcare-Training-Summary-View'

    def get(self, request):
        return render(request, template_name=self.template_name, context=self.get_context_data())

    def post(self, request):
        application_id = request.GET['id']
        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)

    def get_context_data(self):
        context = dict()
        application_id = self.request.GET['id']
        context['application_id'] = application_id
        context['register'] = childcare_register_type(application_id)
        return context


class ChildcareTrainingSummaryView(View):
    template_name = 'generic-summary-template.html'
    success_url = 'Task-List-View'

    def get(self, request):
        context = self.get_context_data(application_id=request.GET['id'])
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        application_id = self.request.GET['id']
        status.update(application_id, 'childcare_training_status', 'COMPLETED')
        return HttpResponseRedirect(reverse(self.success_url) + '?id=' + application_id)

    @staticmethod
    def get_context_data(application_id):  # Static method for use in Master-Summary-View.
        context = dict()
        context['application_id'] = application_id
        context['page_title'] = 'Check your answers: childcare training'

        register = childcare_register_type(application_id)
        childcare_training_record = ChildcareTraining.objects.get(application_id=application_id)

        if register == 'childcare_register_only':
            context['table_list'] = ChildcareTrainingSummaryView.childcare_register_table_list(childcare_training_record)

        elif register == 'early_years_register':
            context['table_list'] = ChildcareTrainingSummaryView.eyfs_table_list(childcare_training_record)
            context = submit_link_setter(context, context['table_list'], 'eyfs_training', application_id)

        return context

    @staticmethod
    def childcare_register_table_list(childcare_training_record):
        """
        Method to create a table list containing summary data for the childcare register applicants.
        :param childcare_training_record: Childcare Training record from which to grab data.
        :return: list of tables to be rendered on summary page.
        """
        if childcare_training_record.eyfs_training and childcare_training_record.common_core_training:
            row_value = 'Training that covers the EYFS and training in common core skills'
        elif childcare_training_record.eyfs_training:
            row_value = 'Training that covers the EYFS'
        elif childcare_training_record.common_core_training:
            row_value = 'Training in common core skills'
        else:
            row_value = 'None'

        childcare_training_row = Row('childcare_training', 'What type of childcare course have you completed?',
                                     row_value, 'Type-Of-Childcare-Training-View', '')

        childcare_training_summary_table = Table([childcare_training_record.pk])
        childcare_training_summary_table.row_list = [childcare_training_row]
        childcare_training_summary_table.get_errors()
        childcare_training_summary_table.error_summary_title = 'There was a problem'
        return [childcare_training_summary_table]

    @staticmethod
    def eyfs_table_list(childcare_training_record):
        """
        Method to create a table list containing summary data for the EYFS applicants.
        :param childcare_training_record: Childcare Training record from which to grab data.
        :return: list of tables to be rendered on summary page.
        """
        # datetime.datetime.strptime(childcare_training_record.course_date, '%Y-%m-%d').date()

        eyfs_fields = collections.OrderedDict([
            ('eyfs_course_name', childcare_training_record.eyfs_course_name),
            ('eyfs_course_date', '/'.join([str(childcare_training_record.eyfs_course_date_day).zfill(2),
                                           str(childcare_training_record.eyfs_course_date_month).zfill(2),
                                           str(childcare_training_record.eyfs_course_date_year)]))
        ])

        eyfs_table = collections.OrderedDict({
            'table_object': Table([childcare_training_record.pk]),
            'fields': eyfs_fields,
            'title': '',
            'error_summary_title': 'There was a problem',
        })

        eyfs_table.error_summary_title = 'There was a problem'

        table_list = create_tables([eyfs_table], eyfs_name_dict, eyfs_link_dict, eyfs_change_link_description_dict)
        return table_list
