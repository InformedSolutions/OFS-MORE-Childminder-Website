from django.test import TestCase, tag
from django.conf import settings
from django.http import HttpResponseRedirect

from application import models
from application.login import redirect_by_status


@tag('unit')
class TestLoginRedirectHelper(TestCase):

    def test_drafting_application_status_redirects_to_task_list(self):
        application = models.Application.objects.create()
        application.application_status = 'DRAFTING'
        redirect = redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/childcare/type/"
        self.assertTrue(isinstance(redirect, HttpResponseRedirect))
        self.assertTrue(target_path in redirect.url)

    def test_submitted_status_redirects_to_awaiting_review(self):
        application = models.Application.objects.create()
        application.application_status = 'SUBMITTED'
        redirect = redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/awaiting-review"
        self.assertTrue(isinstance(redirect, HttpResponseRedirect))
        self.assertTrue(target_path in redirect.url)

    def test_arc_review_status_redirects_to_awaiting_review(self):
        application = models.Application.objects.create()
        application.application_status = 'ARC_REVIEW'
        redirect = redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/awaiting-review"
        self.assertTrue(isinstance(redirect, HttpResponseRedirect))
        self.assertTrue(target_path in redirect.url)

    def test_further_information_status_redirects_to_task_list(self):
        application = models.Application.objects.create()
        application.application_status = 'FURTHER_INFORMATION'
        redirect = redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/task-list"
        self.assertTrue(isinstance(redirect, HttpResponseRedirect))
        self.assertTrue(target_path in redirect.url)

    def test_accepted_status_redirects_to_task_list(self):
        application = models.Application.objects.create()
        application.application_status = 'ACCEPTED'
        redirect = redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/accepted"
        self.assertTrue(isinstance(redirect, HttpResponseRedirect))
        self.assertTrue(target_path in redirect.url)