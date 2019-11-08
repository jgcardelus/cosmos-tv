import os
import json
import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import server
import config
from services.show import Show, Episode

username = None
password = None
netflix_user = None
if config.settings_path != None:
    if os.path.isfile(config.settings_path):
        settings_file = open(config.settings_path, 'r')
        settings = json.loads(settings_file.read())

        for app in settings["apps"]:
            if app["name"] == "netflix":
                username = app["username"]
                password = app["password"]
                netflix_user = app["netflix-user"]

class Netflix:
    def __init__(self):
        self.driver = None
        self.url = "https://www.netflix.com"
        self.name = "Netflix"
        self.id_ = "netflix"

        self.time = 0
        self.total_time = 0
        self.scan_result = None
        self.skip_requested = False

        self.shows = []
        self.show_name = None
        self.episode = None
        self.season = None

        # SCAN SETTINGS
        self.max_scroll = 4

        # LOAD SETTINGS
        self.username = username
        self.password = password
        self.netflix_user = netflix_user

    def wait_until(self, xpath, html=None):
        counter = 0
        while True:
            try:
                selector = self.driver.find_element_by_xpath(xpath)
                attr = selector.get_attribute('innerHTML')

                if counter == 10000:
                    break

                if html == None:
                    if attr != html:
                        break

                if attr == html:
                    break
                else:
                    time.sleep(1)
                    counter += 1
            except exceptions.NoSuchElementException:
                if counter == 10000:
                    break

                time.sleep(1)
                counter += 1

    def start(self):
        self.driver = webdriver.Chrome(executable_path=config.driver_path, chrome_options=config.chrome_options)
        self.driver.get(self.url)
        self.focus()
        self.start_checks()

        self.scan()

    def scroll_page(self):
        height = int(self.driver.execute_script("return document.body.offsetHeight"))
        counter = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.offsetHeight);")
            time.sleep(1)
            new_height = int(self.driver.execute_script("return document.body.offsetHeight"))
            counter += 1
            if height != new_height:
                height = new_height
            else:
                break

            if counter == self.max_scroll:
                break

    def scan(self):
        print("Scanning")

        # Wait until main page has been loaded
        self.wait_until('//ul[@class="tabbed-primary-navigation"]')

        self.scroll_page()
        self.driver.execute_script("window.scrollTo(0, 0);")
        
        elements = self.driver.find_elements_by_class_name('slider-item')
        # shows_container = elements.find_element_by_xpath('//p[@class="fallback-text"]')

    
        shows = []
        for element in elements:
            try:
                show_container = element.find_element_by_css_selector('p.fallback-text')
                url_container = element.find_element_by_css_selector("a[role='link']")

                show_name = show_container.get_attribute('innerHTML')
                url = url_container.get_attribute('href')

                show = Show(show_name, url, element)
                self.shows.append(show)
            except exceptions.NoSuchElementException:
                pass

    def start_checks(self):
        # FIND LOG-IN
        log_in = None
        try:
            log_in = self.driver.find_element_by_xpath('//a[@data-uia="header-login-link"]')
        except exceptions.NoSuchElementException:
            pass
        
        if log_in != None:
            log_in.click()
            username_input = self.driver.find_element_by_xpath('//input[@id="id_userLoginId"]')
            username_input.send_keys(self.username)
            password_input = self.driver.find_element_by_xpath('//input[@id="id_password"]')
            password_input.send_keys(self.password)

            submit_log_in = self.driver.find_element_by_xpath('//button[@data-uia="login-submit-button"]')
            submit_log_in.click()

        profile_gate = None
        try:
            profile_gate = self.driver.find_element_by_xpath('//ul[@class="choose-profile"]')
        except exceptions.NoSuchElementException:
            pass

        if profile_gate != None:
            profiles = self.driver.find_elements_by_xpath('//a[@class="profile-link"]')
            netflix_users = self.driver.find_elements_by_xpath('//span[@class="profile-name"]')
            for i, netflix_user in enumerate(netflix_users):
                if self.netflix_user == netflix_user.get_attribute('innerHTML'):
                    profiles[i].click()
                    break

    def parse_scan():
        pass

    def focus(self):
        self.driver.maximize_window()
       
    def close(self):
        self.driver.quit()



