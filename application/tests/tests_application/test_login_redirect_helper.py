"""
OFS-MORE-CCN3: Apply to be a Childminder Beta
-- test_login_redirect_helper.py --

@author: Informed Solutions
"""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.test import TestCase

from ... import login_redirect_helper
from ...models import Application


class TestLoginRedirectHelper(TestCase):

    def test_drafting_application_status_redirects_to_task_list(self):
        application = Application.objects.create()
        application.application_status = 'DRAFTING'
        redirect = login_redirect_helper.redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/childcare/guidance/"
        assert (isinstance(redirect, HttpResponseRedirect))
        print(target_path)
        print(redirect.url)
        assert(target_path in redirect.url)

    def test_submitted_status_redirects_to_awaiting_review(self):
        application = Application.objects.create()
        application.application_status = 'SUBMITTED'
        redirect = login_redirect_helper.redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/awaiting-review"
        assert (isinstance(redirect, HttpResponseRedirect))
        assert(target_path in redirect.url)

    def test_arc_review_status_redirects_to_awaiting_review(self):
        application = Application.objects.create()
        application.application_status = 'ARC_REVIEW'
        redirect = login_redirect_helper.redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/awaiting-review"
        assert (isinstance(redirect, HttpResponseRedirect))
        assert(target_path in redirect.url)

    def test_further_information_status_redirects_to_task_list(self):
        application = Application.objects.create()
        application.application_status = 'FURTHER_INFORMATION'
        redirect = login_redirect_helper.redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/task-list"
        assert (isinstance(redirect, HttpResponseRedirect))
        assert(target_path in redirect.url)

    def test_accepted_status_redirects_to_task_list(self):
        application = Application.objects.create()
        application.application_status = 'ACCEPTED'
        redirect = login_redirect_helper.redirect_by_status(application)
        target_path = settings.URL_PREFIX + "/accepted"
        assert (isinstance(redirect, HttpResponseRedirect))
        assert(target_path in redirect.url)
