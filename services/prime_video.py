import os
import json
import time
import keyboard

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import server
import config
import framework as fmk
from services.show import Show, Episode, Season

# LOAD CONFIGURATION
username = None
password = None
netflix_user = None
if config.settings_path != None:
    if os.path.isfile(config.settings_path):
        settings_file = open(config.settings_path, 'r')
        settings = json.loads(settings_file.read())

        for app in settings["apps"]:
            if app["name"] == "prime-video":
                username = app["username"]
                password = app["password"]

class Prime_Video:
    def __init__(self, driver, window_handles):
        # BASIC VARIABLES
        self.driver = driver
        self.window_handles = window_handles
        self.url = "https://www.primevideo.com"
        self.name = "Prime Video"
        self.id_ = "prime-video"

        # MEDIA VARIABLES
        self.is_show_on = False
        self.time = 0
        self.total_time = 0
        self.scan_result = None
        self.skip_intro_requested = False
        self.skip_outro_requested = False
        self.skip_button = None

        # OPENED APP VARIABLES
        self.created_open_app = False

        # SCAN SETTINGS
        self.shows = []
        self.show_name = None
        self.episode = None
        self.season = None

        self.max_scroll = 1
        self.last_show_parsed = 0
        self.show_parse_length = 15

        # LOAD SETTINGS
        self.username = username
        self.password = password

    def get(self, url):
        self.driver.get(url)
        self.render_opened_app()
        self.render_show_info()
        self.focus()
        self.init_profile()

        self.scan(20)
        if len(self.shows) > 0:
            self.render_scan()

    def render_opened_app(self):
        parser = fmk.Parser()
        opened_app_json = None

        if not self.created_open_app:
            opened_app_json = parser.parse_open_app(self.name, "", self.id_)
            self.created_open_app = True
            server.emit("opened-apps", opened_app_json)
        else:
            opened_app_json = None
            if self.episode != None:
                opened_app_json = parser.parse_open_app(self.name, self.episode.name, self.id_)
            elif self.show_name != None:
                opened_app_json = parser.parse_open_app(self.name, self.show_name, self.id_)
            else:
                opened_app_json = parser.parse_open_app(self.name, "", self.id_)

            server.emit("opened-apps-update", opened_app_json)

    def render_scan(self):
        start = self.last_show_parsed
        end = self.last_show_parsed + self.show_parse_length
        if self.last_show_parsed + self.show_parse_length >= len(self.shows):
            end = len(self.shows)

        self.last_show_parsed = end
        if start != end:
            # Create parser object
            parser = fmk.Parser()
            shows_json = parser.parse_shows(self.shows[start:end])
            self.emit_scan_result(shows_json)

    def render_show_info(self):
        if self.episode != None:
            server.emit('show-name', self.episode.name)
            parser = fmk.Parser()
            info = parser.parse_season_episode_info(self.season.number, self.episode.number)
            server.emit('season-episode-info', info)
        elif self.show_name != None:
            server.emit('show-name', self.show_name)
            server.emit('season-episode-info', "")
        else:
            server.emit('show-name', self.name)
            server.emit('season-episode-info', "")

    def log_in(self):
        log_in_button = None
        try:
            log_in_button = self.driver.find_element_by_css_selector('span.pv-nav-accounts-single-link')
        except exceptions.NoSuchElementException:
            pass
        
        if log_in_button != None:
            log_in_button.click()
            username_input = self.driver.find_element_by_xpath('//input[@type="email"]')
            username_input.send_keys(self.username)
            password_input = self.driver.find_element_by_xpath('//input[@type="password"]')
            password_input.send_keys(self.password)

            submit_log_in = self.driver.find_element_by_xpath('//input[@id="signInSubmit"]')
            submit_log_in.click()

        return log_in_button

    def init_profile(self):
        # FIND LOG-IN
        log_in = self.log_in()

        if log_in == None:
            time.sleep(1) # Change, wait until page loads

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

    def scan(self, max_scan_count):
        try:
            wait = fmk.Wait_Until(self.driver)
            # Wait until main page has been loaded
            wait.wait_xpath('//div[@class="pv-nav-primary-components"]')
            self.scroll_page()
            self.driver.execute_script("window.scrollTo(0, 0);")

            elements = self.driver.find_elements_by_css_selector('div.tst-packshot-link')
            print(len(elements))
            self.shows = []

            counter = 0
            if len(elements) < max_scan_count:
                max_scan_count = len(elements)

            while counter < max_scan_count:
                try:
                    element = elements[counter]
                    # SELECT ELEMENT
                    info_container = element.find_element_by_css_selector('a')
                    # GET INFORMATION
                    show_name = info_container.get_attribute('aria-label')
                    url = info_container.get_attribute('href')
                    # SAVE SHOW
                    show = Show(show_name, url, element)
                    self.shows.append(show)
                    
                except exceptions.NoSuchElementException:
                    pass
                    
                counter += 1
        except:
            pass

    def emit_scan_result(self, result_data):
        server.emit("scan-result", result_data)

    def start_show(self, name, url):
        show = None
        for iter_show in self.shows:
            if iter_show.name == name and iter_show.url == url:
                show = iter_show
                break
        
        if show != None:
            self.get(show.url)

        else:
            self.get(url)

    def load_session(self):
        if self.skip_intro_requested or self.skip_outro_requested:
            server.emit("activate-skip", "skip")
        
        if self.is_show_on:
            self.update_show_info()

    def get_media_information(self):
        try:
            media_screen = self.driver.find_element_by_css_selector('div.dv-player-fullscreen')
            if not self.is_show_on:
                self.is_show_on = True
                self.update_show_info()

            if self.is_show_on:
                self.get_skip_button()
            
        except exceptions.NoSuchElementException:
            if self.is_show_on:
                self.is_show_on = False
                self.reset_media_info()

    def reset_media_info(self):
        self.season = None
        self.episode = None
        self.show_name = ""

        self.render_opened_app()
        self.render_show_info()

    def update_show_info(self):
        self.get_show_info()
        self.render_opened_app()
        self.render_show_info()

    def get_show_info(self):
        title_div = self.driver.find_element_by_css_selector('div.title')
        self.show_name = title_div.get_attribute('innerHTML')

    def get_skip_button(self):
        self.get_skip_intro()
        self.get_skip_outro()

    def get_skip_intro(self):
        try:
            skip_button = self.driver.find_element_by_css_selector('div.skipElement')
            if not self.skip_intro_requested:
                self.skip_button = skip_button
                self.skip_intro_requested = True

                server.emit("activate-skip", "skip")
        except exceptions.NoSuchElementException:
            if self.skip_intro_requested:
                self.skip_intro_requested = False
                server.emit("deactivate-skip", "skip")
        except exceptions.StaleElementReferenceException:
            if self.skip_intro_requested:
                self.skip_intro_requested = False
                server.emit("deactivate-skip", "skip")
    
    def get_skip_outro(self):
        try:
            skip_button = self.driver.find_element_by_css_selector('div.nextUpCard')
            if not self.skip_outro_requested:
                self.skip_button = skip_button
                self.skip_outro_requested = True

                server.emit("activate-skip", "skip")
        except exceptions.NoSuchElementException:
            if self.skip_outro_requested:
                self.skip_outro_requested = False
                server.emit("deactivate-skip", "skip")
        except exceptions.StaleElementReferenceException:
            if self.skip_outro_requested:
                self.skip_outro_requested = False
                server.emit("deactivate-skip", "skip")

    def skip(self):
        if self.skip_outro_requested or self.skip_intro_requested:
            try:
                self.skip_button.click()
                self.skip_requested = False
            except exceptions.StaleElementReferenceException:
                print("Element has gone stale")

    def fullscreen(self):
        if self.is_show_on:
            fmk.keyboard.press(fmk.k_key.f11)
            fmk.keyboard.release(fmk.k_key.f11)
        else:
            server.raise_not("Select a show first")

    def play(self):
        if self.is_show_on:
            fmk.keyboard.press(fmk.k_key.space)
            fmk.keyboard.release(fmk.k_key.space)
        else:
            server.raise_not("Select a show first")

    def next_show(self):
        if self.is_show_on:
            try:
                fmk.mouse.move(10, 10)
                next_show_button = self.driver.find_element_by_css_selector('div.nextTitleButton')
                next_show_button.click()
            except exceptions.NoSuchElementException:
                server.raise_not("This episode does not allow this action")
                pass
        else:
            server.raise_not("Select a show first")

    def forwards(self):
        if self.is_show_on:
            fmk.keyboard.press(fmk.k_key.right)
            fmk.keyboard.release(fmk.k_key.right)
        else:
            server.raise_not("Select a show first")

    def backwards(self):
        if self.is_show_on:
            fmk.keyboard.press(fmk.k_key.left)
            fmk.keyboard.release(fmk.k_key.left)
        else:
            server.raise_not("Select a show first")

    def focus(self):
        self.driver.maximize_window()
       
    def close(self):
        self.driver.quit()