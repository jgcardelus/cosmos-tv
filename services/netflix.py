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
import framework as fmk
from services.show import Show, Episode, Season

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

        self.last_show_parsed = 0
        self.show_parse_length = 15

        self.shows = []
        self.show_name = None
        self.episode = None
        self.season = None


        # HAS SENT OPENED APP
        self.opened_app = False

        # WAIT UNTIL SECONDS
        self.sleep_time = 1
        self.sleep_max_count = 5

        # SCAN SETTINGS
        self.max_scroll = 4

        # LOAD SETTINGS
        self.username = username
        self.password = password
        self.netflix_user = netflix_user

    def wait_until(self, xpath, html=None, container=None):
        counter = 0
        if container == None:
            container = self.driver
        while True:
            try:
                selector = container.find_element_by_xpath(xpath)
                attr = selector.get_attribute('innerHTML')

                if counter == self.sleep_max_count:
                    break

                if html == None:
                    if attr != html:
                        break

                if attr == html:
                    break
                else:
                    time.sleep(self.sleep_time)
                    counter += 1
            except exceptions.NoSuchElementException:
                if counter == self.sleep_max_count:
                    break

                time.sleep(self.sleep_time)
                counter += 1
            except exceptions.StaleElementReferenceException:
                if counter == self.sleep_max_count:
                    break

                time.sleep(self.sleep_time)
                counter += 1

    def wait_until_css(self, css_selector, html=None, container=None):
        counter = 0
        if container == None:
            container = self.driver
        while True:
            try:
                selector = container.find_element_by_css_selector(css_selector)
                attr = selector.get_attribute('innerHTML')

                if counter == self.sleep_max_count:
                    break

                if html == None:
                    if attr != html:
                        break

                if attr == html:
                    break
                else:
                    time.sleep(self.sleep_time)
                    counter += 1
            except exceptions.NoSuchElementException:
                if counter == self.sleep_max_count:
                    break

                time.sleep(self.sleep_time)
                counter += 1
            except exceptions.StaleElementReferenceException:
                if counter == self.sleep_max_count:
                    break

                time.sleep(self.sleep_time)
                counter += 1

    def start(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-data-dir=' + config.data_dir_path)

        self.driver = webdriver.Chrome(executable_path=config.driver_path, chrome_options=chrome_options)
        self.get(self.url)

    def render_shows(self):
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

    def render_opened_app(self):
        parser = fmk.Parser()
        if not self.opened_app:
            opened_app_json = parser.parse_app(self.name, "", self.id_)
            server.emit("opened-apps", opened_app_json)
        else:
            opened_app_json = parser.parse_app(self.name, "", self.id_)
            server.emit("opened-apps-update", opened_app_json)

    def get(self, url):
        self.driver.get(url)
        self.render_opened_app()
        self.focus()
        self.init_profile()

        self.scan()
        if len(self.shows) > 0:
            self.render_shows()

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
        try:
            # Wait until main page has been loaded
            self.wait_until('//ul[@class="tabbed-primary-navigation"]')
            self.scroll_page()
            self.driver.execute_script("window.scrollTo(0, 0);")

            elements = self.driver.find_elements_by_class_name('slider-item')
            self.shows = []

            counter = 0
            max_count = 50
            
            if len(elements) < max_count:
                max_count = len(elements)

            while counter < max_count:
                try:
                    element = elements[counter]
                    show_container = element.find_element_by_css_selector("p.fallback-text")
                    url_container = element.find_element_by_css_selector("a[role='link']")

                    show_name = show_container.get_attribute('innerHTML')
                    url = url_container.get_attribute('href')

                    show = Show(show_name, url, element)
                    self.shows.append(show)
                    
                except exceptions.NoSuchElementException:
                    pass
                    
                counter += 1
        except:
            pass

    def emit_scan_result(self, result_data):
        server.emit("scan-result", result_data)

    def log_in(self):
        log_in_button = None
        try:
            log_in_button = self.driver.find_element_by_xpath('//a[@data-uia="header-login-link"]')
        except exceptions.NoSuchElementException:
            pass
        
        if log_in_button != None:
            log_in_button.click()
            username_input = self.driver.find_element_by_xpath('//input[@id="id_userLoginId"]')
            username_input.send_keys(self.username)
            password_input = self.driver.find_element_by_xpath('//input[@id="id_password"]')
            password_input.send_keys(self.password)

            submit_log_in = self.driver.find_element_by_xpath('//button[@data-uia="login-submit-button"]')
            submit_log_in.click()

        return log_in_button

    def select_user(self):
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

        return profile_gate

    def init_profile(self):
        # FIND LOG-IN
        log_in = self.log_in()
        profile_gate = self.select_user()

        if log_in == None and profile_gate == None:
            time.sleep(1)

    def start_show(self, name, url):
        show = None
        for iter_show in self.shows:
            if iter_show.name == name and iter_show.url == url:
                show = iter_show
                break
        
        if show != None:
            # Check if element contains episodes
            is_series = self.deep_scan(show)
            
            if not is_series:
                # It is not a series, open player
                self.get(show.url)
            else:
                # Create parser object
                parser = fmk.Parser()
                # Show the results
                scan_result = parser.parse_series(show)
                self.emit_scan_result(scan_result)
        else:
            self.get(url)

    def deep_scan(self, show):
        is_series = False
        try:
            more_info = show.container.find_element_by_css_selector('div.bob-jawbone-chevron')
            more_info.click()
            self.wait_until("//li[@id='tab-Overview']")
            container = self.driver.find_element_by_xpath('//div[@class="jawBoneFadeInPlaceContainer"]')
            episodes_selector = container.find_element_by_css_selector('li#tab-Episodes')
            episodes_selector.click()

            # Iterate through seasons
            self.wait_until_css('div.nfDropDown')
            dropbox = container.find_element_by_css_selector("div.nfDropDown")
            dropbox.click()
            self.wait_until_css("a.sub-menu-link")
            seasons_buttons = self.driver.find_elements_by_css_selector("a.sub-menu-link")
            for i in range(len(seasons_buttons)):
                if i > 0:
                    # Click on the dropdown
                    elem = self.driver.find_element_by_css_selector("div.nfDropDown")
                    elem.click()
                
                # Click on season and get seasons name
                self.wait_until_css("a.sub-menu-link")
                select_buttons = self.driver.find_elements_by_css_selector("a.sub-menu-link")
                season_name = select_buttons[i].get_attribute('innerHTML')
                select_buttons[i].click()

                season_info = season_name.split(' ')
                season_number = int(season_info[1])

                season = Season(season_number)

                time.sleep(1)
                container = self.driver.find_element_by_css_selector('div.episodesContainer')
                # Select episodes in container
                print("Select container")
                self.wait_until_css('div.slider-item', container=container)
                print("Container selected")
                season_episodes = container.find_elements_by_css_selector('div.slider-item')

                for season_episode in season_episodes:
                    # Get name
                    self.wait_until_css("div.episodeTitle p", container=season_episode)
                    episode_name_container = season_episode.find_element_by_css_selector('div.episodeTitle p')
                    episode_name = episode_name_container.get_attribute('innerHTML')
                    
                    # Get link
                    self.wait_until('//a[@data-uia="play-button"]', container=season_episode)
                    episode_url_container = season_episode.find_element_by_xpath('//a[@data-uia="play-button"]')
                    episode_url = episode_url_container.get_attribute('href')
                    
                    # Get number
                    self.wait_until_css("div.episodeNumber span", container=season_episode)
                    episode_number_container = season_episode.find_element_by_css_selector("div.episodeNumber span")
                    episode_number = int(episode_number_container.get_attribute('innerHTML'))
                    
                    episode = Episode(episode_name, episode_url, episode_number)
                    season.episodes.append(episode)

                show.seasons.append(season)

            is_series = True
        except exceptions.NoSuchElementException:
            pass

        return is_series

    def focus(self):
        self.driver.maximize_window()
       
    def close(self):
        self.driver.quit()