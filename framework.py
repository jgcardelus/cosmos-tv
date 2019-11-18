import random
import json
import time

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions

import config
import server
import actuators

# SERVICES IMPORTS
from services.netflix import Netflix

## FRAMEWORK VARIABLES
# DEFINE DRIVER
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--user-data-dir=' + config.data_dir_path)

driver = None

# MEDIA VARS
opened_apps = []
active_app = None
volume = 0
is_mute = False

# PARSE
class Parser:
    def __init__(self):
        self.unwanted_chars = "!·$%&/()='`*;:-|@#~½¬{[]}[─·̣ \\<>"

    def clean_text(self, raw_text):
        text = ""
        for letter in raw_text:
            if letter not in self.unwanted_chars:
                text += letter

        return text

    def generate_show_id(self, name, i, prefix=None):
        show_id = ""

        if prefix != None:
            show_id = prefix
        
        name_chunks = name.lower().split(' ')
        for i in range(len(name_chunks)):
            name_chunks[i] = self.clean_text(name_chunks[i])

        name_id = "".join(name_chunks)

        show_id += name_id + '-' + str(i)

        return show_id

    def parse_shows(self, shows):
        shows_dict = {"scan-result": []}
        for i, show in enumerate(shows):
            show_id = self.generate_show_id(show.name, i)

            show_dict = {
                "name": show.name,
                "url": show.url,
                "id": show_id,
                "episodes": []
            }

            shows_dict["scan-result"].append(show_dict)

        shows_json = json.dumps(shows_dict)
        return shows_json

    def parse_season(self, season):
        season_id = "title-season-" + str(season.number)
        season_name = "Season " + str(season.number)

        season_dict = {
            "name": season_name,
            "url": "no-url",
            "id": season_id,
            "episodes": []
        }

        for episode in season.episodes:
            episode_id = str(season.number) + '-ep-' + str(episode.number)
            episode_dict = {
                "name": episode.name,
                "url": episode.url,
                "id": episode_id
            }

            season_dict["episodes"].append(episode_dict)

        return season_dict

    def parse_series(self, show):
        show_dict = {"scan-result": []}

        play_id = self.generate_show_id(show.name, 0, "play-")
        play_button = {
            "name": "Play",
            "url": show.url,
            "id": play_id,
            "episodes": []
        }

        show_dict["scan-result"].append(play_button)
        
        for season in show.seasons:
            season_dict = self.parse_season(season)
            show_dict["scan-result"].append(season_dict)

        show_json = json.dumps(show_dict)
        return show_json

    def parse_open_app(self, show, show_name, app_id):            
        open_app_dict = {"opened-apps": [
            {
                "show": show,
                "show_name": show_name,
                "id": app_id
            }
        ]}

        open_app_json = json.dumps(open_app_dict)
        return open_app_json

class Wait_Until:
    def __init__(self, driver):
        self.driver = driver

        self.counter = 0
        self.sleep_time = 0.2
        self.sleep_max_count = 60

        self.is_xpath = False

    def wait_xpath(self, element, html=None, container=None):
        self.is_xpath = True
        self.wait(element, html, container)

    def wait_css(self, element, html=None,container=None):
        self.is_xpath = False
        self.wait(element, html, container)

    def get_element_information(self, container, element):
        selector = None
        if self.is_xpath:
            selector = container.find_element_by_xpath(element)
        else:
            selector = container.find_element_by_css_selector(element)
        inner_html = selector.get_attribute('innerHTML')
            
        return inner_html

    def wait(self, element, html=None, container=None):
        self.counter = 0
        if container == None:
            container = self.driver
        while True:
            try:
                inner_html = self.get_element_information(container, element)
                
                if self.counter == self.sleep_max_count:
                    break

                if html == None:
                    # Inner HTML is not empty, then break, it has loaded
                    if inner_html != "":
                        break
                elif inner_html == html:
                    # If the innerHTML has the requested content, break
                    break
                else:
                    self.sleep()
            except exceptions.NoSuchElementException:
                if self.counter == self.sleep_max_count:
                    break

                self.sleep()
            except exceptions.StaleElementReferenceException:
                if self.counter == self.sleep_max_count:
                    break

                self.sleep()

    def sleep(self):
        time.sleep(self.sleep_time)
        self.counter += 1

    def wait_different_xpath(self, element, html, container=None):
        self.is_xpath = True
        self.wait_different(element, html, container)

    def wait_different_css(self, element, html, container=None):
        self.is_xpath = False
        self.wait_different(element, html, container)

    def wait_different(self, element, html, container=None):
        self.counter = 0
        if container == None:
            container = self.driver
        while True:
            try:
                inner_html = self.get_element_information(container, element)
                
                if self.counter == self.sleep_max_count:
                    break

                if inner_html != html:
                    # If the innerHTML is different from the requested content, break
                    break
                else:
                    self.sleep()
            except exceptions.NoSuchElementException:
                if self.counter == self.sleep_max_count:
                    break

                self.sleep()
            except exceptions.StaleElementReferenceException:
                if self.counter == self.sleep_max_count:
                    break

                self.sleep()

# START SEQUENCE
def start():
    server.start()

def start_frontend():
    load_apps()
    load_opened_apps()
    load_scan_results()

def load_apps():
    apps_file = open('services/services.json', 'r')
    apps = apps_file.read()
    server.emit('apps', apps)

def load_opened_apps():
    global opened_apps

    for opened_app in opened_apps:
        opened_app.created_open_app = False
        opened_app.render_opened_app()

def load_scan_results():
    global active_app
    if active_app != None:
        if len(active_app.shows) > 0:
            active_app.last_show_parsed = 0
            active_app.render_shows()

def start_offline():
    server.start_offline()

# APPS INIT SEQUENCE
def generate_id_identifier(prefix):
    global opened_apps

    identifier = random.randint(0, 1000000)
    id_ = prefix + '-' + str(identifier)

    exists = False
    for app in opened_apps:
        if app.id_ == id_:
            exists = True
            break

    if exists:
        id_ = generate_id_identifier(prefix)
    
    return id_

def start_show(name, url):
    global active_app

    if active_app != None:
        active_app.start_show(name, url)
    else:
        print(len(opened_apps))
        server.raise_not("There is no opened app at the moment.")
    

def start_driver():
    global driver
    global chrome_options

    driver = webdriver.Chrome(executable_path=config.driver_path, chrome_options=chrome_options)
    driver.execute_script("window.open('about:blank');")
    windows_handles = driver.window_handles
    window_handles = driver.window_handles[len(windows_handles) - 1]
    driver.switch_to_window(window_handles)

def create_app_environment():
    global driver

    driver.execute_script("window.open('about:blank');")

    windows_handles = driver.window_handles
    window_handles = driver.window_handles[len(windows_handles) - 1]

    driver.switch_to_window(window_handles)

    return window_handles



def start_app(app_id, use_default_url):
    global opened_apps
    global active_app
    global driver
    global chrome_options
    
    if driver == None:
        start_driver()

    windows_handles = driver.window_handles
    window_handles = driver.window_handles[len(windows_handles) - 1]
    
    if active_app != None:
        window_handles = create_app_environment()

    if app_id == "netflix":
        netflix = Netflix(driver, window_handles)
        netflix.id_ = generate_id_identifier(netflix.id_)
        opened_apps.append(netflix)

        active_app = netflix
    
    app = opened_apps[len(opened_apps) - 1]
    if use_default_url:
        app.get(app.url)

    return app

def focus_app(app_id, delete_requested):
    global opened_apps
    global active_app
    global driver

    try:
        focused_app = None
        focused_app_position = 0
        for i, open_app in enumerate(opened_apps):
            if open_app.id_ == app_id:
                driver.switch_to_window(open_app.window_handles)
                focused_app = open_app
                focused_app_position = i
                break

        active_app = focused_app

        if not delete_requested:
            active_app.last_show_parsed = 0
            active_app.render_shows()

        return focused_app, focused_app_position
    except exceptions.NoSuchWindowException:
        return None, None

def close_app(app_id):
    global opened_apps
    global active_app
    global driver

    focused_app, i = focus_app(app_id, True)
    if focused_app != None and i != None:
        focused_app.driver.execute_script("window.close();")

        if focused_app == active_app:
            active_app = None

        opened_apps.pop(i)
        if len(opened_apps) == 0:
            driver.quit()
            driver = None

def start_app_search(app_id, search_url):
    app = start_app(app_id, False)
    app.get(search_url)


def test():
    start_app("netflix")

    netflix = opened_apps[0]
    netflix.start_show("Rick and Morty", "some-url")