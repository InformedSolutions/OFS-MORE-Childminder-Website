"""
Selenium test cases for the Childminder service
"""

import os
import random
from datetime import datetime

from django.test import LiveServerTestCase, override_settings, tag
from selenium import webdriver

from .selenium_task_executor import SeleniumTaskExecutor

from faker import Faker

# Configure faker to use english locale
faker = Faker('en_GB')

selenium_driver = None
selenium_task_executor = None


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class ApplyAsAChildminder(LiveServerTestCase):
    port = 8000
    host = '0.0.0.0'
    current_year = datetime.now().year

    def setUp(self):
        global selenium_task_executor
        global selenium_driver

        base_url = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS')

        if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
            # If running on a windows host, make sure to drop the
            # geckodriver.exe into your Python/Scripts installation folder
            selenium_driver = webdriver.Firefox()
        else:
            # If not using local driver, default requests to a selenium grid server
            selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
            )

        selenium_driver.maximize_window()
        selenium_driver.implicitly_wait(5)

        self.verification_errors = []
        self.accept_next_alert = True

        selenium_task_executor = SeleniumTaskExecutor(selenium_driver, base_url)

        super(ApplyAsAChildminder, self).setUp()

    # Test wrappers are used here to allow ordering of tests. Tests are also split to produce more
    # meaningful test report outputs in the event of a failure.
    def test_directed_to_local_authority_if_not_eyfs_register(self):
        self.assert_directed_to_local_authority_if_not_eyfs_register()

    def assert_directed_to_local_authority_if_not_eyfs_register(self):
        """
        Tests that a user is directed toward guidance advising them to contact their local authority if
        the ages of children they are minding does not
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

            # Guidance page
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

            # Choose 5 to 7 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

            # Confirm selection
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

            self.assertEqual("Childcare Register",
                             selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/form/div/h1").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_shown_eyfs_only_guidance(self):
        self.assert_shown_eyfs_only_guidance()

    def assert_shown_eyfs_only_guidance(self):
        """
        Test to make sure guidance page shown when only minding children up to the age of five gets shown
        if only the "0 to 5 year olds' option is selected on the Age of Children page
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

            # Guidance page
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

            # Choose 0-5 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

            # Confirm selection
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

            self.assertEqual("Early Years Register", selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/form/div/h1").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_shown_eyfs_compulsory_part_guidance(self):
        self.assert_shown_eyfs_compulsory_part_guidance()

    def assert_shown_eyfs_compulsory_part_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children both up
        to the age of five and between 5 and 7
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

            # Guidance page
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

            # Choose 0-5 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

            # Choose 5-7 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

            # Confirm selection
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

            self.assertEqual("Early Years and Childcare Register (compulsory part)", selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/form/div/h1").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_shown_both_parts_guidance(self):
        self.assert_shown_both_parts_guidance()

    def assert_shown_both_parts_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children of all ages
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

            # Guidance page
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

            # Choose 0-5 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

            # Choose 5-7 year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

            # Choose 8+ year olds option
            selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_2").click()

            # Confirm selection
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

            self.assertEqual("Early Years and Childcare Register (both parts)", selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/form/div/h1").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_complete_personal_details_task_when_location_of_care_is_same_as_home_address(self):
        self.assert_can_complete_personal_details_task_when_location_of_care_is_same_as_home_address()

    def assert_can_complete_personal_details_task_when_location_of_care_is_same_as_home_address(self):
        """
        Test to make sure a user can choose Yes to the question Is this where you will be looking after the children?
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            # Below DOB means they are an adult so do not fire validation triggers
            selenium_task_executor.complete_personal_details(
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
                True
            )

            # Check task status marked as Done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='personal_details']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_complete_dbs_task_without_cautions_or_convictions(self):
        self.assert_can_complete_dbs_task_without_cautions_or_convictions()

    def assert_can_complete_dbs_task_without_cautions_or_convictions(self):
        """
        Tests the Criminal record (DBS) check task can be completed when stating that you do not have cautions
        or convictions
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
            selenium_task_executor.complete_dbs_task(test_dbs, False)
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='dbs']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_complete_people_in_your_home_task_without_other_adults_but_with_other_children(self):
        self.assert_can_complete_people_in_your_home_task_without_other_adults_but_with_other_children()

    def assert_can_complete_people_in_your_home_task_without_other_adults_but_with_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering No to the question
        'Does anyone aged 16 or over live or work in your home?'
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            selenium_task_executor.complete_people_in_your_home_task(
                False,
                None, None, None,
                None, None, None, None, None,
                True, faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 15, self.current_year - 1),
                'Child'
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_complete_people_in_your_home_task_with_other_adults_but_without_other_children(self):
        self.assert_can_complete_people_in_your_home_task_with_other_adults_but_without_other_children()

    def assert_can_complete_people_in_your_home_task_with_other_adults_but_without_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            selenium_task_executor.complete_people_in_your_home_task(
                True,
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
                False, None, None, None,
                None, None, None,
                None
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_apply_as_a_childminder_full_question_set(self):
        self.assert_can_apply_as_a_childminder_full_question_set()

    def assert_can_apply_as_a_childminder_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        global selenium_task_executor

        try:
            self.complete_full_question_set()

            selenium_task_executor.complete_review()
            selenium_task_executor.complete_declaration()

            # Card number must be 5454... due to this being a Worldpay API test value
            test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
            selenium_task_executor.complete_payment(True, 'Visa', '5454545454545454', str(random.randint(1, 12)),
                                                    str(random.randint(self.current_year + 1, self.current_year + 5)),
                                                    faker.name(),
                                                    test_cvc)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_access_costs(self):
        self.assert_can_access_costs()

    def assert_can_access_costs(self):
        """
        Tests that the costs page can be reached
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()
            selenium_task_executor.get_driver().find_element_by_link_text("more about costs").click()
            self.assertEqual("Costs of becoming a childminder", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_begin_returning_user_sign_in_process(self):
        self.assert_can_begin_returning_user_sign_in_process()

    def assert_can_begin_returning_user_sign_in_process(self):
        """
        Tests that the sign in page for returning users can be reached
        """
        global selenium_task_executor

        try:
            test_email = self.create_standard_eyfs_application()
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Start now']").click()
            selenium_task_executor.get_driver().find_element_by_link_text("Sign in").click()
            selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(test_email)
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
            self.assertEqual("Email sent", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_apply_as_a_childminder_using_full_question_set(self):
        self.assert_can_apply_as_a_childminder_using_full_question_set()

    def assert_can_apply_as_a_childminder_using_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            # Below DOB means they are an adult so do not fire validation triggers
            selenium_task_executor.complete_personal_details(
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
                False
            )

            # Check task status marked as Done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='personal_details']/td/a/strong").text)

            # When completing first aid training task ensure that certification is within last 3 years
            selenium_task_executor.complete_first_aid_training(
                faker.company(),
                random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1),
                False
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='first_aid']/td/a/strong").text)

            selenium_task_executor.complete_health_declaration_task()

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='health']/td/a/strong").text)

            test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
            selenium_task_executor.complete_dbs_task(test_dbs, False)

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='dbs']/td/a/strong").text)

            selenium_task_executor.complete_people_in_your_home_task(
                True,
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
                True, faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 15, self.current_year - 1),
                'Child'
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/strong").text)

            selenium_task_executor.complete_references_task(
                faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
                selenium_task_executor.generate_random_mobile_number(), faker.email(),
                faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
                selenium_task_executor.generate_random_mobile_number(), faker.email()
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='references']/td/a/strong").text)

            selenium_task_executor.complete_review()
            selenium_task_executor.complete_declaration()

            # Card number must be 5454... due to this being a Worldpay API test value
            test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
            selenium_task_executor.complete_payment(True, 'Visa', '5454545454545454', str(random.randint(1, 12)),
                                                    str(random.randint(self.current_year + 1, self.current_year + 5)),
                                                    faker.name(),
                                                    test_cvc)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_apply_as_a_childminder_no_overnight_care(self):
        self.assert_can_apply_as_a_childminder_no_overnight_care()

    def assert_can_apply_as_a_childminder_no_overnight_care(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
            selenium_task_executor.complete_type_of_childcare(True, False, False, False)

            # Check task status set to done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='account_details']/td/a/strong").text)
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='children']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_first_aid_out_of_date_guidance_shown(self):
        self.assert_first_aid_out_of_date_guidance_shown()

    def assert_first_aid_out_of_date_guidance_shown(self):
        """
        Test to check that if a first aid training certificate is expired a user is informed they need to update their traininig
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            # Below DOB means they are an adult so do not fire validation triggers
            selenium_task_executor.complete_personal_details(
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
                False
            )

            # Check task status marked as Done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='personal_details']/td/a/strong").text)

            # When completing first aid training task set expired certification year
            selenium_task_executor.complete_first_aid_training(
                faker.company(),
                random.randint(1, 28), random.randint(1, 12), 2012,
                True
            )

            self.assertEqual("Update your first aid training", selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/form/div/h1").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_cannot_create_multiple_applications_using_same_email(self):
        self.assert_cannot_create_multiple_applications_using_same_email()

    def assert_cannot_create_multiple_applications_using_same_email(self):
        """
        Test to ensure a user cannot register twice with the same email address
        """
        global selenium_task_executor

        try:
            test_email = self.create_standard_eyfs_application()
            selenium_task_executor.navigate_to_base_url()
            selenium_task_executor.register_email_address(test_email)

            self.assertEqual("Email sent", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_cancel_application(self):
        self.assert_can_cancel_application()

    def assert_can_cancel_application(self):
        """
        Test to assert a new application can be cancelled
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            selenium_task_executor.get_driver().find_element_by_link_text("Cancel application").click()
            selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Cancel Application']").click()
            self.assertEqual("Application Cancelled", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_can_save_and_exit(self):
        self.assert_can_save_and_exit()

    def assert_can_save_and_exit(self):
        """
        Test to assert a user can save and exit an application
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            selenium_task_executor.get_driver().find_element_by_link_text("Save and exit").click()
            self.assertEqual("Application saved", selenium_task_executor.get_driver().title)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def test_task_summaries_display_on_completion(self):
        self.assert_task_summaries_display_on_completion()

    def assert_task_summaries_display_on_completion(self):
        """
        Tests that once a task is marked as Done, clicking that task from the task list shows the summary page
        """
        global selenium_task_executor

        self.complete_full_question_set()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='children']/td/a/span").click()
        self.assertEqual("Check your answers: Type of childcare",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='personal_details']/td/a/span").click()
        self.assertEqual("Check your answers: your personal details",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='first_aid']/td/a/span").click()
        self.assertEqual("Check your answers: first aid training",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='health']/td/a/span").click()
        self.assertEqual("Check your answers: your health",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='dbs']/td/a/span").click()
        self.assertEqual("Check your answers: criminal record (DBS) check",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.assertEqual("Check your answers: people in your home",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='references']/td/a/span").click()
        self.assertEqual("Check your answers: references",
                         selenium_task_executor.get_driver().find_element_by_xpath("//main[@id='content']/h1").text)
        selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='review']/td/a/span").click()

    def create_standard_eyfs_application(self):
        """
        Helper method for starting a new application
        :return: email address used to register the application
        """
        global selenium_task_executor

        try:
            selenium_task_executor.navigate_to_base_url()

            test_email = faker.email()
            test_phone_number = selenium_task_executor.generate_random_mobile_number()
            test_alt_phone_number = selenium_task_executor.generate_random_mobile_number()

            selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
            selenium_task_executor.complete_type_of_childcare(True, False, False, True)

            # Check task status set to done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='account_details']/td/a/strong").text)
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='children']/td/a/strong").text)

            return test_email
        except Exception as e:
            self.capture_screenshot()
            raise e

    def complete_full_question_set(self):
        """
        Helper method for completing all questions in an application
        """
        global selenium_task_executor

        try:
            self.create_standard_eyfs_application()

            # Below DOB means they are an adult so do not fire validation triggers
            selenium_task_executor.complete_personal_details(
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
                False
            )

            # Check task status marked as Done
            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='personal_details']/td/a/strong").text)

            # When completing first aid training task ensure that certification is within last 3 years
            selenium_task_executor.complete_first_aid_training(
                faker.company(),
                random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1),
                False
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='first_aid']/td/a/strong").text)

            selenium_task_executor.complete_health_declaration_task()

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='health']/td/a/strong").text)

            test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
            selenium_task_executor.complete_dbs_task(test_dbs, True)

            self.assertEqual("Done",
                             selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='dbs']/td/a/strong").text)

            selenium_task_executor.complete_people_in_your_home_task(
                True,
                faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
                True, faker.first_name(), faker.first_name(), faker.last_name_female(),
                random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 15, self.current_year - 1),
                'Child'
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='other_people']/td/a/strong").text)

            selenium_task_executor.complete_references_task(
                faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
                selenium_task_executor.generate_random_mobile_number(), faker.email(),
                faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
                selenium_task_executor.generate_random_mobile_number(), faker.email()
            )

            self.assertEqual("Done", selenium_task_executor.get_driver().find_element_by_xpath(
                "//tr[@id='references']/td/a/strong").text)
        except Exception as e:
            self.capture_screenshot()
            raise e

    def capture_screenshot(self):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        scr = selenium_driver.find_element_by_tag_name('html')
        scr.screenshot('selenium/screenshot-%s-%s.png' % (self.__class__.__name__, now))

    def tearDown(self):
        global selenium_driver
        selenium_driver.quit()
        super(ApplyAsAChildminder, self).tearDown()
        self.assertEqual([], self.verification_errors)

