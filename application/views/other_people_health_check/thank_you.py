from application.middleware import CustomAuthenticationHandler
from application.models import AdultInHome, UserDetails, ApplicantName, Application
from application.notify import send_email
from application.status import update
from application.views import create_account_magic_link
from application.views.other_people_health_check.BaseViews import BaseTemplateView
from childminder import settings


class ThankYou(BaseTemplateView):

    template_name = 'other_people_health_check/thank_you.html'
    success_url_name = 'Health-Check-Thank-You'

    def get(self, request, *args, **kwargs):
        response = super().get(request=self.request)
        adult_record = AdultInHome.objects.get(pk=self.request.GET.get('person_id'))
        adult_name = ' '.join([adult_record.first_name , (adult_record.middle_names or '') ,adult_record.last_name])
        application = Application.objects.get(pk=adult_record.application_id)
        user_details = Application.objects.get(application_id=application)

        try:
            applicant = ApplicantName.objects.get(application_id=adult_record.application_id)

            firstname = applicant.first_name
        except:
            firstname = 'Applicant'

        if adult_record.health_check_status == 'To do':
            template_id = '8f5713f5-4437-479e-9fcc-262d0306f58c'
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(application)
            personalisation = {"link": link,
                               "firstName": firstname,
                               "Household Member Name": adult_name}
            r = send_email(email, personalisation, template_id)

            adult_record.health_check_status = 'Done'
            adult_record.save()
            all_adults = AdultInHome.objects.filter(application_id=adult_record.application_id)

            for adult in all_adults:
                if adult.health_check_status == 'To do':
                    cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
                    request.COOKIES[cookie_key] = None

                    CustomAuthenticationHandler.destroy_session(response)
                    return response

            template_id = '0acc42fa-9ba0-4c5e-8171-e49c08c22b67'
            email = user_details.email
            personalisation = {"link": link,
                               "firstName": adult_record.first_name,
                               "ApplicantName": firstname}
            r = send_email(email, personalisation, template_id)

            update(adult_record.application_id_id, 'people_in_home_status', 'COMPLETED')

        cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
        request.COOKIES[cookie_key] = None

        CustomAuthenticationHandler.destroy_session(response)
        return response