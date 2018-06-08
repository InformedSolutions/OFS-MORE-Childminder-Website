from application.middleware import CustomAuthenticationHandler
from application.models import AdultInHome, UserDetails, ApplicantName, Application, ArcComments
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
        adult_name = ' '.join([adult_record.first_name, (adult_record.middle_names or ''), adult_record.last_name])
        application = Application.objects.get(application_id=adult_record.application_id_id)
        user_details = UserDetails.objects.get(application_id=application.application_id)

        try:
            applicant = ApplicantName.objects.get(application_id=adult_record.application_id)

            firstname = applicant.first_name
        except:
            firstname = 'Applicant'

        if adult_record.health_check_status == 'To do' or adult_record.health_check_status == 'Flagged':
            template_id = '8f5713f5-4437-479e-9fcc-262d0306f58c'
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            personalisation = {"link": link,
                               "firstName": firstname,
                               "Household Member Name": adult_name}
            r = send_email(email, personalisation, template_id)
            print(link)
            # Delete ARC comment if it exists after recompleting the household member health check
            if ArcComments.objects.filter(table_pk=self.request.GET.get('person_id'),
                                                  field_name='health_check_status').count() > 0:
                arc_comment = ArcComments.objects.get(table_pk=self.request.GET.get('person_id'),
                                                      field_name='health_check_status')
                arc_comment.delete()
            adult_record.health_check_status = 'Done'
            adult_record.save()

            # Set task to Done if no ARC comments exist for task
            if ArcComments.objects.filter(table_pk=self.request.GET.get('person_id'),
                                          table_name='ADULT_IN_HOME').count() == 0:
                if ArcComments.objects.filter(table_pk=self.request.GET.get('person_id'),
                                          table_name='CHILD_IN_HOME').count() == 0:
                    application.people_in_home_status = 'COMPLETED'
                    application.save()

            all_adults = AdultInHome.objects.filter(application_id=adult_record.application_id)

            for adult in all_adults:
                if adult.health_check_status == 'To do':
                    cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
                    request.COOKIES[cookie_key] = None

                    CustomAuthenticationHandler.destroy_session(response)
                    return response

            template_id = '0acc42fa-9ba0-4c5e-8171-e49c08c22b67'
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            personalisation = {"link": link,
                               "firstName": firstname,
                               "ApplicantName": firstname}
            r = send_email(email, personalisation, template_id)
            print(link)

            update(adult_record.application_id_id, 'people_in_home_status', 'COMPLETED')

        cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
        request.COOKIES[cookie_key] = None

        CustomAuthenticationHandler.destroy_session(response)
        return response
