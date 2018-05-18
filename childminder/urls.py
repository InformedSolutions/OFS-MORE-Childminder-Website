"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- URLs --

@author: Informed Solutions
"""
import re

from django.conf import settings
from django.conf.urls import url, include
from django.views.generic import TemplateView

from application import views, utils
from application.views import security_question, magic_link


urlpatterns = [
    url(r'^$', views.start_page, name='start-page.html'),
    url(r'^task-list/', views.task_list, name='Task-List-View'),
    url(r'^childcare/guidance/', views.type_of_childcare_guidance, name='Type-Of-Childcare-Guidance-View'),
    url(r'^childcare/age-groups/', views.type_of_childcare_age_groups, name='Type-Of-Childcare-Age-Groups-View'),
    url(r'^childcare/register/', views.type_of_childcare_register, name='Type-Of-Childcare-Register-View'),
    url(r'^childcare/local-authority/', views.local_authority_links, name='Local-Authority-View'),
    url(r'^childcare/overnight-care/', views.overnight_care, name='Type-Of-Childcare-Overnight-Care-View'),
    url(r'^childcare/summary/', views.childcare_type_summary, name='Type-Of-Childcare-Summary-View'),
    url(r'^sign-in/change-email/', views.UpdateEmailView.as_view(), name='Contact-Email-View'),
    url(r'^account/phone/', views.contact_phone, name='Contact-Phone-View'),
    url(r'^sign-in/check-answers/', views.contact_summary, name='Contact-Summary-View'),
    url(r'^personal-details/$', views.personal_details_guidance, name='Personal-Details-Guidance-View'),
    url(r'^personal-details/your-name/', views.personal_details_name, name='Personal-Details-Name-View'),
    url(r'^personal-details/your-date-of-birth/', views.personal_details_dob, name='Personal-Details-DOB-View'),
    url(r'^personal-details/your-home-address/', views.personal_details_home_address,
        name='Personal-Details-Home-Address-View'),
    url(r'^personal-details/select-home-address/', views.personal_details_home_address_select,
        name='Personal-Details-Home-Address-Select-View'),
    url(r'^personal-details/enter-home-address/', views.personal_details_home_address_manual,
        name='Personal-Details-Home-Address-Manual-View'),
    url(r'^personal-details/home-address-details/', views.personal_details_location_of_care,
        name='Personal-Details-Location-Of-Care-View'),
    url(r'^personal-details/childcare-address/', views.personal_details_childcare_address,
        name='Personal-Details-Childcare-Address-View'),
    url(r'^personal-details/select-childcare-address/', views.personal_details_childcare_address_select,
        name='Personal-Details-Childcare-Address-Select-View'),
    url(r'^personal-details/enter-childcare-address/', views.personal_details_childcare_address_manual,
        name='Personal-Details-Childcare-Address-Manual-View'),
    url(r'^personal-details/check-answers/', views.personal_details_summary, name='Personal-Details-Summary-View'),
    url(r'^first-aid/$', views.first_aid_training_guidance, name='First-Aid-Training-Guidance-View'),
    url(r'^first-aid/details/', views.first_aid_training_details, name='First-Aid-Training-Details-View'),
    url(r'^first-aid/certificate/', views.first_aid_training_declaration, name='First-Aid-Training-Declaration-View'),
    url(r'^first-aid/renew/', views.first_aid_training_renew, name='First-Aid-Training-Renew-View'),
    url(r'^first-aid/update/', views.first_aid_training_training, name='First-Aid-Training-Training-View'),
    url(r'^first-aid/check-answers/', views.first_aid_training_summary, name='First-Aid-Training-Summary-View'),
    url(r'^criminal-record/$', views.dbs_check_guidance, name='DBS-Check-Guidance-View'),
    url(r'^criminal-record/your-details/', views.dbs_check_dbs_details, name='DBS-Check-DBS-Details-View'),
    url(r'^criminal-record/post-certificate/', views.dbs_check_upload_dbs, name='DBS-Check-Upload-DBS-View'),
    url(r'^criminal-record/check-answers/', views.dbs_check_summary, name='DBS-Check-Summary-View'),
    url(r'^early-years/$', views.eyfs_guidance, name='EYFS-Guidance-View'),
    url(r'^early-years/details', views.eyfs_details, name='EYFS-Details-View'),
    url(r'^early-years/certificate', views.eyfs_certificate, name='EYFS-Certificate-View'),
    url(r'^early-years/check-answers/', views.eyfs_summary, name='EYFS-Summary-View'),
    url(r'^health/$', views.health_intro, name='Health-Intro-View'),
    url(r'^health/booklet/', views.health_booklet, name='Health-Booklet-View'),
    url(r'^health/check-answers/', views.health_check_answers, name='Health-Check-Answers-View'),
    url(r'^references/$', views.references_intro, name='References-Intro-View'),
    url(r'^references/first-reference/', views.references_first_reference, name='References-First-Reference-View'),
    url(r'^references/first-reference-address/', views.references_first_reference_address,
        name='References-First-Reference-Address-View'),
    url(r'^references/select-first-reference-address/', views.references_first_reference_address_select,
        name='References-Select-First-Reference-Address-View'),
    url(r'^references/enter-first-reference-address/', views.references_first_reference_address_manual,
        name='References-Enter-First-Reference-Address-View'),
    url(r'^references/first-reference-contact-details/', views.references_first_reference_contact_details,
        name='References-First-Reference-Contact-Details-View'),
    url(r'^references/second-reference/', views.references_second_reference, name='References-Second-Reference-View'),
    url(r'^references/second-reference-address/', views.references_second_reference_address,
        name='References-Second-Reference-Address-View'),
    url(r'^references/select-second-reference-address/', views.references_second_reference_address_select,
        name='References-Select-Second-Reference-Address-View'),
    url(r'^references/enter-second-reference-address/', views.references_second_reference_address_manual,
        name='References-Enter-Second-Reference-Address-View'),
    url(r'^references/second-reference-contact-details/', views.references_second_reference_contact_details,
        name='References-Second-Reference-Contact-Details-View'),
    url(r'^references/check-answers/', views.references_summary, name='References-Summary-View'),
    url(r'^other-people/guidance/', views.other_people_guidance, name='Other-People-Guidance-View'),
    url(r'^other-people/adult-question/', views.other_people_adult_question, name='Other-People-Adult-Question-View'),
    url(r'^other-people/adult-details/', views.other_people_adult_details, name='Other-People-Adult-Details-View'),
    url(r'^other-people/adult-dbs/', views.other_people_adult_dbs, name='Other-People-Adult-DBS-View'),
    url(r'^other-people/adult-permission/', views.other_people_adult_permission,
        name='Other-People-Adult-Permission-View'),
    url(r'^other-people/children-question/', views.other_people_children_question,
        name='Other-People-Children-Question-View'),
    url(r'^other-people/children-details/', views.other_people_children_details,
        name='Other-People-Children-Details-View'),
    url(r'^other-people/approaching-16/', views.other_people_approaching_16, name='Other-People-Approaching-16-View'),
    url(r'^other-people/summary/', views.other_people_summary, name='Other-People-Summary-View'),
    url(r'^declaration/', views.declaration_intro, name='Declaration-Intro-View'),
    url(r'^your-declaration/', views.declaration_declaration, name='Declaration-Declaration-View'),
    url(r'^check-answers/', views.declaration_summary, name='Declaration-Summary-View'),
    url(r'^payment/$', views.payment_selection, name='Payment-View'),
    url(r'^payment/details/', views.card_payment_details, name='Payment-Details-View'),
    url(r'^paypal-payment-completion/', views.paypal_payment_completion, name='Paypal-Payment-Completion-View'),
    url(r'^application-saved/', views.application_saved, name='Application-Saved-View'),
    url(r'^validate/(?P<id>[\w-]+)/$', magic_link.validate_magic_link, name='Validate-Email'),
    url(r'^security-code/', magic_link.sms_verification, name='Security-Code'),
    url(r'^email-sent/', TemplateView.as_view(template_name='email-sent.html'), name='Email-Sent-Template'),
    url(r'^start/', views.start_page, name='Start-Page-View'),
    url(r'^confirmation/', views.payment_confirmation, name='Payment-Confirmation'),
    url(r'^next-steps/documents/', views.documents_needed, name='Next-Steps-Documents'),
    url(r'^next-steps/home/', views.home_ready, name='Next-Steps-Home'),
    url(r'^next-steps/interview/', views.prepare_for_interview, name='Next-Steps-Interview'),
    url(r'^code-expired/', TemplateView.as_view(template_name='code-expired.html')),
    url(r'^link-used/', TemplateView.as_view(template_name='bad-link.html')),
    url(r'^sign-in/question/(?P<id>[\w-]+)/$', security_question.question, name='Security-QuestionP'),
    url(r'^sign-in/question/$', security_question.question, name='Security-Question'),
    url(r'^djga/', include('google_analytics.urls')),
    url(r'^awaiting-review/', views.awaiting_review, name='Awaiting-Review-View'),
    url(r'^accepted/', views.application_accepted, name='Accepted-View'),
    url(r'^print-application/(?P<page>[-\w]+)/$', views.base_print_handler, name='Print-Handler-View'),
    url(r'^costs/$', views.costs, name='Costs-View'),
    url(r'^cancel-application/guidance/$', views.cancel_app, name='Cancel-Application'),
    url(r'^cancel-application/confirmation/$', views.cancel_app_confirmation, name='Cancel-Application-Confirmation'),
    url(r'^childcare-register/cancel-application/$', views.cr_cancel_app, name='CR-Cancel-Application'),
    url(r'^childcare-register/application-cancelled/$', views.cr_cancel_app_confirmation,
        name='CR-Cancel-Application-Confirmation'),
    url(r'^new-application/$', views.login.NewUserSignInView.as_view(), name='New-Email'),
    url(r'^new-application/email-sent/$', views.login.login_email_link_sent, name='New-Email-Sent'),
    url(r'^sign-in/$', views.login.ExistingUserSignInView.as_view(), name='Existing-Email'),
    url(r'^sign-in/check-email/$', views.login.login_email_link_sent, name='Existing-Email-Sent'),
    url(r'^sign-in/check-email-change/$', views.login.update_email_link_sent, name='Update-Email-Sent'),
    url(r'^sign-in/change-email-resent/$', views.login.update_email_link_resent, name='Update-Email-Resent'),
    url(r'^sign-in/new-application/$', views.login.account_selection, name='Account-Selection'),
    url(r'^service-unavailable/$', utils.service_down, name='Service-Down'),
    url(r'^email-resent/$', views.login.login_email_link_resent, name='Email-Resent'),
    url(r'^code-resent/$', magic_link.resend_code, name='Resend-Code'),
    url(r'^help-advice/$', views.help_and_advice, name='Help-And-Advice-View'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

if settings.URL_PREFIX:
    prefixed_url_pattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_url_pattern.append(pat)
    urlpatterns = prefixed_url_pattern

handler404 = views.error_404
handler500 = views.error_500
