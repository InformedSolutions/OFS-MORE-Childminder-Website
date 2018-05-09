from .apply_as_a_childminder import *
from faker import Faker

# Configure faker to use english locale
faker = Faker('en_GB')


@tag('selenium')
class EYFSTests(ApplyAsAChildminder):

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
                             "//main[@id='content']/form/div/h1").text)

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

        self.assertEqual("Early Years Register", self.selenium_task_executor.get_driver().find_element_by_xpath(
            "//main[@id='content']/form/div/h1").text)

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
                         self.selenium_task_executor.get_driver().find_element_by_xpath(
                             "//main[@id='content']/form/div/h1").text)
