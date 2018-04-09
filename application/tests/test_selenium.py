# -*- coding: utf-8 -*-

import os
import socket
from datetime import datetime

from django.test import LiveServerTestCase, override_settings, tag

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

@tag('selenium')
@override_settings(ALLOWED_HOSTS=['*'])
class ApplyAsAChildminder(LiveServerTestCase):

    port = 8000
    host = '0.0.0.0'

    def setUp(self):

        #self.host = socket.gethostbyname(socket.gethostname())

        self.driver = webdriver.Remote(
            command_executor='http://' + os.environ['SELENIUM_HOST'] + ':4444/wd/hub',
            desired_capabilities={'platform': 'ANY', 'browserName': 'firefox', 'version': ''}
        )
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

        self.verification_errors = []
        self.accept_next_alert = True

        super(ApplyAsAChildminder, self).setUp()

    def test_apply_as_a_childminder(self):

        try:
            driver = self.driver
            driver.get("http://" + os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] + "/childminder")
            driver.find_element_by_xpath("//input[@value='Start now']").click()
            driver.find_element_by_xpath("//input[@value='Create my account']").click()
            driver.find_element_by_id("id_email_address").click()
            driver.find_element_by_id("id_email_address").clear()
            driver.find_element_by_id("id_email_address").send_keys("cruddasj@informed.com")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_mobile_number").click()
            driver.find_element_by_id("id_mobile_number").clear()
            driver.find_element_by_id("id_mobile_number").send_keys("07824893361")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_security_question").click()
            driver.find_element_by_id("id_security_question").clear()
            driver.find_element_by_id("id_security_question").send_keys("test")
            driver.find_element_by_id("id_security_answer").clear()
            driver.find_element_by_id("id_security_answer").send_keys("test")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_type_of_childcare_0").click()
            driver.find_element_by_id("id_type_of_childcare_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_id("id_overnight_care_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='personal_details']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_first_name-label").click()
            driver.find_element_by_id("id_first_name").clear()
            driver.find_element_by_id("id_first_name").send_keys("James")
            driver.find_element_by_id("id_last_name").clear()
            driver.find_element_by_id("id_last_name").send_keys("Cruddas")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_date_of_birth_0").click()
            driver.find_element_by_id("id_date_of_birth_0").clear()
            driver.find_element_by_id("id_date_of_birth_0").send_keys("22")
            driver.find_element_by_id("id_date_of_birth_1").click()
            driver.find_element_by_id("id_date_of_birth_1").clear()
            driver.find_element_by_id("id_date_of_birth_1").send_keys("1")
            driver.find_element_by_id("id_date_of_birth_2").click()
            driver.find_element_by_id("id_date_of_birth_2").clear()
            driver.find_element_by_id("id_date_of_birth_2").send_keys("1991")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_postcode").click()
            driver.find_element_by_id("id_postcode").clear()
            driver.find_element_by_id("id_postcode").send_keys("WA14 5GQ")
            driver.find_element_by_name("postcode-search").click()
            driver.find_element_by_id("id_address").click()
            Select(driver.find_element_by_id("id_address")).select_by_visible_text("INFORMED SOLUTIONS LTD, THE OLD BANK, OLD MARKET PLACE, ALTRINCHAM, WA14 4PA")
            driver.find_element_by_id("id_address").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_location_of_care_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='first_aid']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_first_aid_training_organisation").click()
            driver.find_element_by_id("id_first_aid_training_organisation").clear()
            driver.find_element_by_id("id_first_aid_training_organisation").send_keys("JMC Training")
            driver.find_element_by_id("id_title_of_training_course").clear()
            driver.find_element_by_id("id_title_of_training_course").send_keys("Test")
            driver.find_element_by_id("id_course_date_0").click()
            driver.find_element_by_id("id_course_date_0").clear()
            driver.find_element_by_id("id_course_date_0").send_keys("22")
            driver.find_element_by_id("id_course_date_1").click()
            driver.find_element_by_id("id_course_date_1").clear()
            driver.find_element_by_id("id_course_date_1").send_keys("1")
            driver.find_element_by_id("id_course_date_2").clear()
            driver.find_element_by_id("id_course_date_2").send_keys("2018")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_declaration").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='health']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_send_hdb_declare").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='dbs']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_dbs_certificate_number").click()
            driver.find_element_by_id("id_dbs_certificate_number").clear()
            driver.find_element_by_id("id_dbs_certificate_number").send_keys("121212121212")
            driver.find_element_by_id("id_convictions_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='other_people']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_adults_in_home_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_children_in_home_1").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='references']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_first_name").click()
            driver.find_element_by_id("id_first_name").clear()
            driver.find_element_by_id("id_first_name").send_keys("Test")
            driver.find_element_by_id("id_last_name").clear()
            driver.find_element_by_id("id_last_name").send_keys("Person")
            driver.find_element_by_id("id_relationship").clear()
            driver.find_element_by_id("id_relationship").send_keys("Friend")
            driver.find_element_by_id("id_time_known_0").clear()
            driver.find_element_by_id("id_time_known_0").send_keys("2")
            driver.find_element_by_id("id_time_known_1").clear()
            driver.find_element_by_id("id_time_known_1").send_keys("2")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_postcode").click()
            driver.find_element_by_id("id_postcode").clear()
            driver.find_element_by_id("id_postcode").send_keys("WA14 5GQ")
            driver.find_element_by_name("postcode-search").click()
            driver.find_element_by_id("id_address").click()
            Select(driver.find_element_by_id("id_address")).select_by_visible_text("INFORMED SOLUTIONS LTD, THE OLD BANK, OLD MARKET PLACE, ALTRINCHAM, WA14 4PA")
            driver.find_element_by_id("id_address").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_phone_number").click()
            driver.find_element_by_id("id_phone_number").clear()
            driver.find_element_by_id("id_phone_number").send_keys("07791618129")
            driver.find_element_by_id("id_email_address").click()
            driver.find_element_by_id("id_email_address").clear()
            driver.find_element_by_id("id_email_address").send_keys("james.cruddas@informed.com")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_first_name").click()
            driver.find_element_by_id("id_first_name").clear()
            driver.find_element_by_id("id_first_name").send_keys("Test")
            driver.find_element_by_id("id_last_name").clear()
            driver.find_element_by_id("id_last_name").send_keys("User")
            driver.find_element_by_id("id_relationship").clear()
            driver.find_element_by_id("id_relationship").send_keys("Neighbour")
            driver.find_element_by_id("id_time_known_0").clear()
            driver.find_element_by_id("id_time_known_0").send_keys("2")
            driver.find_element_by_id("id_time_known_1").clear()
            driver.find_element_by_id("id_time_known_1").send_keys("4")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_postcode").click()
            driver.find_element_by_id("id_postcode").clear()
            driver.find_element_by_id("id_postcode").send_keys("WA14 5GQ")
            driver.find_element_by_name("postcode-search").click()
            driver.find_element_by_id("id_address").click()
            Select(driver.find_element_by_id("id_address")).select_by_visible_text("INFORMED SOLUTIONS LTD, THE OLD BANK, OLD MARKET PLACE, ALTRINCHAM, WA14 4PA")
            driver.find_element_by_id("id_address").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_id("id_phone_number").click()
            driver.find_element_by_id("id_phone_number").clear()
            driver.find_element_by_id("id_phone_number").send_keys("07791618129")
            driver.find_element_by_id("id_email_address").click()
            driver.find_element_by_id("id_email_address").clear()
            driver.find_element_by_id("id_email_address").send_keys("james.cruddas@informed.com")
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//tr[@id='review']/td/a/span").click()
            driver.find_element_by_xpath("//input[@value='Confirm and continue']").click()
            driver.find_element_by_xpath("//input[@value='Continue']").click()
            driver.find_element_by_id("id_background_check_declare-label").click()
            driver.find_element_by_id("id_inspect_home_declare-label").click()
            driver.find_element_by_xpath("//div[@id='id_interview_declare-group']/div").click()
            driver.find_element_by_id("id_interview_declare-label").click()
            driver.find_element_by_id("id_share_info_declare").click()
            driver.find_element_by_id("id_information_correct_declare-label").click()
            driver.find_element_by_id("id_change_declare").click()
            driver.find_element_by_xpath("//input[@value='Confirm and pay your fee']").click()
            driver.find_element_by_id("id_payment_method_0").click()
            driver.find_element_by_xpath("//input[@value='Save and continue']").click()
            Select(driver.find_element_by_id("id_card_type")).select_by_visible_text("Visa")
            driver.find_element_by_id("id_card_number").clear()
            driver.find_element_by_id("id_card_number").send_keys("5454545454545454")
            Select(driver.find_element_by_id("id_expiry_date_0")).select_by_visible_text("6")
            Select(driver.find_element_by_id("id_expiry_date_1")).select_by_visible_text("2018")
            driver.find_element_by_id("id_cardholders_name").clear()
            driver.find_element_by_id("id_cardholders_name").send_keys("Test user")
            driver.find_element_by_id("id_card_security_code").clear()
            driver.find_element_by_id("id_card_security_code").send_keys("352")
            driver.find_element_by_xpath("//input[@value='Make payment and apply']").click()
        except Exception as e:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            scr = driver.find_element_by_tag_name('html')
            scr.screenshot('selenium/screenshot-%s-%s.png' % (self.__class__.__name__, now))
            raise(e)


    def is_element_present(self, how, what):

        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False

        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException:
            return False

        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        super(ApplyAsAChildminder, self).tearDown()
        self.assertEqual([], self.verification_errors)
