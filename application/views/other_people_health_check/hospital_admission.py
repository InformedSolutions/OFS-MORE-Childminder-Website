from django.http import HttpResponseRedirect

from application.forms.other_person_health_check.hospital_admission import HospitalAdmissionStart, HospitalAdmission, \
    MoreHospitalAdmissions
from application.models import AdultInHome, HealthCheckHospital
from application.utils import build_url
from application.views.other_people_health_check.BaseViews import BaseFormView


class HospitalAdmissionStartView(BaseFormView):
    """
    Hospital admission start class to render the initial question on whether you have been admitted to hospital
    """
    # See Django Form CBGV documentation for definition of these
    template_name = 'other_people_health_check/hospital_admission_start.html'
    form_class = HospitalAdmissionStart
    # This is inherited from custom BaseFormView to allow for build_url utility to be used
    success_url = 'Health-Check-Hospital'

    def get_initial(self):
        """
        Populated the form instance with initial data
        :return: a dictionary containing keys mapping to form fields and their respective initial values
        """

        initial = super().get_initial()
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))

        initial['has_illnesses'] = adult_record.hospital_admission

        return initial

    def form_valid(self, form):
        """
        Extended from BaseFormView to decide on redirect based off form data
        :param form:
        :return:
        """
        clean = form.cleaned_data
        decision = clean['has_illnesses']
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        existing_records = HealthCheckHospital.objects.filter(person_id=adult_record)

        if decision == 'True':
            # If there are already hospital record and this is reached, then it has been referred to from the summary
            # page, therefore the only question you need to change is this one before going back
            self.success_url = 'Health-Check-Hospital'
        else:
            # If they've said no, but there are already records, then they've changed their mind from the summary page
            if existing_records.exists():
                # So we delete the records and go back to the summary page
                existing_records.delete()
            self.success_url = 'Health-Check-Summary'

        adult_record.hospital_admission = decision
        adult_record.save()
        return HttpResponseRedirect(self.get_success_url())


class HospitalAdmissionView(BaseFormView):
    """
    Main detail view for the hospital admission set of pages
    """
    template_name = 'other_people_health_check/hospital_admission.html'
    form_class = HospitalAdmission
    success_url = 'Health-Check-Hospital-More'

    def get_context_data(self, **kwargs):
        """
        Returns the form fields to be prepopulated by the view
        :param kwargs:
        :return:
        """
        context = super().get_context_data()
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        context['illnesses'] = HealthCheckHospital.objects.filter(
            person_id=person_record
        )

        return context

    def form_valid(self, form):
        """
        Saves a hospital admission record, if the form is valid
        :param form:
        :return:
        """
        illness_record = self._get_clean(form)
        illness_record.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        """
        Returns the adult record associated with the person id to be used in start_date validations.
        :return:
        """
        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        kwargs = super(HospitalAdmissionView, self).get_form_kwargs()
        kwargs['adult'] = person_record
        return kwargs

    def get(self, request=None):
        """
        If a get request is performed, this checks to see if a 'delete' hyperlink was followed, and removes the
        associated record if so
        :param request:
        :return:
        """
        response = super().get(request=self.request)

        person_id = self.request.GET.get('person_id')
        person_record = AdultInHome.objects.get(pk=person_id)
        if self.request.GET.get('action') == 'Delete':
            HealthCheckHospital.objects.filter(pk=self.request.GET.get('illness_id')).delete()
            if not HealthCheckHospital.objects.filter(person_id=person_record).exists():
                return HttpResponseRedirect(build_url('Health-Check-Hospital-Start', get={'person_id': person_id}))

        return response

    def _get_clean(self, form):
        """
        Returns a hospital admission record that contains the data from the form sent to the view
        :param form:
        :return:
        """
        clean = form.cleaned_data
        description = clean['illness_details']
        start_date = clean['start_date']
        end_date = clean['end_date']
        person_id = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))

        hospital_admission_record = HealthCheckHospital(
            description=description,
            start_date=start_date,
            end_date=end_date,
            person_id=person_id,
        )

        return hospital_admission_record


class MoreHospitalAdmissionsView(BaseFormView):
    """
    View to ask whether the adult has had any more hospital admissions
    """
    template_name = 'other_people_health_check/more_hospital_admissions.html'
    form_class = MoreHospitalAdmissions
    success_url = None

    def form_valid(self, form):
        """
        If the form is valid, return them to the next or previous view dependant on the answer
        :param form:
        :return:
        """
        clean = form.cleaned_data
        decision = clean['more_illnesses']
        if decision == 'True':
            self.success_url = 'Health-Check-Hospital'
        else:
            self.success_url = 'Health-Check-Summary'
        return HttpResponseRedirect(self.get_success_url())


class HospitalAdmissionEditView(BaseFormView):
    """
    View to allow editing of a single hospital illness record once submitted (this is accessed from the summary page)
    """
    template_name = 'other_people_health_check/hospital_admission.html'
    form_class = HospitalAdmission
    success_url = 'Health-Check-Summary'

    def get_initial(self):
        """
        Populated the form instance with initial data
        :return: a dictionary containing keys mapping to form fields and their respective initial values
        """

        initial = super().get_initial()

        illness_id = self.request.GET.get('illness_id')

        illness_record = HealthCheckHospital.objects.get(pk=illness_id)

        initial['illness_details'] = illness_record.description
        initial['start_date'] = illness_record.start_date
        initial['end_date'] = illness_record.end_date

        return initial

    def get_context_data(self, **kwargs):
        """
        Returns the form fields to be prepopulated by the view
        :param kwargs:
        :return:
        """
        context = super().get_context_data()
        context['person_id'] = self.request.GET.get('person_id')
        context['illness_id'] = self.request.GET.get('illness_id')
        person_record = AdultInHome.objects.get(pk=context['person_id'])

        return context

    def form_valid(self, form):
        """
        Update the illness record, should it be valid
        :param form: The form instance to be checked
        :return:
        """
        clean = form.cleaned_data
        description = clean['illness_details']
        start_date = clean['start_date']
        end_date = clean['end_date']
        illness_record = HealthCheckHospital.objects.get(pk=self.request.GET.get('illness_id'))
        illness_record.description = description
        illness_record.start_date = start_date
        illness_record.end_date = end_date
        illness_record.save()

        return super().form_valid(form)


