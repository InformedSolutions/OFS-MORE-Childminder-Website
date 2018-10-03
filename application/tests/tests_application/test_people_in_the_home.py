from django.test import modify_settings, TestCase


@modify_settings(MIDDLEWARE={
        'remove': [
            'application.middleware.CustomAuthenticationHandler'
        ]
    })
class PeopleInTheHomeTestSuite(TestCase):
    def test_can_render_guidance_page(self):
        pass

    def test_post_request_to_guidance_page_redirects_to_adult_page(self):
        pass
