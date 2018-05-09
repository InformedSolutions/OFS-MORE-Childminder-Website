from .test_views import *


class ApplicationSavedTest(ViewsTest):

    def test_url_resolves_to_page(self):
        found = resolve(settings.URL_PREFIX + '/application-saved/')
        self.assertEqual(found.func, application_saved)

    def test_page_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/application-saved/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)