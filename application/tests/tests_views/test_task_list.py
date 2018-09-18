from .view_parent import *
from uuid import uuid4
from django.utils import timezone

from application.views.task_list import show_hide_tasks


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

    def test_hide_your_children_and_people_in_your_home_task(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            your_children_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='IN_PROGRESS',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            own_children=False,
            working_in_other_childminder_home=True
        )
        context = {
            'tasks': [
                {
                    'name': 'your_children',
                    'hidden': False
                },
                {
                    'name': 'other_people',
                    'hidden': False
                }
            ]
        }

        context = show_hide_tasks(context, application)
        self.assertEqual(True, context['tasks'][0]['hidden'])
        self.assertEqual(True, context['tasks'][1]['hidden'])

    def test_show_your_children_and_people_in_your_home_task(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            your_children_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='IN_PROGRESS',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            own_children=True,
            working_in_other_childminder_home=False
        )
        context = {
            'tasks': [
                {
                    'name': 'your_children',
                    'hidden': True
                },
                {
                    'name': 'other_people',
                    'hidden': True
                }
            ]
        }

        context = show_hide_tasks(context, application)
        self.assertEqual(False, context['tasks'][0]['hidden'])
        self.assertEqual(False, context['tasks'][1]['hidden'])

    def test_show_your_children_and_hide_people_in_your_home_task(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            your_children_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='IN_PROGRESS',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            own_children=True,
            working_in_other_childminder_home=True
        )
        context = {
            'tasks': [
                {
                    'name': 'your_children',
                    'hidden': True
                },
                {
                    'name': 'other_people',
                    'hidden': False
                }
            ]
        }

        context = show_hide_tasks(context, application)
        self.assertEqual(False, context['tasks'][0]['hidden'])
        self.assertEqual(True, context['tasks'][1]['hidden'])

    def test_hide_your_children_and_show_people_in_your_home_task(self):
        test_application_id = 'f8c42666-1367-4878-92e2-1cee6ebcb48c'

        application = models.Application.objects.create(
            application_id=(UUID(test_application_id)),
            application_type='CHILDMINDER',
            application_status='DRAFTING',
            cygnum_urn='',
            login_details_status='COMPLETED',
            personal_details_status='COMPLETED',
            childcare_type_status='COMPLETED',
            first_aid_training_status='COMPLETED',
            childcare_training_status='COMPLETED',
            your_children_status='COMPLETED',
            criminal_record_check_status='COMPLETED',
            health_status='COMPLETED',
            references_status='COMPLETED',
            people_in_home_status='COMPLETED',
            declarations_status='IN_PROGRESS',
            date_created=datetime.datetime.today(),
            date_updated=datetime.datetime.today(),
            date_accepted=None,
            own_children=False,
            working_in_other_childminder_home=False
        )
        context = {
            'tasks': [
                {
                    'name': 'your_children',
                    'hidden': False
                },
                {
                    'name': 'other_people',
                    'hidden': True
                }
            ]
        }

        context = show_hide_tasks(context, application)
        self.assertEqual(True, context['tasks'][0]['hidden'])
        self.assertEqual(False, context['tasks'][1]['hidden'])
