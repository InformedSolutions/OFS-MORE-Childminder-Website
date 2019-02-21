from application.middleware import CustomAuthenticationHandler
from application.models import AdultInHome, UserDetails, ApplicantName, Application, ArcComments
from application.notify import send_email
from application.status import update
from application.views import create_account_magic_link
from application.views.other_people_health_check.BaseViews import BaseTemplateView
from childminder import settings
from django.shortcuts import render
import logging
from ..dbs import NO_ADDITIONAL_CERTIFICATE_INFORMATION

logger = logging.getLogger()

def get_name_formatted_string(adult_list):
    if len(adult_list) == 1:
        name_string = adult_list[0].get_full_name

    else:
        names = [adult.get_full_name for adult in adult_list]
        name_string = ', '.join(names[:-1])
        name_string += ' and ' + names[-1]

    return name_string


class ThankYou(BaseTemplateView):

    success_url_name = 'Health-Check-Thank-You'


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

            # get applicant email details
            email = user_details.email
            link = str(settings.PUBLIC_APPLICATION_URL) + '/validate/' + create_account_magic_link(user_details)
            applicant = ApplicantName.objects.get(application_id=application_id)
            personalisation = {"link": link,
                               "firstName": applicant.first_name,
                               }
            # send email to applicant
            self.send_applicant_email(application_id, personalisation, email)

            update(application_id, 'people_in_home_status', 'COMPLETED')

        adult_record.validated = True
        adult_record.save()

        # email will not be sent if the health check if flagged
        if not application.health_arc_flagged:
            self.send_survey_email(adult_record)

        context = {
            'ApplicantName': applicantName,
        }

        response = render(request, self.template_name, context)
        CustomAuthenticationHandler.destroy_session(response)
        return response

    @staticmethod
    def send_survey_email(adult_record):

        survey_template_id = '4f850789-b9c9-4192-adfa-fe66883c5872'
        email = adult_record.email

        survey_personalisation={
            'first_name': adult_record.first_name,
        }

        send_email(email, survey_personalisation, survey_template_id)

    @staticmethod
    def get_templates(capita, certificate_information, lived_abroad, within_three_months, on_update):
        """
        method to get the email template id and template name
        :param capita: the adults capita field
        :param certificate_information: adult's certificate_information
        :param lived_abroad: adult's lived abroad field
        :param within_three_months: adult's within_three_months field
        :param on_update: adult's update field
        :return: relevant email template id and template name
        """
        # email template ids below
        DBS_ONLY_TEMPLATE_ID = '2e9c097c-9e75-4198-9b5d-bab4b710e903'
        DBS_LIVED_ABROAD_TEMPLATE_ID = '0df95124-4b08-4ed7-9881-70c4f0352767'
        LIVED_ABROAD_ONLY_TEMPLATE_ID = 'b598fceb-8c3d-46c3-a2fd-7f1568fa7b14'
        # templates below
        DBS_ONLY_TEMPLATE_NAME = 'other_people_health_check/thank_you_dbs.html'
        DBS_LIVED_ABROAD_TEMPLATE_NAME = 'other_people_health_check/thank_you_dbs_abroad.html'
        LIVED_ABROAD_ONLY_TEMPLATE_NAME = 'other_people_health_check/thank_you_abroad.html'
        NEITHER_TEMPLATE_NAME = 'other_people_health_check/thank_you_neither.html'
        # email templates and relevant templates
        DBS_ONLY_TEMPLATES = DBS_ONLY_TEMPLATE_ID, DBS_ONLY_TEMPLATE_NAME
        DBS_LIVED_ABROAD_TEMPLATES = DBS_LIVED_ABROAD_TEMPLATE_ID, DBS_LIVED_ABROAD_TEMPLATE_NAME
        LIVED_ABROAD_ONLY_TEMPLATES = LIVED_ABROAD_ONLY_TEMPLATE_ID, LIVED_ABROAD_ONLY_TEMPLATE_NAME
        NEITHER_TEMPLATES = None, NEITHER_TEMPLATE_NAME

        if capita:
            if within_three_months:
                if certificate_information not in NO_ADDITIONAL_CERTIFICATE_INFORMATION:
                    if lived_abroad:
                        logger.debug(
                            'Attempting send of email "Household member completed - Confirmation - DBS & lived abroad"')
                        return DBS_LIVED_ABROAD_TEMPLATES
                    else:
                        logger.debug('Attempting send of email "Household member completed - Confirmation - DBS"')
                        return DBS_ONLY_TEMPLATES
                else:
                    if lived_abroad:
                        logger.debug(
                            'Attempting send of email "Household member completed - Confirmation - lived abroad"')
                        return LIVED_ABROAD_ONLY_TEMPLATES
                    else:
                        return NEITHER_TEMPLATES
            else:
                if on_update:
                    if lived_abroad:
                        logger.debug(
                            'Attempting send of email "Household member completed - Confirmation - DBS & lived abroad"')
                        return DBS_LIVED_ABROAD_TEMPLATES
                    else:
                        logger.debug('Attempting send of email "Household member completed - Confirmation - DBS"')
                        return DBS_ONLY_TEMPLATES
                else:
                    logger.debug("""The following combination is not covered in if block: 
                                    on_update {0} """.format(on_update))
                    raise ValueError("""
                                    The following combination is not covered in if block: 
                                    on_update {0} """.format(on_update))
        else:
            if on_update:
                if lived_abroad:
                    logger.debug('Attempting send of email "Household member completed - Confirmation - DBS & lived abroad"')
                    return DBS_LIVED_ABROAD_TEMPLATES
                else:
                    logger.debug('Attempting send of email "Household member completed - Confirmation - DBS"')
                    return DBS_ONLY_TEMPLATES
            else:
                logger.debug("""The following combination is not covered in if block: 
                on_update {0} """.format(on_update))
                raise ValueError("""
                The following combination is not covered in if block: 
                on_update {0} """.format(on_update))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_template_names(self):
         """
         Handles logic on returning the templates and sending emails
         :return: template string
         """
         adult_id = self.request.GET.get('person_id')
         adult_record = AdultInHome.objects.get(pk=adult_id)
         application_id = adult_record.application_id_id
         applicant = ApplicantName.objects.get(application_id=application_id)
         applicant_name = ' '.join([applicant.first_name, (applicant.middle_names or ''), applicant.last_name])
         # get adult personalisation
         adult_personalisation = {"firstName": adult_record.first_name,
                                  "ApplicantName": applicant_name}
         # get adults crc details
         capita = adult_record.capita
         lived_abroad = adult_record.lived_abroad
         within_three_months = adult_record.within_three_months
         certificate_information = adult_record.certificate_information
         on_update = adult_record.on_update
         # get email template id and template name
         templates = self.get_templates(capita, certificate_information, lived_abroad, within_three_months, on_update)
         adult_template_id = templates[0]
         if adult_template_id is not None:
             r = send_email(adult_record.email, adult_personalisation, adult_template_id)
         # assign template id
         self.template_name = templates[1]
         return self.template_name

    def send_applicant_email(self, application_id, personalisation, email):
        """
        method to send email to the applicant when all adults have completed the health check
        :param application_id: application id
        :param personalisation: email personalisation
        :param email: email address
        :return:
        """
        dbs_list = list(AdultInHome.objects.filter(application_id=application_id, capita=True,
                                               within_three_months=True,
                                               certificate_information=NO_ADDITIONAL_CERTIFICATE_INFORMATION))
        lived_abroad_list = list(AdultInHome.objects.filter(application_id=application_id, lived_abroad=True))
        adult_list = list(AdultInHome.objects.filter(application_id=application_id))
        if any(dbs_list):
            if any(lived_abroad_list):
                lived_abroad_names_string = get_name_formatted_string(lived_abroad_list)
                personalisation["crc_names"] = lived_abroad_names_string
                template_id = '07438eef-d88b-48fe-9812-2bc9e09dbae6'
                r = send_email(email, personalisation, template_id)
                logger.debug('Attempting send of email "Confirm completion of all household member’s health checks CRC only"')
                print(personalisation["link"])
            else:
                template_id = '0acc42fa-9ba0-4c5e-8171-e49c08c22b67'
                r = send_email(email, personalisation, template_id)
                logger.debug('Attempting send of email "Confirm completion of all household member’s health checks"')
                print(personalisation["link"])
        else:
            if any(lived_abroad_list):
                dbs_post_list = list(set(adult_list) - set(dbs_list))
                dbs_names_string = get_name_formatted_string(dbs_post_list)
                lived_abroad_names_string = get_name_formatted_string(lived_abroad_list)
                personalisation["dbs_names"] = dbs_names_string
                personalisation["crc_names"] = lived_abroad_names_string
                template_id = '5d5db808-2c83-41f6-adba-eda1b24c5714'
                r = send_email(email, personalisation, template_id)
                logger.debug('Attempting send of email "Confirm completion of all household member’s health checks DBS and CRC"')
                print(personalisation["link"])
            else:
                dbs_names_string = get_name_formatted_string(dbs_list)
                personalisation["dbs_names"] = dbs_names_string
                template_id = '9aa3a240-0a00-44bc-ac49-88125eb7c749'
                logger.debug('Attempting send of email "Confirm completion of all household member’s health checks DBS"')
                r = send_email(email, personalisation, template_id)
