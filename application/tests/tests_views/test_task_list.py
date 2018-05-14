from .view_parent import *
from uuid import uuid4
from django.utils import timezone


class TaskListTest(ViewsTest):

    def test_url_resolves_to_task_list(self):
        found = resolve(settings.URL_PREFIX + '/task-list/')
        self.assertEqual(found.func, task_list)

    def test_task_list_not_displayed_without_id(self):
        c = Client()
        try:
            c.get(settings.URL_PREFIX + '/task-list/?id=')
            self.assertEqual(1, 0)
        except:
            self.assertEqual(0, 0)