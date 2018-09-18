# from django.http import HttpResponseRedirect
# from django.views.generic import TemplateView
# from django.views.generic.base import TemplateResponseMixin
# from application.models import AdultInHome
#
# from application.forms.PITH_forms.PITH_lived_abroad_form import PITHLivedAbroadForm
# from application.utils import build_url, get_id
#
# from application.business_logic import get_adult_in_home, update_adult_in_home, get_childcare_register_type
#
#
# class PITHLivedAbroadView(TemplateView, TemplateResponseMixin):
#     template_name = 'PITH_templates/PITH_lived_abroad.html'
#     form_class = PITHLivedAbroadForm
#     success_url = ('PITH-Abroad-Criminal-View', 'PITH-Military-View', 'PITH-DBS-Check-View')
#     application_field_name = 'lived_abroad'
#     form_list = None
#
#     def get_context_data(self, **kwargs):
#         if 'form_list' not in kwargs:
#             kwargs['form_list'] = self.get_form_list()
#         return super().get_context_data(**kwargs)
#
#     def get_form_kwargs(self, adult=None):
#         """
#         Returns the keyword arguments for instantiating the form.
#         """
#         application_id = get_id(self.request)
#
#         kwargs = {
#             'initial': self.get_initial(),
#         }
#
#         if self.request.method in ('POST', 'PUT'):
#             kwargs.update({
#                 'data': self.request.POST,
#                 'files': self.request.FILES,
#             })
#
#         context = {
#             'id': application_id,
#             'application_field_name': self.application_field_name}
#
#         if adult:
#             context.update({
#                 'adult': adult
#             })
#
#         kwargs.update(context)
#         return kwargs
#
#     def get_success_url(self, get=None):
#         """
#         This view redirects to three potential phases.
#         This method is overridden to return those specific three cases.
#         :param get:
#         :return:
#         """
#         application_id = get_id(self.request)
#
#         if not get:
#             return build_url(self.get_choice_url(application_id), get={'id': application_id})
#         else:
#             return build_url(self.get_choice_url(application_id), get=get)
#
#     def post(self, request, *args, **kwargs):
#         """
#         Handles POST requests, instantiating a form instance with the passed
#         POST variables and then checked for validity.
#         """
#         form_list = self.get_form_list()
#         if all(form.is_valid() for form in form_list):
#             return self.form_valid(form_list)
#         else:
#             return self.form_invalid(form_list)
#
#     def form_valid(self, form):
#         """
#         If the form is valid, redirect to the supplied URL.
#         """
#         application_id = get_id(self.request)
#
#         adults = AdultInHome.objects.filter(application_id=application_id)
#
#         for adult in adults:
#             lived_abroad_bool = self.request.POST.get(self.application_field_name+str(adult.pk))
#
#             setattr(adult, self.application_field_name, lived_abroad_bool)
#             adult.save()
#         return HttpResponseRedirect(self.get_success_url())
#
#     def form_invalid(self, form):
#         """
#         If the form is invalid, re-render the context data with the
#         data-filled form and errors.
#         """
#         return self.render_to_response(self.get_context_data(form=form))
#
#     def get_form_list(self):
#         application_id = get_id(self.request)
#
#         adults = AdultInHome.objects.filter(application_id=application_id)
#
#         form_list = [self.form_class(**self.get_form_kwargs(adult=adult))
#                      for adult in adults]
#
#         sorted_form_list = \
#             sorted(form_list, key=lambda form: form.adult.adult)
#
#         return sorted_form_list
#
#     def get_initial(self):
#         application_id = get_id(self.request)
#
#         adults = AdultInHome.objects.filter(application_id=application_id)
#
#         initial_context = {self.application_field_name+str(adult.pk): adult.lived_abroad
#                            for adult in adults}
#
#         return initial_context
#
#     def get_num_forms(self):
#         return 5
#
#     def get_choice_bool(self):
#         return get_adult_in_home()
#
#     def get_choice_url(self, app_id):
#         adults = AdultInHome.objects.filter(application_id=app_id)
#
#         yes_choice, no_yes_choice, no_no_choice = self.success_url
#
#         childcare_register_status, childcare_register_cost = get_childcare_register_type(app_id)
#
#         if any(adult.lived_abroad for adult in adults):
#             return yes_choice
#         else:
#             if 'CR' in childcare_register_status and 'EYR' not in childcare_register_status:
#                 return no_yes_choice
#             else:
#                 return no_no_choice