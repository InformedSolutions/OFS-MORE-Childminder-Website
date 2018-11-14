from application.middleware import CustomAuthenticationHandler
from application.models import AdultInHome, UserDetails, ApplicantName, Application, ArcComments
from application.notify import send_email
from application.status import update
from application.views import create_account_magic_link
from application.views.other_people_health_check.BaseViews import BaseTemplateView
from childminder import settings
from django.shortcuts import render


def qset_to_formatted_string(qset):
    if len(qset) == 1:
        name_string = qset[0].get_full_name

    else:
        names = [adult.get_full_name for adult in qset]
        name_string = ', '.join(names[:-1])
        name_string += ' and ' + names[-1]

    return name_string


class ThankYou(BaseTemplateView):

    success_url_name = 'Health-Check-Thank-You'

    def getStatus(self,application_id):

        dbs_qset = AdultInHome.objects.filter(application_id=application_id, capita=False, on_update=True)
        crc_qset = AdultInHome.objects.filter(application_id=application_id, lived_abroad=True)
        if len(dbs_qset)>0:
            if len(crc_qset)>0:
                self.template_name = 'other_people_health_check/thank_you_dbs_abroad.html'
                #TEMPLATE NAME IS BOTH
            else:
                self.template_name = 'other_people_health_check/thank_you_dbs.html'
                #TEMPLATE NAME IS JUST DBS
        elif len(crc_qset)>0:
            self.template_name = 'other_people_health_check/thank_you_abroad.html'
            #TEMPLATE NAME IS JUST CRC
        else:
            self.template_name = 'other_people_health_check/thank_you_neither.html'
            #TEMPLATE NAME IS NEITHER

    def get(self, request, *args, **kwargs):
        adult_id = self.request.GET.get('person_id')
        adult_record = AdultInHome.objects.get(pk=adult_id)
        adult_name = ' '.join([adult_record.first_name, (adult_record.middle_names or ''), adult_record.last_name])
        application_id = adult_record.application_id_id
        application = Application.objects.get(application_id=application_id)
        user_details = UserDetails.objects.get(application_id=application_id)

        try:
            applicant = ApplicantName.objects.get(application_id=application_id)
            applicantName = ' '.join([applicant.first_name, (applicant.middle_names or ''), applicant.last_name])

        except:
            applicantName = 'Applicant'

        # Initialises the correct template to load depending on whether the household member has a non-capita DBS check or lived abroad
        self.getStatus(application_id)

        response = super().get(request=self.request)
        if adult_record.health_check_status == 'To do' or adult_record.health_check_status == 'Started':
            template_id = '8f5713f5-4437-479e-9fcc-262d0306f58c'
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            personalisation = {"link": link,
                               "ApplicantName": applicantName,
                               "Household Member Name": adult_name}
            r = send_email(email, personalisation, template_id)
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


            dbs_qset = AdultInHome.objects.filter(application_id=application_id, capita=False, on_update=True)
            crc_qset = AdultInHome.objects.filter(application_id=application_id, lived_abroad=True)

            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            applicant = ApplicantName.objects.get(application_id=application_id)
            personalisation = {"link": link,
                               "firstName": applicant.first_name,
                               }
            #Personalisation parameters for the household member
            adult_personalisation={"firstName": adult_record.first_name,
                                   "ApplicantName": applicantName}
            if len(dbs_qset) > 0 and len(crc_qset) == 0:
                dbs_names_string = qset_to_formatted_string(dbs_qset)
                personalisation["dbs_names"] = dbs_names_string
                template_id = '9aa3a240-0a00-44bc-ac49-88125eb7c749'
                r = send_email(email, personalisation, template_id)
                adult_template_id = '2e9c097c-9e75-4198-9b5d-bab4b710e903'
                r = send_email(adult_record.email, adult_personalisation, adult_template_id)
                print(link)

            elif len(crc_qset) > 0 and len(dbs_qset) == 0:
                crc_names_string = qset_to_formatted_string(crc_qset)
                personalisation["crc_names"] = crc_names_string
                template_id = '07438eef-d88b-48fe-9812-2bc9e09dbae6'
                r = send_email(email, personalisation, template_id)
                adult_template_id = 'b598fceb-8c3d-46c3-a2fd-7f1568fa7b14'
                r = send_email(adult_record.email, adult_personalisation, adult_template_id)
                print(link)

            elif len(dbs_qset) > 0 and len(crc_qset) > 0:
                dbs_names_string = qset_to_formatted_string(dbs_qset)
                crc_names_string = qset_to_formatted_string(crc_qset)
                personalisation["dbs_names"] = dbs_names_string
                personalisation["crc_names"] = crc_names_string
                template_id = '5d5db808-2c83-41f6-adba-eda1b24c5714'
                r = send_email(email, personalisation, template_id)
                adult_template_id = '0df95124-4b08-4ed7-9881-70c4f0352767'
                r = send_email(adult_record.email, adult_personalisation, adult_template_id)
                print(link)

            else:
                template_id = '0acc42fa-9ba0-4c5e-8171-e49c08c22b67'
                r = send_email(email, personalisation, template_id)
                print(link)

            update(application_id, 'people_in_home_status', 'COMPLETED')

        adult_record.validated = True
        adult_record.save()
        self.send_survey_email(adult_record)


        context = {
            'ApplicantName': applicantName,
        }

        response = render(request, self.template_name, context)
        CustomAuthenticationHandler.destroy_session(response)
        return response

    def send_survey_email(self, adult_record):

        survey_template_id = '4f850789-b9c9-4192-adfa-fe66883c5872'
        email = adult_record.email

        survey_personalisation={
            'first_name': adult_record.first_name,
        }

        send_email(email, survey_personalisation, survey_template_id)
