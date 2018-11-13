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
from application.views import security_question, magic_link, feedback, your_children
from application.views.other_people_health_check import health_check_login, dob_auth, current_treatment, local_authorities, guidance, \
    declaration, serious_illness, hospital_admission, summary, thank_you
from application.views import PITH_views

urlpatterns = [
    url(r'^$', views.start_page, name='start-page.html'),
    url(r'^task-list/', views.task_list, name='Task-List-View'),
    url(r'^childcare/type/', views.type_of_childcare_guidance, name='Type-Of-Childcare-Guidance-View'),
    url(r'^childcare/age-groups/', views.type_of_childcare_age_groups, name='Type-Of-Childcare-Age-Groups-View'),
    url(r'^childcare/register/', views.type_of_childcare_register, name='Type-Of-Childcare-Register-View'),
    url(r'^childcare/local-authority/', views.local_authority_links, name='Local-Authority-View'),
    url(r'^childcare/overnight-care/', views.overnight_care, name='Type-Of-Childcare-Overnight-Care-View'),
    url(r'^childcare/check-answers/', views.childcare_type_summary, name='Type-Of-Childcare-Summary-View'),
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
    url(r'^personal-details/childcare-address-details/', views.personal_details_working_in_other_childminder_home,
        name='Personal-Details-Childcare-Address-Details-View'),
    url(r'^personal-details/your-children/', views.personal_details_own_children,
        name='Personal-Details-Your-Own-Children-View'),
    url(r'^personal-details/check-answers/', views.personal_details_summary, name='Personal-Details-Summary-View'),
    url(r'^first-aid/$', views.first_aid_training_guidance, name='First-Aid-Training-Guidance-View'),
    url(r'^first-aid/details/', views.first_aid_training_details, name='First-Aid-Training-Details-View'),
    url(r'^first-aid/certificate/', views.first_aid_training_declaration, name='First-Aid-Training-Declaration-View'),
    url(r'^first-aid/renew/', views.first_aid_training_renew, name='First-Aid-Training-Renew-View'),
    url(r'^first-aid/update/', views.first_aid_training_training, name='First-Aid-Training-Training-View'),
    url(r'^first-aid/check-answers/', views.first_aid_training_summary, name='First-Aid-Training-Summary-View'),

    # ======================= #
    # Childcare Training urls #
    # ======================= #

    url(r'^childcare-training/$', views.ChildcareTrainingGuidanceView.as_view(),
        name='Childcare-Training-Guidance-View'),
    url(r'^childcare-training/details/', views.ChildcareTrainingDetailsView.as_view(),
        name='Childcare-Training-Details-View'),
    url(r'^childcare-training/type/', views.TypeOfChildcareTrainingView.as_view(),
        name='Type-Of-Childcare-Training-View'),
    url(r'^childcare-training-course/', views.ChildcareTrainingCourseRequiredView.as_view(),
        name='Childcare-Training-Course-Required-View'),
    url(r'^childcare-training-certificate/', views.ChildcareTrainingCertificateView.as_view(),
        name='Childcare-Training-Certificate-View'),
    url(r'^childcare-training/check-answers/', views.ChildcareTrainingSummaryView.as_view(),
        name='Childcare-Training-Summary-View'),

    # =========================== #
    # Criminal Record Checks urls #
    # =========================== #

    url(r'^criminal-record/$', views.DBSGuidanceView.as_view(), name='DBS-Guidance-View'),
    url(r'^criminal-record/type/$', views.DBSTypeView.as_view(), name='DBS-Type-View'),
    url(r'^criminal-record/lived-abroad/$', views.DBSLivedAbroadView.as_view(), name='DBS-Lived-Abroad-View'),
    url(r'^criminal-record/abroad/$', views.DBSGoodConductView.as_view(), name='DBS-Good-Conduct-View'),
    url(r'^criminal-record/email-certificates/$', views.DBSEmailCertificatesView.as_view(),
        name='DBS-Email-Certificates-View'),
    url(r'^criminal-record/military-base-abroad/$', views.DBSMilitaryView.as_view(), name='DBS-Military-View'),
    url(r'^criminal-record/MOD-checks/$', views.DBSMinistryOfDefenceView.as_view(),
        name='DBS-Ministry-Of-Defence-View'),
    url(r'^criminal-record/UK/$', views.DBSGuidanceSecondView.as_view(), name='DBS-Guidance-Second-View'),
    url(r'^criminal-record/your-details/$', views.DBSCheckCapitaView.as_view(), name='DBS-Check-Capita-View'),
    url(r'^criminal-record/DBS-details/$', views.DBSCheckNoCapitaView.as_view(), name='DBS-Check-No-Capita-View'),
    url(r'^criminal-record/update/$', views.DBSUpdateView.as_view(), name='DBS-Update-View'),
    url(r'^criminal-record/Ofsted-check/$', views.DBSGetView.as_view(), name='DBS-Get-View'),
    url(r'^criminal-record/post-certificate/', views.DBSPostView.as_view(), name='DBS-Post-View'),
    url(r'^criminal-record/check-answers/', views.DBSSummaryView.as_view(), name='DBS-Summary-View'),

    # ======================= #
    # People in the Home urls #
    # ======================= #

    url(r'^people/$', PITH_views.PITHGuidanceView.as_view(), name='PITH-Guidance-View'),

    # Adults
    url(r'^people/adults/$', PITH_views.PITHAdultCheckView.as_view(), name='PITH-Adult-Check-View'),
    url(r'^people/adults-details/$', views.other_people_adult_details, name='PITH-Adult-Details-View'),
    url(r'^people/adults-lived-abroad/$', PITH_views.PITHLivedAbroadView.as_view(), name='PITH-Lived-Abroad-View'),
    url(r'^people/adults-checks-abroad/$', PITH_views.PITHAbroadCriminalView.as_view(), name='PITH-Abroad-Criminal-View'),
    url(r'^people/adults-military-bases/$', PITH_views.PITHMilitaryView.as_view(), name='PITH-Military-View'),
    url(r'^people/adults-MoD-checks/$', PITH_views.PITHMinistryView.as_view(), name='PITH-Ministry-View'),
    url(r'^people/adult-dbs-checks/$', PITH_views.PITHDBSCheckView.as_view(), name='PITH-DBS-Check-View'),
    url(r'^people/post-certificate/$', PITH_views.PITHPostView.as_view(), name='PITH-Post-View'),
    url(r'^people/adults-apply/$', PITH_views.PITHApplyView.as_view(), name='PITH-Apply-View'),

    # Children
    url(r'^people/children/$', PITH_views.PITHChildrenCheckView.as_view(), name='PITH-Children-Check-View'),
    url(r'^people/children-details/$', PITH_views.PITHChildrenDetailsView.as_view(),
        name='PITH-Children-Details-View'),
    url(r'^people/children-turning-16/$', views.other_people_approaching_16, name='PITH-Approaching-16-View'),
    url(r'^people/your-children/$', PITH_views.PITHOwnChildrenCheckView.as_view(), name='PITH-Own-Children-Check-View'),
    url(r'^people/your-children-details/$', PITH_views.PITHOwnChildrenDetailsView.as_view(), name='PITH-Own-Children-Details-View'),
    url(r'^people/your-children-address/$', PITH_views.PITHOwnChildrenPostcodeView,
        name='PITH-Own-Children-Postcode-View'),
    url(r'^people/select-children-address/$', PITH_views.PITHOwnChildrenSelectView,
        name='PITH-Own-Children-Select-View'),
    url(r'^people/enter-children-address/$', PITH_views.PITHOwnChildrenManualView,
        name='PITH-Own-Children-Manual-View'),
    url(r'^people/check-answers/$', views.other_people_summary, name='PITH-Summary-View'),

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
    url(r'^registration-rules/', TemplateView.as_view(template_name='registration-rules.html'),
        name='Registration-Rules'),
    url(r'^health-check/(?P<id>[\w-]+)/$', health_check_login.validate_magic_link, name='Health-Check-Authentication'),
    url(r'^health-check/birth-date', dob_auth.DobAuthView.as_view(), name='Health-Check-Dob'),
    url(r'^health-check/adults', guidance.Guidance.as_view(), name='Health-Check-Guidance'),
    url(r'^health-check/current-treatment', current_treatment.CurrentTreatment.as_view(), name='Health-Check-Current'),
    url(r'^health-check/serious-illness$', serious_illness.SeriousIllnessStartView.as_view(),
        name='Health-Check-Serious-Start'),
    url(r'^health-check/local-authorities$', local_authorities.LocalAuthorities.as_view(),
        name='Health-Check-Local-Authorities'),
    url(r'^health-check/more-serious-illness', serious_illness.MoreSeriousIllnessesView.as_view(),
        name='Health-Check-Serious-More'),
    url(r'^health-check/serious-illness/edit', serious_illness.SeriousIllnessEditView.as_view(),
        name='Health-Check-Serious-Edit'),
    url(r'^health-check/serious-illness-details$', serious_illness.SeriousIllnessView.as_view(),
        name='Health-Check-Serious'),
    url(r'^health-check/hospital$', hospital_admission.HospitalAdmissionStartView.as_view(),
        name='Health-Check-Hospital-Start'),
    url(r'^health-check/more-hospital', hospital_admission.MoreHospitalAdmissionsView.as_view(),
        name='Health-Check-Hospital-More'),
    url(r'^health-check/hospital/edit', hospital_admission.HospitalAdmissionEditView.as_view(),
        name='Health-Check-Hospital-Edit'),
    url(r'^health-check/hospital-details', hospital_admission.HospitalAdmissionView.as_view(),
        name='Health-Check-Hospital'),
    url(r'^health-check/check-answers', summary.Summary.as_view(), name='Health-Check-Summary'),
    url(r'^health-check/declaration', declaration.Declaration.as_view(), name='Health-Check-Declaration'),
    url(r'^health-check/thank-you', thank_you.ThankYou.as_view(), name='Health-Check-Thank-You'),
    url(r'^people/contacted/', views.other_people_email_confirmation, name='Other-People-Email-Confirmation-View'),
    url(r'^people/resend-email/', views.other_people_resend_email, name='Other-People-Resend-Email-View'),
    url(r'^people/email-resent/', views.other_people_resend_confirmation, name='Other-People-Resend-Confirmation-View'),
    url(r'^declaration/', views.declaration_intro, name='Declaration-Intro-View'),
    url(r'^your-declaration/', views.declaration_declaration, name='Declaration-Declaration-View'),
    url(r'^publishing-your-details/', views.publishing_your_details, name='Publishing-Your-Details-View'),
    url(r'^check-answers/', views.declaration_summary, name='Declaration-Summary-View'),
    url(r'^payment/details/', views.card_payment_details, name='Payment-Details-View'),
    url(r'^application-saved/', views.application_saved, name='Application-Saved-View'),
    url(r'^validate/(?P<id>[\w-]+)/$', magic_link.validate_magic_link, name='Validate-Email'),
    url(r'^security-code/', magic_link.SMSValidationView.as_view(), name='Security-Code'),
    url(r'^email-sent/', TemplateView.as_view(template_name='email-sent.html'), name='Email-Sent-Template'),
    url(r'^start/', views.start_page, name='Start-Page-View'),
    url(r'^confirmation/', views.payment_confirmation, name='Payment-Confirmation'),
    url(r'^documents-needed/', views.documents_needed, name='Next-Steps-Documents'),
    url(r'^home-ready/', views.home_ready, name='Next-Steps-Home'),
    url(r'^prepare-interview/', views.prepare_for_interview, name='Next-Steps-Interview'),
    url(r'^link-used/', TemplateView.as_view(template_name='bad-link.html')),
    url(r'^link-expired/', TemplateView.as_view(template_name='link-expired.html')),
    url(r'^sign-in/question/(?P<id>[\w-]+)/$', security_question.question, name='Security-Question'),
    url(r'^sign-in/question/$', security_question.question, name='Security-Question'),
    url(r'^djga/', include('google_analytics.urls')),
    url(r'^awaiting-review/', views.awaiting_review, name='Awaiting-Review-View'),
    url(r'^accepted/', views.application_accepted, name='Accepted-View'),
    url(r'^print-application/(?P<page>[-\w]+)/$', views.base_print_handler, name='Print-Handler-View'),
    url(r'^cancel-application/guidance/$', views.cancel_app, name='Cancel-Application'),
    url(r'^cancel-application/confirmation/$', views.cancel_app_confirmation, name='Cancel-Application-Confirmation'),
    url(r'^childcare-register/cancel-application/$', views.cr_cancel_app, name='CR-Cancel-Application'),
    url(r'^application-cancelled/$', views.cr_cancel_app_confirmation,
        name='CR-Cancel-Application-Confirmation'),
    url(r'^new-application/$', views.login.NewUserSignInView.as_view(), name='New-Email'),
    url(r'^new-application/email-sent/$', views.login.login_email_link_sent, name='New-Email-Sent'),
    url(r'^sign-in/$', views.login.ExistingUserSignInView.as_view(), name='Existing-Email'),
    url(r'^sign-in/check-email/$', views.login.login_email_link_sent, name='Existing-Email-Sent'),
    url(r'^sign-in/check-email-change/$', views.login.update_email_link_sent, name='Update-Email-Sent'),
    url(r'^sign-in/change-email-resent/$', views.login.update_email_link_resent, name='Update-Email-Resent'),
    url(r'^sign-in/your-location/$', views.login.your_location, name='Your-Location'),
    url(r'^sign-in/new-application/$', views.login.account_selection, name='Account-Selection'),
    url(r'^service-unavailable/$', utils.service_down, name='Service-Down'),
    url(r'^email-resent/$', views.login.login_email_link_resent, name='Email-Resent'),
    url(r'^new-code/$', magic_link.ResendSMSCodeView.as_view(), name='Resend-Code'),
    url(r'^help-contact/$', views.help_and_contact, name='Help-And-Contact-View'),
    url(r'^childcare-location/cancel-application', views.cancel_application.cl_cancel_app, name='Service-Unavailable'),
    url(r'^feedback/', feedback.feedback, name='Feedback'),
    url(r'^feedback-submitted/', feedback.feedback_confirmation, name='Feedback-Confirmation'),

    # =========================== #
    # Your children urls #
    # =========================== #
    url(r'^your-children/$', your_children.your_children_guidance, name='Your-Children-Guidance-View'),
    url(r'^your-children-details/$', your_children.your_children_details, name='Your-Children-Details-View'),
    url(r'^your-children/living-with-you/$', your_children.your_children_living_with_you, name='Your-Children-Living-With-You-View'),
    url(r'^your-children/addresses/$', your_children.your_children_address_capture, name='Your-Children-Address-View'),
    url(r'^your-children/address-details/$', your_children.your_children_address_selection, name='Your-Children-Address-Select-View'),
    url(r'^your-children/enter-address/$', your_children.your_children_address_manual, name='Your-Children-Address-Manual-View'),
    url(r'^your-children/check-answers/$', your_children.your_children_summary, name='Your-Children-Summary-View'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

if hasattr(settings, 'URL_PREFIX'):
    prefixed_url_pattern = []
    for pat in urlpatterns:
        pat.regex = re.compile(r"^%s/%s" % (settings.URL_PREFIX[1:], pat.regex.pattern[1:]))
        prefixed_url_pattern.append(pat)
    urlpatterns = prefixed_url_pattern

handler404 = views.error_404
handler500 = views.error_500
