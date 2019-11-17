import random
import json
import time

from selenium.common import exceptions

import config
import server
import actuators

# SERVICES IMPORTS
from services.netflix import Netflix

## FRAMEOWRK VARIABLES
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
        self.sleep_max_count = 250

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

def load_apps():
    apps_file = open('services/services.json', 'r')
    apps = apps_file.read()
    server.emit('apps', apps)
    
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
    

def start_app(app_id):
    global opened_apps
    global active_app

    if app_id == "netflix":
        netflix = Netflix()
        netflix.id_ = generate_id_identifier(netflix.id_)
        opened_apps.append(netflix)

        active_app = netflix
        if active_app != None:
            print("There is an active app")
        netflix.start()

def close_app(app_id):
    global opened_apps

    for i, open_app in enumerate(opened_apps):
        if open_app.id_ == app_id:
            open_app.close()
            opened_apps.pop(i)
            break

def start_app_search(app_id, search_url):
    print(app_id, search_url)


def test():
    start_app("netflix")

    netflix = opened_apps[0]
    netflix.start_show("Rick and Morty", "some-url")