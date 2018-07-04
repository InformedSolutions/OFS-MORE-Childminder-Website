"""
Selenium test cases for the Childminder service
"""

import os
import random
import time
from datetime import datetime

from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings, tag
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from .selenium_task_executor import SeleniumTaskExecutor

from faker import Faker

# Configure faker to use english locale
faker = Faker('en_GB')
selenium_driver_out = None


def try_except_method(func):
    """
    :param func: assert method to be used in try/except statement
    :return: decorated method to use in try/except statement
    """

    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            capture_screenshot(func)
            raise e

    return func_wrapper


def capture_screenshot(func):
    global selenium_driver_out
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    scr = selenium_driver_out.find_element_by_tag_name('html')
    scr.screenshot('selenium/screenshot-%s-%s.png' % (func.__name__, now))


@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class ApplyAsAChildminder(LiveServerTestCase):
    port = 8000

    if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
        host = '127.0.0.1'
    else:
        host = '0.0.0.0'

    current_year = datetime.now().year

    def setUp(self):
        base_url = os.environ.get('DJANGO_LIVE_TEST_SERVER_ADDRESS')

        if os.environ.get('LOCAL_SELENIUM_DRIVER') == 'True':
            # If running on a windows host, make sure to drop the
            # geckodriver.exe into your Python/Scripts installation folder
            self.launch_local_browser()
        else:
            # If not using local driver, default requests to a selenium grid server
            self.launch_remote_browser()

        self.selenium_driver.implicitly_wait(30)

        self.verification_errors = []
        self.accept_next_alert = True

        self.selenium_task_executor = SeleniumTaskExecutor(self.selenium_driver, base_url)

        global selenium_driver_out
        selenium_driver_out = self.selenium_driver

        super(ApplyAsAChildminder, self).setUp()

    def launch_local_browser(self):
        """
        If the HEADLESS_CHROME value in Environment variables is set to true then it will launch chrome headless
        browser, else it will launch firefox.
        """

        if os.environ.get('HEADLESS_CHROME') == 'True':
            path_to_chromedriver = '/usr/lib/chromium-browser/chromedriver'
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            self.selenium_driver = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
        else:
            self.selenium_driver = webdriver.Firefox()
        self.selenium_driver.maximize_window()

    def launch_remote_browser(self):
        """
        If the HEADLESS_CHROME value in Environment variables is set to true then it will launch chrome headless
        browser, else it will launch firefox.
        """

        if os.environ.get('HEADLESS_CHROME') == 'True':
            self.selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', "headless": 'true', 'browserName': 'chrome', 'version': ''}
            )

        else:
            self.selenium_driver = webdriver.Remote(
                command_executor=os.environ['SELENIUM_HOST'],
                desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
            )
            self.selenium_driver.maximize_window()

    @try_except_method
    def test_directed_to_local_authority_if_not_eyfs_register(self):
        """
        Tests that a user is directed toward guidance advising them to contact their local authority if
        the ages of children they are minding does not
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 5 to 7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Childcare Register"))

        self.assertEqual("Childcare Register",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/form/div/h1").text)

    @try_except_method
    def test_shown_eyfs_only_guidance(self):
        """
        Test to make sure guidance page shown when only minding children up to the age of five gets shown
        if only the "0 to 5 year olds' option is selected on the Age of Children page
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years Register", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_shown_eyfs_compulsory_part_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children both up
        to the age of five and between 5 and 7
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Choose 5-7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years and Childcare Register (compulsory part)",
                         self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_shown_both_parts_guidance(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children of all ages
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Choose 5-7 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_1").click()

        # Choose 8+ year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_2").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.assertEqual("Early Years and Childcare Register (both parts)",
                         self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_must_fill_out_childcare_type_and_personal_details_before_task_list(self):
        """
        Test to ensure the Type of childcare and personal details tasks must be completed before accessing the task list
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)

        self.selenium_task_executor.complete_type_of_childcare(True, True, True, True)

        # Try to get to task list
        self.selenium_task_executor.get_driver().find_element_by_id("proposition-name").click()

        self.assertEqual("Your name",
                         self.selenium_task_executor.get_driver().title)

        # Partially complete Personal details task
        self.selenium_task_executor.get_driver().find_element_by_id("id_first_name").send_keys('Test')
        self.selenium_task_executor.get_driver().find_element_by_id("id_last_name").send_keys('Test')
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Try to get to task list
        self.selenium_task_executor.get_driver().find_element_by_id("proposition-name").click()

        self.assertEqual("Your name",
                         self.selenium_task_executor.get_driver().title)

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Partially complete Personal details task
        self.selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_0").send_keys(20)
        self.selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_1").send_keys(12)
        self.selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_2").send_keys(1995)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Try to get to task list
        self.selenium_task_executor.get_driver().find_element_by_id("proposition-name").click()

        self.assertEqual("Your name",
                         self.selenium_task_executor.get_driver().title)

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_id("id_postcode").send_keys("WA14 4PA")
        self.selenium_task_executor.get_driver().find_element_by_name("postcode-search").click()

        # Select matched result
        self.selenium_task_executor.get_driver().find_element_by_id("id_address").click()
        Select(self.selenium_task_executor.get_driver().find_element_by_id("id_address")).select_by_visible_text(
            "INFORMED SOLUTIONS LTD, THE OLD BANK, OLD MARKET PLACE, ALTRINCHAM, WA14 4PA")

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Try to get to task list
        self.selenium_task_executor.get_driver().find_element_by_id("proposition-name").click()

        self.assertEqual("Your name",
                         self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_return_to_task_list_from_help_and_costs_when_authenticated(self):
        """
        Test to make sure the correct guidance page gets shown when only minding children of all ages
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number,
                                                                test_alt_phone_number)

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Choose 0-5 year olds option
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()

        # Confirm selection
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

        # Overnight care page
        self.selenium_task_executor.get_driver().find_element_by_id("id_overnight_care_0").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Confirmation page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Costs page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='proposition-links']/li[1]/a").click()

        # Go back to task list
        self.selenium_task_executor.get_driver().find_element_by_xpath("//html/body/main/div[2]/a").click()

        self.assertEqual("Register as a childminder",
                         self.selenium_task_executor.get_driver().title)

        # Help page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//*[@id='proposition-links']/li[2]/a").click()

        # Go back to task list
        self.selenium_task_executor.get_driver().find_element_by_link_text("Return to application").click()

        self.assertEqual("Register as a childminder",
                         self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_complete_personal_details_task_when_location_of_care_is_same_as_home_address(self):
        """
        Test to make sure a user can choose Yes to the question Is this where you will be looking after the children?
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

    @try_except_method
    def test_cannot_complete_personal_details_task_when_location_of_care_is_not_same_as_home_address(self):
        """
        Test to make sure a user cannot complete an application if they choose No to the question Is this where you
        will be looking after the children?
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            False
        )

        # Check Can't user service page is shown
        self.assertEqual("Can't use service", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_complete_dbs_task_without_cautions_or_convictions(self):
        """
        Tests the Criminal record (DBS) check task can be completed when stating that you do not have cautions
        or convictions
        """
        self.create_standard_eyfs_application()

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, False)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='dbs']/td/a/strong").text)

    @try_except_method
    def test_can_complete_dbs_number_with_leading_zeros(self):
        """
        Tests the Criminal record (DBS) check task can be completed when the DBS number starts with a '0' and is
        otherwise valid.
        """
        self.create_standard_eyfs_application()

        test_dbs = '000000000012'
        self.selenium_task_executor.complete_dbs_task(test_dbs, False)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='dbs']/td/a/strong").text)

    @try_except_method
    def test_can_complete_people_in_your_home_task_without_other_adults_but_with_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering No to the question
        'Does anyone aged 16 or over live or work in your home?'
        """
        applicant_email = self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            False,
            None, None, None,
            None, None, None, None, None,
            faker.email(), True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child', applicant_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_but_without_other_children(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        applicant_email = self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            faker.email(), False, None, None, None,
            None, None, None,
            None, applicant_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_cannot_resend_health_check_email_more_than_three_times(self):
        """
        Tests that the adult health check email cannot be sent more than three times within 24 hours
        """
        applicant_email = self.create_standard_eyfs_application()

        # Complete People in your home task (until status is Waiting)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()

        # Guidance page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_id("id_adults_in_home_0").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 30).until(
            expected_conditions.title_contains("Details of adults in your home")
        )

        self.selenium_task_executor.get_driver().find_element_by_id("id_1-first_name").send_keys(faker.first_name())
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-middle_names").send_keys(faker.first_name())
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-last_name").send_keys(faker.last_name_female())
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-date_of_birth_0").send_keys(20)
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-date_of_birth_1").send_keys(4)
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-date_of_birth_2").send_keys(1995)
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-relationship").send_keys('Friend')
        self.selenium_task_executor.get_driver().find_element_by_id("id_1-email_address").send_keys(faker.email())

        # Javascript click execution is used here given element falls out of view location range
        submit_button = self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']")
        self.selenium_task_executor.get_driver().execute_script("arguments[0].click();", submit_button)

        WebDriverWait(self.selenium_task_executor.get_driver(), 30).until(
            expected_conditions.title_contains("DBS checks on adults in your home"))

        self.selenium_task_executor.get_driver().find_element_by_id("id_1-dbs_certificate_number").send_keys(123456654321)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 30).until(expected_conditions.title_contains("Children in your home"))
        self.selenium_task_executor.get_driver().find_element_by_id("id_children_in_home_1").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        # Javascript click execution is used here given element falls out of view location range
        submit_button = self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']")
        self.selenium_task_executor.get_driver().execute_script("arguments[0].click();", submit_button)

        # Task summary confirmation
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").send_keys(Keys.RETURN)

        # Email confirmation page
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").send_keys(Keys.RETURN)

        # Resend health check e-mail 3 times
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Resend email").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Resend email']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Resend email").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Resend email']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Resend email").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Resend email']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Resend email").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Resend email']").click()

        self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary")

    @try_except_method
    def test_can_apply_as_a_childminder_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.complete_full_question_set()

        self.selenium_task_executor.complete_review()
        self.selenium_task_executor.complete_declaration()

        # Card number must be 5454... due to this being a Worldpay API test value
        test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
        self.selenium_task_executor.complete_payment('Visa', '5454545454545454', str(random.randint(1, 12)),
                                                     str(random.randint(20, 30)),
                                                     faker.name(),
                                                     test_cvc)

    @try_except_method
    def test_sign_out_link_not_shown_when_unauthenticated(self):
        """
        Tests that the sign-out link is not present if a user is not logged in
        """
        self.selenium_task_executor.navigate_to_base_url()
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out')

    @try_except_method
    def test_can_sign_out_when_authenticated(self):
        """
        Tests that the sign-out link is present if a user is logged in and they can successfully sign out
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.assertEqual("Application saved", self.selenium_task_executor.get_driver().title)

        # After signing out make sure sign out link no longer shows
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out')

    @try_except_method
    def test_banner_link_returns_user_to_task_list_when_authenticated(self):
        """
        Tests that when a user is logged in clicking the "Register as a childminder" link in the banner returns them to the
        task list
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Register as a childminder').click()
        self.assertEqual("Register as a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs_without_authenticating(self):
        """
        Tests the costs page can be accessed without logging in.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Costs').click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs_when_authenticated(self):
        """
        Tests the costs page can be accessed when logged in.
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Costs').click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_costs_not_shown_if_further_information_required(self):
        """
        Tests that the costs link is not shown if an application has been returned to the applicant
        """
        # Load fixtures to populate a test application
        call_command("loaddata", "test_returned_application.json", verbosity=0)

        # Note that this email address is loaded from fixture
        self.selenium_task_executor.sign_back_in('test@informed.com')

        # Test that costs link is not shown in header
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('Costs')

        # Test that costs link is not shown above task list
        with self.assertRaises(NoSuchElementException):
            self.selenium_task_executor.get_driver().find_element_by_link_text('more about costs')

        # Test that the grayed out class is present (for unflagged tasks which are disabled)
        self.assertTrue(self.selenium_task_executor.get_driver().find_element_by_class_name('grayed-out'))

        # Test that the task-disabled class is present (for unflagged tasks which are disabled)
        self.assertTrue(self.selenium_task_executor.get_driver().find_element_by_class_name('task-disabled'))

    @try_except_method
    def test_updated_tasks_are_listed_in_confirmation_page(self):
        """
        Tests that the costs link is not shown if an application has been returned to the applicant
        """
        # Load fixtures to populate a test application
        call_command("loaddata", "test_returned_application.json", verbosity=0)

        # Note that this email address is loaded from fixture
        self.selenium_task_executor.sign_back_in('test@informed.com')

        self.selenium_task_executor.get_driver().find_element_by_id("health").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//a[contains(@href,'health/booklet/')]").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        # Verify that the updated task is still accessible
        self.selenium_task_executor.get_driver().find_element_by_id("health").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='review']/td/a/span").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_share_info_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_display_contact_details_on_web").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_suitable_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_information_correct_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_change_declare").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Payment confirmed"))

        # Check if the updated task is listed on the confirmation page
        self.selenium_task_executor.get_driver().find_elements_by_xpath(
            "//*[contains(text(), 'Health declaration booklet')]")

    @try_except_method
    def test_can_access_help_without_authenticating(self):
        """
        Tests the help page can be accessed without logging in.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Help and contacts').click()
        self.assertEqual("Help and contacts", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_help_when_authenticated(self):
        """
        Tests the help page can be accessed once logged in.
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Help and contacts').click()
        self.assertEqual("Help and contacts", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_access_costs(self):
        """
        Tests that the costs page can be reached
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Costs").click()
        self.assertEqual("Costs of becoming a childminder", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_begin_returning_user_sign_in_process(self):
        """
        Tests that the sign in page for returning users can be reached
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Sign in']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_acc_selection_1-label").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(test_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_apply_as_a_childminder_using_full_question_set(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status marked as Done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        # When completing first aid training task ensure that certification is within last 3 years
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), self.current_year - 1,
            False
        )

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='first_aid']/td/a/strong").text)

        self.selenium_task_executor.complete_health_declaration_task()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='health']/td/a/strong").text)

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, False)

        self.assertEqual("Done",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//tr[@id='dbs']/td/a/strong").text)

        self.selenium_task_executor.complete_eyfs_details(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1)
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='eyfs']/td/a/strong").text)

        self.selenium_task_executor.complete_people_in_your_home_task(
            False,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            faker.email(), True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child', test_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

        self.selenium_task_executor.complete_references_task(
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email(),
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email()
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='references']/td/a/strong").text)

        self.selenium_task_executor.complete_review()
        self.selenium_task_executor.complete_declaration()

        # Card number must be 5454... due to this being a Worldpay API test value
        test_cvc = ''.join(str(random.randint(0, 9)) for _ in range(3))
        self.selenium_task_executor.complete_payment('Visa', '5454545454545454', str(random.randint(1, 12)),
                                                     str(20),
                                                     faker.name(),
                                                     test_cvc)

    @try_except_method
    def test_can_apply_as_a_childminder_no_overnight_care(self):
        """
        Test to exercise the largest set of questions possible within a childminder application
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, False)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

    @try_except_method
    def test_first_aid_out_of_date_guidance_shown(self):
        """
        Test to check that if a first aid training certificate is expired a user is informed they need to update their training
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, False)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        # When completing first aid training task set expired certification year
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), 2012,
            True
        )

        self.assertEqual("First aid training",
                         self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_cannot_change_email_to_preexisting_one(self):
        """
        Complete application contact details then attempt to change email to one which exists under another application.
        Should .......
        """
        first_email = self.create_standard_eyfs_application()
        second_email = self.create_standard_eyfs_application()

        # Click through to changing email for second account.
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='email_address']/td/a").click()

        # Change email of second account to the first one.
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(first_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        self.assertEqual("We've sent a link to {}.".format(first_email),
                         self.selenium_task_executor.get_driver().find_element_by_xpath("//html/body/main/div[2]/p[1]").text)

        # Try to grab email validation URL.
        # Should redirect to bad link; no email validation link sent for preexsiting email.
        self.selenium_task_executor.navigate_to_email_validation_url()
        self.assertEqual('Link used already', self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_cannot_create_multiple_applications_using_same_email(self):
        """
        Test to ensure a user cannot register twice with the same email address
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_cancel_application(self):
        """
        Test to assert a new application can be cancelled
        """
        self.create_standard_eyfs_application()

        self.selenium_task_executor.get_driver().find_element_by_link_text("Cancel application").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Cancel Application']").click()
        self.assertEqual("Application Cancelled", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_save_and_exit(self):
        """
        Test to assert a user can save and exit an application
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Save and exit").click()
        self.assertEqual("Application saved", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_task_summaries_display_on_completion(self):
        """
        Tests that once a task is marked as Done, clicking that task from the task list shows the summary page
        """
        self.complete_full_question_set()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='children']/td/a/span").click()
        self.assertEqual("Check your answers: type of childcare",
                         self.selenium_task_executor.get_driver().find_element_by_xpath("//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='personal_details']/td/a/span").click()
        self.assertEqual("Check your answers: your personal details",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='first_aid']/td/a/span").click()
        self.assertEqual("Check your answers: first aid training",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='health']/td/a/span").click()

        self.assertEqual("Check your answers: health declaration booklet",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='dbs']/td/a/span").click()
        self.assertEqual("Check your answers: criminal record (DBS) check",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
        self.assertEqual("Check your answers: people in your home",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//input[@value='Confirm and continue']").send_keys(
            Keys.RETURN)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='references']/td/a/span").click()
        self.assertEqual("Check your answers: references",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/h1").text)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//tr[@id='review']/td/a/span").click()

    @try_except_method
    def test_can_create_application_using_email_with_apostrophe_and_hyphen(self):
        """
        Test to ensure a user can enter an email where the name includes an apostrophe and/or hyphen
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = 'Alfie-James.O\'Brien@emailtestworld.com'
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)

        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_invalid_email_raises_error_box(self):
        """
        Tests that passing an invalid email address to the email form raises validation error.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address("invalid_email")
        self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary")
        self.selenium_task_executor.get_driver().find_element_by_class_name("form-group-error")

    @try_except_method
    def test_invalid_phone_number_raises_error(self):
        """
        Tests that passing an invalid phone number to the phone number form raises a validation error
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address("test_email@email.com")
        self.selenium_task_executor.navigate_to_email_validation_url()
        self.selenium_task_executor.get_driver().find_element_by_id("id_mobile_number").send_keys('a')
        self.selenium_task_executor.get_driver().find_element_by_id("id_add_phone_number").send_keys('a')
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary")
        self.selenium_task_executor.get_driver().find_element_by_class_name("form-group-error")

    @try_except_method
    def test_unticked_age_groups_raises_error(self):
        """
        Tests that not selecting any age groups raises a validation error.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.complete_your_login_details(email_address="test@test.com",
                                                                phone_number='07754000000',
                                                                additional_phone_number=None)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary")
        self.selenium_task_executor.get_driver().find_element_by_class_name("form-group-error")

    @try_except_method
    def test_unticked_overnight_care_box_raises_error(self):
        """
        Tests that not selecting yes/no on overnight care raises a validation error.
        """
        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.complete_your_login_details(email_address="test@test.com",
                                                                phone_number='07754000000',
                                                                additional_phone_number=None)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_type_of_childcare_0").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()
        self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary")
        self.selenium_task_executor.get_driver().find_element_by_class_name("form-group-error")

    @try_except_method
    def test_entering_validation_email_link_twice_raises_error(self):
        """
        Tests that using email link for sign-in more than once returns a 'bad link' page.
        """
        self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.selenium_task_executor.navigate_to_email_validation_url()
        self.selenium_task_executor.navigate_to_email_validation_url()

        self.assertEqual("Link used already",
                         self.selenium_task_executor.get_driver().find_element_by_class_name("form-title").text)

    @try_except_method
    def test_entering_invalid_sms_code_raises_error(self):
        '''
        Tests that entering invalid sms code (none at all, too short, too long or incorrect) raises error.
        '''
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        # Test no code, too short a code, too long a code and incorrect code.
        test_codes = ['', '1', '123456', '10101']
        for code in test_codes:
            self.selenium_task_executor.get_driver().find_element_by_name(
                'magic_link_sms').clear()  # Clear form of previous code.
            self.selenium_task_executor.get_driver().find_element_by_name('magic_link_sms').send_keys(code)
            self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()
            self.assertIn("problem",
                          self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    @try_except_method
    def test_invalid_mobile_security_question_raises_error(self):
        '''
        Test that invalid response to mobile number security question form raises validation error.
        4 different login scenarios:
            - App contains user DBS: Ask for DBS Certificate No.
            - User given details of whom they live with: Ask for DoB for eldest person in home.
            - User has completed personal details: Ask for DoB and postcode.
            * If none of above, ask for user's phone number.
        '''
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        # Select 'Don't have your phone?' to trigger security question.
        self.selenium_task_executor.get_driver().find_element_by_link_text('Don\'t have your phone?').click()
        self.assertIn("Mobile",
                      self.selenium_task_executor.get_driver().find_element_by_class_name("heading-small").text)

        # Test no number, too short a mobile number, too long a mobile number and incorrect mobile number.
        test_numbers = ['', '0', '123456789012', '07754000001']
        for test_number in test_numbers:
            self.selenium_task_executor.get_driver().find_element_by_name("security_answer").clear()
            self.selenium_task_executor.get_driver().find_element_by_name("security_answer").send_keys(test_number)
            self.selenium_task_executor.get_driver().find_element_by_xpath(
                "//input[@value='Save and continue']").click()
            self.assertIn("problem",
                          self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    @try_except_method
    def test_invalid_personal_details_security_question_raises_error(self):
        '''
        Test that invalid response to postcode security question form raises validation error.
        4 different login scenarios:
            - App contains user DBS: Ask for DBS Certificate No.
            - User given details of whom they live with: Ask for DoB for eldest person in home.
            - User has completed personal details: Ask for DoB and postcode.
            * If none of above, ask for user's phone number.
        '''
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)
        # Fill out personal details.
        self.selenium_task_executor.complete_personal_details(forename="Gael",
                                                              middle_name="Viaros",
                                                              surname="Givet",
                                                              dob_day="1",
                                                              dob_month="1",
                                                              dob_year="1985",
                                                              is_location_of_care=True)
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        # Select 'Don't have your phone?' to trigger security question.
        self.selenium_task_executor.get_driver().find_element_by_link_text('Don\'t have your phone?').click()
        self.assertEqual("Please enter your postcode and date of birth.",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/form/div/p[2]").text)

        # Populate DoB form with correct values - same validation already covered in test_invalid_eldest_dob_security_question_raises_error.
        DoB = ['1', '1', '1985']
        for index, value in enumerate(DoB):
            self.selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_{}".format(index)).send_keys(
                value)

        # Test for postcode validation messages. Test no code, invalid code and incorrect code.
        postcodes = ['', 'abc', 'SW1 1AA']
        for postcode in postcodes:
            self.selenium_task_executor.get_driver().find_element_by_id("id_security_answer").clear()
            self.selenium_task_executor.get_driver().find_element_by_id("id_security_answer").send_keys(postcode)
            self.selenium_task_executor.get_driver().find_element_by_xpath(
                "//input[@value='Save and continue']").click()
            self.assertIn("problem",
                          self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    @try_except_method
    def test_invalid_eldest_dob_security_question_raises_error(self):
        """
        Test that invalid response to eldest person at home's DoB security question form raises validation error.
        4 different login scenarios:
            - App contains user DBS: Ask for DBS Certificate No.
            - User given details of whom they live with: Ask for DoB for eldest person in home.
            - User has completed personal details: Ask for DoB and postcode.
            * If none of above, ask for user's phone number.
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.complete_people_in_your_home_task(True,
                                                                      faker.first_name(), faker.first_name(),
                                                                      faker.last_name_female(),
                                                                      1, 1, 1985, 'Friend', 121212121212,
                                                                      faker.email(), True, faker.first_name(),
                                                                      faker.first_name(),
                                                                      faker.last_name_female(),
                                                                      random.randint(1, 28), random.randint(1, 12),
                                                                      random.randint(self.current_year - 14,
                                                                                     self.current_year - 1),
                                                                      'Child', test_email
                                                                      )

        try:
            self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        except StaleElementReferenceException:
            # Allow stale element exception to pass through as DOM will have been updated
            pass

        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        # Select 'Don't have your phone?' to trigger security question.
        self.selenium_task_executor.get_driver().find_element_by_link_text('Don\'t have your phone?').click()
        self.assertEqual("Please enter the date of birth of the eldest person living in your home.",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//html/body/main/div[2]/form/div/p[2]").text)

        test_DoBs = [
            ['', '2', '1666'],  # No day value.
            ['2', '', '1666'],  # No month value.
            ['2', '2', ''],  # No year value.
            ['50', '2', '1666'],  # Invalid day value.
            ['2', '20', '1666'],  # Invalid moth value.
            ['2', '2', '123'],  # Distant past.
            ['2', '2', '12345'],  # Future year.
            ['2', '2', '1666']  # Incorrect DoB.
        ]

        for DoB in test_DoBs:
            for index, value in enumerate(DoB):
                self.selenium_task_executor.get_driver().find_element_by_id("id_date_of_birth_{}".format(index)).clear()
                self.selenium_task_executor.get_driver().find_element_by_id(
                    "id_date_of_birth_{}".format(index)).send_keys(
                    value)

            self.selenium_task_executor.get_driver().find_element_by_xpath(
                "//input[@value='Save and continue']").click()
            self.assertIn("problem",
                          self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_and_children_containing_apostrophe_in_name(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        applicant_email = self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            "Dan-D'arcy", "John-O'Paul", "Omar-O\'Leary",
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            faker.email(), True, "Billie'o-Jo", "Bri'an-James", "O\'Malley-Micheals",
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child', applicant_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_invalid_dbs_security_question_raises_error(self):
        '''
        Test that invalid response to DBS number security question form raises validation error.
        4 different login scenarios:
            - App contains user DBS: Ask for DBS Certificate No.
            - User given details of whom they live with: Ask for DoB for eldest person in home.
            - User has completed personal details: Ask for DoB and postcode.
            * If none of above, ask for user's phone number.
        '''
        test_email = self.create_standard_eyfs_application()
        test_dbs = '123456789101'
        self.selenium_task_executor.complete_dbs_task(test_dbs, True)

        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out').click()
        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        # Select 'Don't have your phone?' to trigger security question.
        self.selenium_task_executor.get_driver().find_element_by_link_text('Don\'t have your phone?').click()
        self.assertIn("DBS", self.selenium_task_executor.get_driver().find_element_by_class_name("heading-small").text)

        # Test no DBS number, too short a DBS number, too long a DBS number and an incorrect DBS number.
        test_numbers = ['', '1', '0123456789101112', '987654321987']
        for test_number in test_numbers:
            self.selenium_task_executor.get_driver().find_element_by_name("security_answer").clear()
            self.selenium_task_executor.get_driver().find_element_by_name("security_answer").send_keys(test_number)
            self.selenium_task_executor.get_driver().find_element_by_xpath(
                "//input[@value='Save and continue']").click()
            self.assertIn("problem",
                          self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    @try_except_method
    def test_can_create_application_using_email_with_apostrophe_and_hyphen(self):
        """
        Test to ensure a user can enter an email where the name includes an apostrophe and/or hyphen
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = 'Alfie-James.O\'Brien@emailtestworld.com'
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        self.selenium_task_executor.navigate_to_base_url()
        self.selenium_task_executor.register_email_address(test_email)

        self.assertEqual("Check your email", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_can_complete_people_in_your_home_task_with_other_adults_and_children_containing_apostrophe_in_name(self):
        """
        Tests that the people in your home task can still be completed when answering Yes to the question
        'Does anyone aged 16 or over live or work in your home?' but No to the question 'Do you live with any children under 16?'
        """
        applicant_email = self.create_standard_eyfs_application()

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            "Dan-D'arcy", "John-O'Paul", "Omar-O\'Leary",
            random.randint(1, 29), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            faker.email(), True, "Billie'o-Jo", "Bri'an-James", "O\'Malley-Micheals",
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child', applicant_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

    @try_except_method
    def test_user_can_change_email_address(self):
        """
         Test that a user can change the email address associated with their account.
        """
        self.create_standard_eyfs_application()
        new_email = "plant@walle.com"

        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Change Your email").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").clear()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(new_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Check your email"))
        self.selenium_task_executor.navigate_to_email_validation_url()

        # From task list, go to the account details and check that the email has changed.
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.assertEqual(new_email, self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='email_address']/td[2]").text)

    @try_except_method
    def test_user_can_use_resend_link_when_changing_email(self):
        self.create_standard_eyfs_application()
        new_email = "eva@walle.com"

        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.selenium_task_executor.get_driver().find_element_by_link_text("Change Your email").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").click()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").clear()
        self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(new_email)
        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Continue']").click()

        # Confirm change email address.
        WebDriverWait(self.selenium_task_executor.get_driver(), 10).until(
            expected_conditions.title_contains("Check your email"))

        # We need to store the first validation url to confirm that it has changed upon clicking 'resend email'.
        first_validation_url = None
        while first_validation_url is None:
            first_validation_url = os.environ.get('EMAIL_VALIDATION_URL')

        self.selenium_task_executor.get_driver().find_element_by_link_text("resend the email").click()
        second_validation_url = self.selenium_task_executor.navigate_to_email_validation_url()

        # From task list, go to the account details and check that the email has changed.
        self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").click()
        self.assertEqual(new_email, self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='email_address']/td[2]").text)

        # Assert that the validation url changed; that is, that the 'resend email' link did indeed resend the email.
        self.assertNotEqual(first_validation_url, second_validation_url)

    @try_except_method
    def test_user_cannot_resend_sms_code_more_than_three_times(self):
        """
        Test to ensure that, if the user requests to resend their SMS security code a fourth time, they are instead
        asked to enter their security question details.
        """
        test_email = self.create_standard_eyfs_application()
        self.selenium_task_executor.get_driver().find_element_by_link_text('Sign out')
        self.selenium_task_executor.navigate_to_SMS_validation_page(test_email)

        for n in range(3):
            self.selenium_task_executor.get_driver().find_element_by_link_text("Didn't get a code?").click()
            self.selenium_task_executor.get_driver().find_element_by_id("id_send_new_code_button").click()

        self.selenium_task_executor.get_driver().find_element_by_link_text("Still didn't get a code?").click()
        self.assertEqual("Sign in question", self.selenium_task_executor.get_driver().title)

    @try_except_method
    def test_applicant_cannot_enter_own_email_or_same_email_for_adults_in_home(self):
        """
        Test to ensure that the applicant cannot enter their own or same email for adults living in house

        """
        # Here it tests that the applicant cannot enter their own email address as a household member's email address
        applicant_email = self.create_standard_eyfs_application()

        household_member_email_id = faker.email()

        driver = self.selenium_task_executor.get_driver()

        driver.find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_adults_in_home_0").click()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        WebDriverWait(self.selenium_task_executor.get_driver(), 30).until(
            expected_conditions.title_contains("Details of adults in your home")
        )

        driver.find_element_by_id("id_1-first_name").send_keys(faker.first_name())
        driver.find_element_by_id("id_1-middle_names").send_keys(faker.first_name())
        driver.find_element_by_id("id_1-last_name").send_keys(faker.last_name())
        driver.find_element_by_id("id_1-date_of_birth_0").send_keys(random.randint(1, 28))
        driver.find_element_by_id("id_1-date_of_birth_1").send_keys(random.randint(1, 12))
        driver.find_element_by_id("id_1-date_of_birth_2").send_keys(random.randint(1980, 2000))
        driver.find_element_by_id("id_1-relationship").send_keys('Co-inhabitant')
        driver.find_element_by_id("id_1-email_address").send_keys(applicant_email)

        # Javascript click execution is used here given element falls out of view location range
        submit_button = driver.find_element_by_xpath("//input[@value='Save and continue']")
        driver.execute_script("arguments[0].click();", submit_button)

        self.assertIn("problem",
                      self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

        # From here it tests that two adults email ids are not same
        driver.find_element_by_id("id_1-email_address").clear()
        driver.find_element_by_id("id_1-email_address").send_keys(household_member_email_id)
        time.sleep(1)
        driver.find_element_by_name("add_person").click()
        driver.find_element_by_id("id_2-first_name").send_keys(faker.first_name())
        driver.find_element_by_id("id_2-middle_names").send_keys(faker.first_name())
        driver.find_element_by_id("id_2-last_name").send_keys(faker.last_name())
        driver.find_element_by_id("id_2-date_of_birth_0").send_keys(random.randint(1, 28))
        driver.find_element_by_id("id_2-date_of_birth_1").send_keys(random.randint(1, 12))
        driver.find_element_by_id("id_2-date_of_birth_2").send_keys(random.randint(1980, 2000))
        driver.find_element_by_id("id_2-relationship").send_keys('Friend')
        driver.find_element_by_id("id_2-email_address").send_keys(household_member_email_id)
        driver.find_element_by_id("adult-details-save").click()
        print(driver.find_element_by_xpath("//div[@id='id_2-email_address-group']/span").text)
        driver.find_element_by_xpath("//div[@id='id_2-email_address-group']/span").click()
        self.assertEqual("Their email address cannot be the same as another person in your home",
                         driver.find_element_by_xpath("//div[@id='id_2-email_address-group']/span").text)


    # @try_except_method
    # def test_feedback_page(self):
    #     """
    #     Test to ensure that the applicant can successfully send feedback
    #     """
    #     self.selenium_task_executor.navigate_to_base_url()
    #     test_email = faker.email()
    #     test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
    #     test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()
    #     self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
    #     self.selenium_task_executor.get_driver().find_element_by_id("feedback").click()
    #     self.assertEqual("Feedback", self.selenium_task_executor.get_driver().title)
    #     self.selenium_task_executor.get_driver().find_element_by_id("id_feedback").send_keys('Test feedback')
    #     self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys(faker.email())
    #     self.selenium_task_executor.get_driver().find_element_by_id("submit").click()
    #     self.assertEqual("Type of childcare", self.selenium_task_executor.get_driver().title)
    #     self.selenium_task_executor.get_driver().find_element_by_id("feedback").click()
    #     characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    #     random_string = ''
    #     # Generates 1500-character random string
    #     for i in range(0, 1500):
    #         random_string += random.choice(characters)
    #     self.selenium_task_executor.get_driver().find_element_by_id("id_feedback").send_keys(random_string)
    #     self.selenium_task_executor.get_driver().find_element_by_id("submit").click()
    #     self.assertIn("problem",
    #                   self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)
    #     self.selenium_task_executor.get_driver().find_element_by_id("id_feedback").send_keys('Test feedback')
    #     self.selenium_task_executor.get_driver().find_element_by_id("id_email_address").send_keys('Test')
    #     self.selenium_task_executor.get_driver().find_element_by_id("submit").click()
    #     self.assertIn("problem",
    #                   self.selenium_task_executor.get_driver().find_element_by_class_name("error-summary").text)

    def complete_full_question_set(self):
        """
        Helper method for completing all questions in an application
        """
        applicant_email = self.create_standard_eyfs_application()

        # When completing first aid training task ensure that certification is within last 3 years
        self.selenium_task_executor.complete_first_aid_training(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1),
            False
        )

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Save and continue']").click()

        self.selenium_task_executor.get_driver().find_element_by_xpath("//input[@value='Confirm and continue']").click()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='first_aid']/td/a/strong").text)

        self.selenium_task_executor.complete_eyfs_details(
            faker.company(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 2, self.current_year - 1)
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='eyfs']/td/a/strong").text)

        self.selenium_task_executor.complete_health_declaration_task()

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='health']/td/a/strong").text)

        test_dbs = ''.join(str(random.randint(1, 9)) for _ in range(12))
        self.selenium_task_executor.complete_dbs_task(test_dbs, True)

        self.assertEqual("Done",
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//tr[@id='dbs']/td/a/strong").text)

        self.selenium_task_executor.complete_people_in_your_home_task(
            True,
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990), 'Friend', 121212121212,
            faker.email(), True, faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(self.current_year - 14, self.current_year - 1),
            'Child', applicant_email=applicant_email
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='other_people']/td/a/strong").text)

        self.selenium_task_executor.complete_references_task(
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email(),
            faker.first_name(), faker.last_name_female(), 'Friend', random.randint(1, 12), random.randint(1, 10),
            self.selenium_task_executor.generate_random_mobile_number(), faker.email()
        )

        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='references']/td/a/strong").text)

    def create_standard_eyfs_application(self):
        """
        Helper method for starting a new application
        :return: email address used to register the application
        """
        self.selenium_task_executor.navigate_to_base_url()

        test_email = faker.email()
        test_phone_number = self.selenium_task_executor.generate_random_mobile_number()
        test_alt_phone_number = self.selenium_task_executor.generate_random_mobile_number()

        self.selenium_task_executor.complete_your_login_details(test_email, test_phone_number, test_alt_phone_number)
        self.selenium_task_executor.complete_type_of_childcare(True, False, False, True)

        # Below DOB means they are an adult so do not fire validation triggers
        self.selenium_task_executor.complete_personal_details(
            faker.first_name(), faker.first_name(), faker.last_name_female(),
            random.randint(1, 28), random.randint(1, 12), random.randint(1950, 1990),
            True
        )

        # Check task status set to done
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='account_details']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='children']/td/a/strong").text)
        self.assertEqual("Done", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//tr[@id='personal_details']/td/a/strong").text)

        return test_email

    def tearDown(self):
        self.selenium_driver.quit()

        try:
            del os.environ['EMAIL_VALIDATION_URL']
        except:
            pass

        super(ApplyAsAChildminder, self).tearDown()
        self.assertEqual([], self.verification_errors)
