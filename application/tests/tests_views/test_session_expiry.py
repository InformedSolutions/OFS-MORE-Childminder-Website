from .view_parent import *

from application.views import SessionExpiredView


class StartPageTest(ViewsTest):

    def test_can_render_session_expiry_page(self):
        found = resolve(reverse('Session-Expired'))
        self.assertEqual(found.func.view_class, SessionExpiredView)
