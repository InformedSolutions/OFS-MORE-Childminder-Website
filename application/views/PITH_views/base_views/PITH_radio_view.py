from application.business_logic import (get_adult_in_home,
                                        update_adult_in_home,
                                        get_application,
                                        update_application)
from application.utils import build_url, get_id
from django.views.generic.edit import FormView


class PITHRadioView(FormView):
    success_url = (None, None)
    PITH_field_name = None
    application_field_name = None

    def get_initial(self):
        application_id = get_id(self.request)
        initial = super().get_initial()
        active_model, active_field_name = self.get_active_field()

        if active_model == 'PITH':
            adult_in_home_field = get_adult_in_home(application_id, active_field_name)
            initial[self.PITH_field_name] = adult_in_home_field
        elif active_model == 'Application':
            adult_in_home_field = get_application(application_id, active_field_name)
            initial[self.application_field_name] = adult_in_home_field

        return initial

    def get_success_url(self, get=None):
        application_id = get_id(self.request)
        yes_choice, no_choice = self.success_url

        active_model, active_field_name = self.get_active_field()

        if active_model == 'PITH':
            choice_bool = get_adult_in_home(application_id, active_field_name)
        elif active_model == 'Application':
            choice_bool = get_application(application_id, active_field_name)
        else:
            raise ValueError("Wasn't able to select a url in {0}, active_model not recognized.".format(self.__name__))

        if choice_bool:
            redirect_url = yes_choice
        else:
            redirect_url = no_choice

        if not get:
            return build_url(redirect_url, get={'id': application_id})
        else:
            return build_url(redirect_url, get=get)

    def get_form_kwargs(self):
        application_id = get_id(self.request)
        kwargs = super().get_form_kwargs()
        active_model, active_field_name = self.get_active_field()

        kwargs['id'] = application_id

        if active_model == 'PITH':
            kwargs['PITH_field_name'] = active_field_name
        elif active_model == 'Application':
            kwargs['application_field_name'] = active_field_name

        return kwargs

    def get_context_data(self, **kwargs):
        application_id = get_id(self.request)
        application_status = get_application(application_id, 'application_status')
        form = self.get_form()

        if application_status == 'FURTHER_INFORMATION':
            form.error_summary_template_name = 'returned-error-summary.html'
            form.error_summary_title = 'There was a problem on this page'

        form.check_flag()

        context = {'id': application_id}

        if 'form' not in kwargs:
            context['form'] = form

        return super().get_context_data(**context, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        form.remove_flag()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        application_id = get_id(self.request)

        # Update task status if flagged or completed (people_in_home_status)
        people_in_home_status = get_application(application_id, 'people_in_home_status')

        if people_in_home_status in ['FLAGGED', 'COMPLETED']:
            # Update the task status to 'IN_PROGRESS' from 'FLAGGED'
            update_application(application_id, 'people_in_home_status', 'IN_PROGRESS')

        active_model, active_field_name = self.get_active_field()

        if active_model == 'PITH':
            update_bool = self.request.POST.get(active_field_name) == 'True'
            successfully_updated = update_adult_in_home(application_id, active_field_name, update_bool)
        elif active_model == 'Application':
            update_bool = self.request.POST.get(active_field_name) == 'True'
            successfully_updated = update_application(application_id, active_field_name, update_bool)

        return super().form_valid(form)

    def get_active_field(self):
        if self.PITH_field_name:
            return 'PITH', self.PITH_field_name
        elif self.application_field_name:
            return 'Application', self.application_field_name
        else:
            raise ValueError('PITH_field_name and application_field_name cannot both be None')