from django.http import HttpResponseRedirect

from application.forms.other_person_health_check.serious_illness import SeriousIllness, SeriousIllnessStart, \
    MoreSeriousIllnesses
from application.models import AdultInHome, HealthCheckCurrent, HealthCheckSerious, HealthCheckHospital
from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseFormView


class SeriousIllnessStartView(BaseFormView):
    """"
    Serious Illness start class to render the initial question on whether you have been admitted to hospital
    """
    template_name = 'other_people_health_check/serious_illness_start.html'
    form_class = SeriousIllnessStart
    success_url = 'Health-Check-Serious'

    def get_initial(self):
        """
        Get the initial values for the form
        :return: initial: dict of initial values.
        """
        initial = super().get_initial()
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        initial['has_illnesses'] = adult_record.serious_illness

        return initial

    def form_valid(self, form):
        """
        Method to redirect to the appropriate view dependant on the adults answer
        :return: redirect to appropriate success url.
        """
        clean = form.cleaned_data
        decision = clean['has_illnesses']
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        existing_records = HealthCheckSerious.objects.filter(person_id=adult_record)

        if decision == 'True':
            self.success_url = 'Health-Check-Serious'
            adult_record.serious_illness = True
        else:
            adult_record.serious_illness = False
            if existing_records.exists():
                existing_records.delete()
            if HealthCheckHospital.objects.filter(person_id=adult_record).exists():
                self.success_url = 'Health-Check-Summary'
            else:
                self.success_url = 'Health-Check-Hospital-Start'

        adult_record.serious_illness = decision
        adult_record.save()

        return HttpResponseRedirect(self.get_success_url())


class SeriousIllnessView(BaseFormView):
    """
    Class containing views for handling the pages relating to the serious illness page.
    """
    template_name = 'other_people_health_check/serious_illness.html'
    form_class = SeriousIllness
    success_url = 'Health-Check-Serious-More'

    def get_context_data(self, **kwargs):
        """
        Method to get data required for the context passed to template.
        :return: context; dict of variables to be rendered in the template.
        """
        context = super().get_context_data()
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        context['illnesses'] = HealthCheckSerious.objects.filter(
            person_id=person_record
        )

        return context

    def form_valid(self, form):
        """
        Method to save a serious illness record should the form be valid
        :return: redirect to appropriate success url.
        """
        illness_record = self._get_clean(form)
        illness_record.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        """
        Method to return keyword arguments passed to the form, including the associated AdultInHome record.
        :return: dict of keyword arguments.
        """
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        kwargs = super(SeriousIllnessView, self).get_form_kwargs()
        kwargs['adult'] = person_record

        return kwargs

    def get(self, request=None):
        """
        Handle get requests made to the SeriousIllnessView page.
        :return: response; HttpResponse containing information to be rendered.
        """
        response = super().get(request=self.request)
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)

        if self.request.GET.get('action') == 'Delete':
            HealthCheckSerious.objects.filter(pk=self.request.GET.get('illness_id')).delete()
            if not HealthCheckSerious.objects.filter(person_id=person_record).exists():
                return HttpResponseRedirect(build_url('Health-Check-Serious-Start', get={'person_id': person_id}))

        return response

    def _get_clean(self, form):
        """
        Method to return an updated HealthCheckSerious object using cleaned form data.
        :return: serious_illness_record; HealthCheckSerious model/object containing cleaned form data.
        """
        clean = form.cleaned_data
        description = clean['illness_details']
        start_date = clean['start_date']
        end_date = clean['end_date']
        person_id = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))

        serious_illness_record = HealthCheckSerious(
            description=description,
            start_date=start_date,
            end_date=end_date,
            person_id=person_id,
        )

        return serious_illness_record


class MoreSeriousIllnessesView(BaseFormView):
    """
    Class containting views handling the pages for adding serious illnesses.
    """
    template_name = 'other_people_health_check/more_serious_illnesses.html'
    form_class = MoreSeriousIllnesses

    def form_valid(self, form):
        """
        Method to redirect user to appropriate view, depending upon the health check's level of completion.
        :return: redirect to appropriate url
        """
        clean = form.cleaned_data
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        existing_records = HealthCheckHospital.objects.filter(person_id=adult_record)
        decision = clean['more_illnesses']

        if decision == 'True':
            self.success_url = 'Health-Check-Serious'
        else:
            if existing_records.exists():
                self.success_url = 'Health-Check-Summary'
            else:
                self.success_url = 'Health-Check-Hospital-Start'
        return HttpResponseRedirect(self.get_success_url())


class SeriousIllnessEditView(BaseFormView):
    """
    Class containting views handling the pages for editing serious illnesses.
    """
    template_name = 'other_people_health_check/serious_illness.html'
    form_class = SeriousIllness
    success_url = 'Health-Check-Summary'

    def get_initial(self):
        """
        Get the initial values for the form.
        :return: initial: dict of initial values for the form.
        """
        initial = super().get_initial()
        illness_record = HealthCheckSerious.objects.get(pk=self.request.GET.get('illness_id'))
        initial['illness_details'] = illness_record.description
        initial['start_date'] = illness_record.start_date
        initial['end_date'] = illness_record.end_date

        return initial

    def get_context_data(self, **kwargs):
        """
        Method to collect the data required for viewing the object.
        :return: context; dictionary of data required for viewing the object.
        """
        context = super().get_context_data()
        context['person_id'] = self.request.GET.get('person_id')
        context['illness_id'] = self.request.GET.get('illness_id')

        return context

    def form_valid(self, form):
        """
        Method to save illness record given adult and then call base class form_valid()
        :return: redirect to appropriate success url.
        """
        clean = form.cleaned_data
        description = clean['illness_details']
        start_date = clean['start_date']
        end_date = clean['end_date']
        illness_record = HealthCheckSerious.objects.get(pk=self.request.GET.get('illness_id'))
        illness_record.description = description
        illness_record.start_date = start_date
        illness_record.end_date = end_date
        illness_record.save()

        return super().form_valid(form)
