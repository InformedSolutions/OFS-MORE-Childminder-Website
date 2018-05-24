from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.generic import FormView

from application.forms.other_person_health_check.current_illness import CurrentIllness
from application.forms.other_person_health_check.serious_illness import SeriousIllness, SeriousIllnessStart, \
    MoreSeriousIllnesses
from application.models import AdultInHome, HealthCheckCurrent, HealthCheckSerious, HealthCheckHospital
from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseFormView


class SeriousIllnessStartView(BaseFormView):

    template_name = 'other_people_health_check/serious_illness_start.html'
    form_class = SeriousIllnessStart
    success_url = 'Health-Check-Serious'

    def get_initial(self):

        initial = super().get_initial()
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))

        initial['has_illnesses'] = adult_record.serious_illness

        return initial

    def form_valid(self, form):
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

    template_name = 'other_people_health_check/serious_illness.html'
    form_class = SeriousIllness
    success_url = 'Health-Check-Serious-More'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        context['illnesses'] = HealthCheckSerious.objects.filter(
            person_id=person_record
        )

        return context

    def form_valid(self, form):
        illness_record = self._get_clean(form)
        illness_record.save()

        return super().form_valid(form)

    def get(self, request=None):
        response = super().get(request=self.request)

        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        if self.request.GET.get('action') == 'Delete':
            HealthCheckSerious.objects.filter(pk=self.request.GET.get('illness_id')).delete()
            if not HealthCheckSerious.objects.filter(person_id=person_record).exists():
                return HttpResponseRedirect(build_url('Health-Check-Serious-Start', get={'person_id': person_id}))

        return response


    def _get_clean(self, form):
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

    template_name = 'other_people_health_check/more_serious_illnesses.html'
    form_class = MoreSeriousIllnesses
    # success_url

    def form_valid(self, form):
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
    template_name = 'other_people_health_check/serious_illness.html'
    form_class = SeriousIllness
    success_url = 'Health-Check-Summary'

    def get_initial(self):

        initial = super().get_initial()

        illness_record = HealthCheckSerious.objects.get(pk=self.request.GET.get('illness_id'))

        initial['illness_details'] = illness_record.description
        initial['start_date'] = illness_record.start_date
        initial['end_date'] = illness_record.end_date

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['person_id'] = self.request.GET.get('person_id')
        context['illness_id'] = self.request.GET.get('illness_id')
        person_record = AdultInHome.objects.get(pk=context['person_id'])

        return context

    def form_valid(self, form):
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



