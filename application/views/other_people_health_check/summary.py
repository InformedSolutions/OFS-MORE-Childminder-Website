from application.models import AdultInHome, HealthCheckCurrent, HealthCheckSerious, HealthCheckHospital
from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseTemplateView


class Summary(BaseTemplateView):
    template_name = 'other_people_health_check/summary.html'
    success_url_name = 'Health-Check-Serious'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['person_id'] = self.request.GET.get('person_id')
        person_object = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        context['declaration_url'] = build_url('Health-Check-Declaration', get={'person_id': context['person_id']})

        context['current_treatment_set'] = HealthCheckCurrent.objects.filter(person_id=self.request.GET.get('person_id'))
        context['serious_illness_set'] = HealthCheckSerious.objects.filter(person_id=person_object)
        context['hospital_admission_set'] = HealthCheckHospital.objects.filter(person_id=person_object)

        context['current_treatment_bool'] = person_object.current_treatment
        context['serious_illness_bool'] = person_object.serious_illness
        context['hospital_admission_bool'] = person_object.hospital_admission

        return context



