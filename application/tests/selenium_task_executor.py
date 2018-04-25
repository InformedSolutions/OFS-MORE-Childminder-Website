import os
import random

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumTaskExecutor:
    """
    Helper class for executing reusable selenium steps
    """

    __driver = None
    __base_url = None

    def __init__(self, driver, base_url):
        """
        Default constructor
        :param driver: the selenium driver to be used for executing steps
        :param base_url: the base url against which tests are to be executed
        """
        self.__driver = driver
        self.__base_url = base_url

    def set_driver(self, driver):
        """
        Method for setting the Selenium driver instance to use for testing purposes
        :param driver: the selenium driver instance to use for testing purposes
        """
        self.__driver = driver

    def get_driver(self):
        """
        Method for getting the current Selenium driver instance
        :return: Current Selenium driver instance
        """
        if self.__driver is None:
            raise Exception("A Selenium driver has not been set. Please use the set_driver method to "
                            "configure which driver to use for tests.")
        return self.__driver

    def set_base_url(self, base_url):
        """
        Method for setting the base url against which tests will be executed
        :param base_url: the base url against which tests will be executed
        """
        self.__base_url = base_url

    def get_base_url(self):
        """
        Method for getting the base url against which tests will be executed
        :return: the base url against which tests will be executed
        """
        if self.__base_url is None:
            raise Exception("No base URL for tests has been set. Please use the set_base_url method"
                            "to configure an appropriate target URL.")
        return self.__base_url

    def navigate_to_base_url(self):
        """
        Method for navigating to the base url of a site
        """
        driver = self.get_driver()
        driver.get(self.__base_url)

    def register_email_address(self, email_address):
        """
        Selenium steps for registering an email address against an application
        """
        driver = self.get_driver()
        driver.find_element_by_xpath("//input[@value='Start now']").click()
        driver.find_element_by_id("id_acc_selection_0-label").click()
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_email_address").send_keys(email_address)
        driver.find_element_by_xpath("//input[@value='Continue']").click()

    def sign_back_in(self, email_address):
        """
        Selenium steps for signing back into an application
        :param email_address: the email address to be used during the sign in process.
        """
        driver = self.get_driver()
        self.navigate_to_base_url()
        driver.find_element_by_xpath("//input[@value='Start now']").click()
        driver.find_element_by_id("id_acc_selection_1-label").click()
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_email_address").send_keys(email_address)
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        WebDriverWait(driver, 10).until(
            expected_conditions.title_contains("Check your email"))

        self.navigate_to_email_validation_url()
        sms_validation_code = os.environ.get('SMS_VALIDATION_CODE')
        driver.find_element_by_id("id_magic_link_sms").send_keys(sms_validation_code)
        driver.find_element_by_xpath("//input[@value='Continue']").click()

    def navigate_to_email_validation_url(self):
        """
        Selenium steps for navigating to the email validation page in the login journey
        """
        driver = self.get_driver()
        validation_url = os.environ.get('EMAIL_VALIDATION_URL')
        driver.get(validation_url)

    def complete_your_login_details(self, email_address, phone_number, additional_phone_number):
        """
        Selenium steps to create a new application by completing the login details task
        :param email_address: the email address to be registered
        :param phone_number: the phone number to be registered
        :param additional_phone_number: an optional additional phone number to be registered
        """
        self.register_email_address(email_address)
        self.navigate_to_email_validation_url()

        driver = self.get_driver()

        driver.find_element_by_id("id_mobile_number").send_keys(phone_number)

        if additional_phone_number is not None:
            driver.find_element_by_id("id_add_phone_number").send_keys(additional_phone_number)

        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Summary page
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_type_of_childcare(self, zero_to_five, five_to_seven, eight_or_over, providing_overnight_care):
        """
        Selenium steps to complete the type of childcare task
        :param zero_to_five: a boolean for whether the 0 to 5 year olds age group should be checked
        :param five_to_seven: a boolean for whether the 5 to 7 year olds age group should be checked
        :param eight_or_over: a boolean for whether the 8 years or older age group should be checked
        :param providing_overnight_care: a boolean for choosing whether overnight care is being provided
        """
        driver = self.get_driver()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        # Ages of children selections
        if zero_to_five is True:
            driver.find_element_by_id("id_type_of_childcare_0").click()

        if five_to_seven is True:
            driver.find_element_by_id("id_type_of_childcare_1").click()

        if eight_or_over is True:
            driver.find_element_by_id("id_type_of_childcare_3").click()

        # Confirm selection
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

        # Overnight care page
        if providing_overnight_care is True:
            driver.find_element_by_id("id_overnight_care_0").click()
        else:
            driver.find_element_by_id("id_overnight_care_1").click()

        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Confirmation page
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_personal_details(self, forename, middle_name, surname, dob_day, dob_month, dob_year,
                                  is_location_of_care):
        """
        Selenium steps to complete the personal details task
        :param forename: the applicant's forename
        :param middle_name: the applicant's middle name
        :param surname: the applicant's surname
        :param dob_day: the day value for an applicant's date of birth
        :param dob_month: the month value for an applicant's date of birth
        :param dob_year: the year value for an applicant's date of birth
        :param is_location_of_care: a boolean flag for whether the applicant's address will be the location of car
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='personal_details']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_first_name").send_keys(forename)

        if middle_name is not None:
            driver.find_element_by_id("id_middle_names").send_keys(middle_name)

        driver.find_element_by_id("id_last_name").send_keys(surname)

        # Confirm name
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        driver.find_element_by_id("id_date_of_birth_0").send_keys(dob_day)
        driver.find_element_by_id("id_date_of_birth_1").send_keys(dob_month)
        driver.find_element_by_id("id_date_of_birth_2").send_keys(dob_year)

        # Confirm DOB
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Enter home address
        self.select_test_address()

        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        if is_location_of_care is True:
            driver.find_element_by_id("id_location_of_care_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()

            # Confirm task summary page
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            return

        driver.find_element_by_id("id_location_of_care_1").click()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Childcare location address
        self.select_test_address()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Confirm task summary page
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_first_aid_training(self, training_provider, completion_date_day, completion_date_month,
                                    completion_date_year, expect_update_page):
        """
        Selenium steps for completing the first aid training task
        :param training_provider: the name of the training provider to be set
        :param completion_date_day: the day value for an applicant's certification date
        :param completion_date_month: the month value for an applicant's certification date
        :param completion_date_year: the year value for an applicant's certification date
        :param expect_update_page: a boolean to indicate whether it is expected that a user must update their training certificate
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='first_aid']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        # Training details
        driver.find_element_by_id("id_first_aid_training_organisation").send_keys(training_provider)
        driver.find_element_by_id("id_title_of_training_course").send_keys("Test course")
        driver.find_element_by_id("id_course_date_0").send_keys(completion_date_day)
        driver.find_element_by_id("id_course_date_1").send_keys(completion_date_month)
        driver.find_element_by_id("id_course_date_2").send_keys(completion_date_year)
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Yield early return if the page stating a user must update their training is expected
        if expect_update_page is True:
            return

        # Confirm declaration
        driver.find_element_by_id("id_declaration").click()
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        # Confirm task summary
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_health_declaration_task(self):
        """
        Selenium steps for completing the health declaration task
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='health']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_send_hdb_declare").click()
        driver.find_element_by_xpath("//input[@value='Continue']").click()
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_dbs_task(self, dbs_number, has_convictions):
        """
        Selenium steps for completing the criminal convictions task
        :param dbs_number: the DBS number to be set
        :param has_convictions: a boolean flag for whether an applicant has criminal convictions or not
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='dbs']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        # Set DBS number
        driver.find_element_by_id("id_dbs_certificate_number").send_keys(dbs_number)

        if has_convictions is not True:
            driver.find_element_by_id("id_convictions_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            # Task summary
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            return

        driver.find_element_by_id("id_convictions_0").click()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Confirm will send DBS certificate
        driver.find_element_by_id("id_declaration").click()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Task summary
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_people_in_your_home_task(self, other_adults_in_home, other_adult_forename, other_adult_middle_name,
                                          other_adult_surname,
                                          other_adult_dob_day, other_adult_dob_month, other_adult_dob_year,
                                          other_adult_relationship, other_adult_dbs,
                                          children_in_home, child_forename, child_middle_name, child_surname,
                                          child_dob_day, child_dob_month, child_dob_year, child_relationship):
        """
        Selenium steps for completing the people in your home task
        :param other_adults_in_home: a boolean flag for whether an applicant has other adults living in their home
        :param other_adult_forename: the forename of the other adult to be set
        :param other_adult_middle_name: the middle name of the other adult to be set
        :param other_adult_surname: the surname of the other adult to be set
        :param other_adult_dob_day: the day value for the other adult's date of birth to be set
        :param other_adult_dob_month: the month value for the other adult's date of birth to be set
        :param other_adult_dob_year: the year value for the other adult's date of birth to be set
        :param other_adult_relationship: the relationship to the other adult
        :param other_adult_dbs: the dbs number for the other adult
        :param children_in_home: a boolean flag for whether an applicant has other children living in their home
        :param child_forename: the forename of the child to be set
        :param child_middle_name: the middle name of the child to be set
        :param child_surname: the surname of the child to be set
        :param child_dob_day: the day value for the child's date of birth to be set
        :param child_dob_month: the month value for the child's date of birth to be set
        :param child_dob_year: the year value for the child's date of birth to be set
        :param child_relationship: the relationship to the other child
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        if other_adults_in_home is True:
            driver.find_element_by_id("id_adults_in_home_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_1-first_name").send_keys(other_adult_forename)
            driver.find_element_by_id("id_1-middle_names").send_keys(other_adult_middle_name)
            driver.find_element_by_id("id_1-last_name").send_keys(other_adult_surname)
            driver.find_element_by_id("id_1-date_of_birth_0").send_keys(other_adult_dob_day)
            driver.find_element_by_id("id_1-date_of_birth_1").send_keys(other_adult_dob_month)
            driver.find_element_by_id("id_1-date_of_birth_2").send_keys(other_adult_dob_year)
            driver.find_element_by_id("id_1-relationship").send_keys(other_adult_relationship)
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_1-dbs_certificate_number").send_keys(other_adult_dbs)
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_1-permission_declare-label").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
        else:
            driver.find_element_by_id("id_adults_in_home_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        if children_in_home is True:
            driver.find_element_by_id("id_children_in_home_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_1-first_name").send_keys(child_forename)
            driver.find_element_by_id("id_1-middle_names").send_keys(child_middle_name)
            driver.find_element_by_id("id_1-last_name").send_keys(child_surname)
            driver.find_element_by_id("id_1-date_of_birth_0").send_keys(child_dob_day)
            driver.find_element_by_id("id_1-date_of_birth_1").send_keys(child_dob_month)
            driver.find_element_by_id("id_1-date_of_birth_2").send_keys(child_dob_year)
            driver.find_element_by_id("id_1-relationship").send_keys(child_relationship)
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
        else:
            driver.find_element_by_id("id_children_in_home_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Task summary confirmation
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").send_keys(Keys.RETURN)

    def complete_references_task(self, first_reference_forename, first_reference_surname, first_reference_relationship,
                                 first_reference_time_known_months, first_reference_time_known_years,
                                 first_reference_phone_number, first_reference_email,
                                 second_reference_forename, second_reference_surname, second_reference_relationship,
                                 second_reference_time_known_months, second_reference_time_known_years,
                                 second_reference_phone_number, second_reference_email):
        """
        Selenium steps for completing the references task
        :param first_reference_forename: the forename of the person acting as an applicant's first reference
        :param first_reference_surname: the surname of the person acting as an applicant's first reference
        :param first_reference_relationship: the relationship of the person acting as an applicant's first reference
        :param first_reference_time_known_months: the number of months the person acting as first reference has known the applicant
        :param first_reference_time_known_years: the number of years the person acting as first reference has known the applicant
        :param first_reference_phone_number: the phone number of the person acting as an applicant's first reference
        :param first_reference_email: the email address of the person acting as an applicant's first reference
        :param second_reference_forename: the forename of the person acting as an applicant's second reference
        :param second_reference_surname: the surname of the person acting as an applicant's second reference
        :param second_reference_relationship: the relationship of the person acting as an applicant's second reference
        :param second_reference_time_known_months: the number of months the person acting as second reference has known the applicant
        :param second_reference_time_known_years: the number of years the person acting as second reference has known the applicant
        :param second_reference_phone_number: the phone number of the person acting as an applicant's second reference
        :param second_reference_email: the email address of the person acting as an applicant's second reference
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='references']/td/a/span").click()

        # Guidance page
        driver.find_element_by_xpath("//input[@value='Continue']").click()

        driver.find_element_by_id("id_first_name").send_keys(first_reference_forename)
        driver.find_element_by_id("id_last_name").send_keys(first_reference_surname)
        driver.find_element_by_id("id_relationship").send_keys(first_reference_relationship)
        driver.find_element_by_id("id_time_known_0").send_keys(first_reference_time_known_months)
        driver.find_element_by_id("id_time_known_1").send_keys(first_reference_time_known_years)
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        self.select_test_address()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        driver.find_element_by_id("id_phone_number").send_keys(first_reference_phone_number)
        driver.find_element_by_id("id_email_address").send_keys(first_reference_email)
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        driver.find_element_by_id("id_first_name").send_keys(second_reference_forename)
        driver.find_element_by_id("id_last_name").send_keys(second_reference_surname)
        driver.find_element_by_id("id_relationship").send_keys(second_reference_relationship)
        driver.find_element_by_id("id_time_known_0").send_keys(second_reference_time_known_months)
        driver.find_element_by_id("id_time_known_1").send_keys(second_reference_time_known_years)
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        self.select_test_address()
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        driver.find_element_by_id("id_phone_number").send_keys(second_reference_phone_number)
        driver.find_element_by_id("id_email_address").send_keys(second_reference_email)
        driver.find_element_by_xpath("//input[@value='Save and continue']").click()

        # Confirm task summary
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()

    def complete_review(self):
        """
        Selenium steps for completing the review task
        """
        driver = self.get_driver()

        driver.find_element_by_xpath("//tr[@id='review']/td/a/span").click()
        driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
        driver.find_element_by_xpath("//input[@value='Continue']").click()

    def complete_payment(self, card_payment, card_type, card_number, expiry_date_month, expiry_date_year,
                         cardholder_name, cvc):
        """
        Selenium steps for completing the payment pages
        :param card_payment: a boolean flag for whether payment should be made by card
        :param card_type: the card type (e.g. VISA)
        :param card_number: the card number to be used for payment
        :param expiry_date_month: the card expiry date month
        :param expiry_date_year: the card expiry date year
        :param cardholder_name: the cardholders name to be used for payment
        :param cvc: the cvc code to be used for payment
        """
        driver = self.get_driver()

        if card_payment is True:
            driver.find_element_by_id("id_payment_method_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            Select(driver.find_element_by_id("id_card_type")).select_by_visible_text(card_type)
            driver.find_element_by_id("id_card_number").send_keys(card_number)
            driver.find_element_by_id("id_expiry_date_0").send_keys(expiry_date_month)
            driver.find_element_by_id("id_expiry_date_1").send_keys(expiry_date_year)
            driver.find_element_by_id("id_cardholders_name").send_keys(cardholder_name)
            driver.find_element_by_id("id_card_security_code").send_keys(cvc)
            driver.find_element_by_xpath("//input[@value='Make payment and apply']").click()
        else:
            driver.find_element_by_id("id_payment_method_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("submit-btn").click()

    def complete_declaration(self):
        """
        Selenium steps for completing the declaration page
        """
        driver = self.get_driver()

        driver.find_element_by_id("id_background_check_declare").click()
        driver.find_element_by_id("id_inspect_home_declare").click()
        driver.find_element_by_id("id_interview_declare").click()
        driver.find_element_by_id("id_share_info_declare").click()
        driver.find_element_by_id("id_information_correct_declare-label").click()
        driver.find_element_by_id("id_change_declare").click()
        driver.find_element_by_xpath("//input[@value='Confirm and pay your fee']").click()

    def select_test_address(self):
        """
        Reusable method for selecting a test address
        """
        driver = self.get_driver()

        # Postcode lookup
        driver.find_element_by_id("id_postcode").send_keys("WA14 4PA")
        driver.find_element_by_name("postcode-search").click()

        # Select matched result
        driver.find_element_by_id("id_address").click()
        Select(driver.find_element_by_id("id_address")).select_by_visible_text(
            "INFORMED SOLUTIONS LTD, THE OLD BANK, OLD MARKET PLACE, ALTRINCHAM, WA14 4PA")

    @staticmethod
    def generate_random_mobile_number():
        """
        Generates a random UK mobile number for testing purposes
        :return: A random UK mobile phone number
        """
        return '0779' + ''.join(str(random.randint(0, 9)) for _ in range(7))
