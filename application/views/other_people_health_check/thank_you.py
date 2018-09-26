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

    def clean_string_from_list(list):
        """

        :param list: List of adult names required for application emails
        :param string: Desired string name to be passed into email template
        :return: string with formatted names
        """
        string = ', '.join(list[-1])
        string = string + ' and ' + list[-1]

        return string

    def get(self, request, *args, **kwargs):
        response = super().get(request=self.request)
        adult_id = self.request.GET.get('person_id')
        adult_record = AdultInHome.objects.get(pk=adult_id)
        application_id = adult_record.application_id_id
        adult_name = ' '.join([adult_record.first_name, (adult_record.middle_names or ''), adult_record.last_name])
        application = Application.objects.get(application_id=application_id)
        user_details = UserDetails.objects.get(application_id=application_id)

        try:
            applicant = ApplicantName.objects.get(application_id=application_id)

            firstname = applicant.first_name
        except:
            firstname = 'Applicant'

        if adult_record.health_check_status == 'To do' or adult_record.health_check_status == 'Started':
            template_id = '8f5713f5-4437-479e-9fcc-262d0306f58c'
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            personalisation = {"link": link,
                               "firstName": firstname,
                               "Household Member Name": adult_name}
            r = send_email(email, personalisation, template_id)
            print(link)
            # Delete ARC comment if it exists after recompleting the household member health check
            if ArcComments.objects.filter(table_pk=application_id, field_name='health_check_status').count() > 0:
                arc_comment = ArcComments.objects.get(table_pk=application_id, field_name='health_check_status')
                arc_comment.delete()
            adult_record.health_check_status = 'Done'
            adult_record.save()

            # Set task to Done if all household members have recompleted their health check
            # and no ARC comments exist for task
            all_adults = AdultInHome.objects.filter(application_id=application_id)
            adults_todo = all_adults.filter(health_check_status='To do')
            adults_flagged = all_adults.filter(health_check_status='Started')
            if adults_flagged.count() == 0 and adults_todo.count() == 0:
                if ArcComments.objects.filter(table_pk=application_id, table_name='ADULT_IN_HOME').count() == 0:
                    if ArcComments.objects.filter(table_pk=application_id, table_name='CHILD_IN_HOME').count() == 0:
                        application.people_in_home_status = 'COMPLETED'
                        application.save()

            for adult in all_adults:
                if adult.health_check_status == 'To do':
                    cookie_key = CustomAuthenticationHandler.get_cookie_identifier()
                    request.COOKIES[cookie_key] = None

                    CustomAuthenticationHandler.destroy_session(response)
                    return response

            dbs_list = [adult for adult in all_adults if not all_adults.capita and not all_adults.on_update]
            crc_list = [adult for adult in all_adults if all_adults.lived_abroad]

            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            personalisation = {"link": link,
                               "firstName": firstname,
                               "ApplicantName": firstname
                               }

            dbs_names = ThankYou.clean_string_from_list(dbs_list)
            crc_names = ThankYou.clean_string_from_list(crc_list)

            if len(dbs_list) > 0 and len(crc_names) == 0:
                personalisation["dbs_names"] = dbs_names
                template_id = '9aa3a240-0a00-44bc-ac49-88125eb7c749'
                r = send_email(email, personalisation, template_id)
                print(link)

            elif len(crc_list) > 0 and len(dbs_list) == 0:
                personalisation["crc_names"] = crc_names
                template_id = '07438eef-d88b-48fe-9812-2bc9e09dbae6'
                r = send_email(email, personalisation, template_id)
                print(link)

            elif len(dbs_list) > 0 and len(crc_list) > 0:
                personalisation["dbs_names"] = dbs_names
                personalisation["crc_names"] = crc_names
                template_id = '5d5db808-2c83-41f6-adba-eda1b24c5714'
                r = send_email(email, personalisation, template_id)
                print(link)

            else:
                template_id = '0acc42fa-9ba0-4c5e-8171-e49c08c22b67'
                r = send_email(email, personalisation, template_id)
                print(link)

            update(application_id, 'people_in_home_status', 'COMPLETED')

        adult_record.validated = True
        adult_record.save()

        CustomAuthenticationHandler.destroy_session(response)
        return response
