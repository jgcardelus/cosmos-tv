from libs import Path
import os
import random
import json
import time
import pynput
import unidecode

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions

from threading import Thread
from subprocess import call

import config
import server
import actuators

# SERVICES IMPORTS
from services.netflix import Netflix
from services.youtube import Youtube
from services.prime_video import Prime_Video

## FRAMEWORK VARIABLES
# DEFINE DRIVER
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--user-data-dir=' + config.data_dir_path)

driver = None

# KEYBOARD AND MOUSE CONTROL
m_button = pynput.mouse.Button
mouse = pynput.mouse.Controller()
k_key = pynput.keyboard.Key
keyboard = pynput.keyboard.Controller()

ctrl_state = False
alt_state = False

# MEDIA VARS
tick_thread = None
tick_pause_requested = False

opened_apps = []
active_app = None
volume = 50
last_volume = 50
is_mute = False

# PARSE
class Parser:
    def __init__(self):
        self.unwanted_chars = "¿?.!·$%&/()='`*;:-|@#~½¬{[]}[─·̣ ,\\<>"

    def clean_text(self, raw_text):
        text = ""
        raw_text = unidecode.unidecode(raw_text)
        for letter in raw_text:
            if letter not in self.unwanted_chars:
                text += letter

        return text

    def generate_show_id(self, name, i, prefix=None):
        show_id = ""

        if prefix != None:
            show_id = prefix
        
        raw_name_chunks = name.lower().split(' ')
        name_chunks = []
        for i in range(len(raw_name_chunks)):
            name_chunks.append(self.clean_text(raw_name_chunks[i]))

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
                "show-name": show_name,
                "id": app_id
            }
        ]}

        open_app_json = json.dumps(open_app_dict)
        return open_app_json

    def parse_season_episode_info(self, raw_season, raw_episode):
        info = '<b>S</b>'
        season = raw_season
        if len(raw_season) == 1:
            season = '0' + raw_season
        info += season + '<b>E</b>'
        episode = raw_episode
        if len(raw_episode) == 1:
            episode = '0' + raw_episode
        info += episode

        return info

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
    start_tick()
    server.start()

def tick():
    global active_app
    global tick_pause_requested

    while True:
        try:
            if not tick_pause_requested:
                if active_app != None:
                    active_app.get_media_information()

            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    
    tick_pause_requested = False

def start_tick():
    global tick_pause_requested
    global tick_thread

    if tick_thread == None:
        tick_thread = Thread(target=tick)

    if not tick_thread.isAlive():
        tick_thread.start()


def pause_tick():
    global tick_pause_requested
    tick_pause_requested = True

def resume_tick():
    global tick_pause_requested
    tick_pause_requested = False

def start_frontend():
    load_apps()
    load_opened_apps()
    load_scan_results()
    load_session_info()

def load_apps():
    apps_path = Path('services/services.json').path
    apps_file = open(apps_path, 'r')
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
            active_app.render_scan()

def load_session_info():
    global active_app
    if active_app != None:
        active_app.load_session()

    set_volume_val()

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
    driver.execute_script("open('about:blank');")
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
    
    #Stop tick
    pause_tick()
    
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
    elif app_id == "youtube":
        youtube = Youtube(driver, window_handles)
        youtube.id_ = generate_id_identifier(youtube.id_)
        opened_apps.append(youtube)

        active_app = youtube
    elif app_id == "prime-video":
        prime_video = Prime_Video(driver, window_handles)
        prime_video.id_ = generate_id_identifier(prime_video.id_)
        opened_apps.append(prime_video)

        active_app = prime_video


    app = opened_apps[len(opened_apps) - 1]
    if use_default_url:
        app.get(app.url)

    #Resume tick
    resume_tick()
    return app

def focus_app(app_id, delete_requested):
    global opened_apps
    global active_app
    global driver

    #Stop tick
    pause_tick()

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
        active_app.load_session()

        if not delete_requested:
            active_app.last_show_parsed = 0
            active_app.render_scan()

        resume_tick()

        return focused_app, focused_app_position
    except exceptions.NoSuchWindowException:
        resume_tick()
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

# MEDIA CONTROL
def skip():
    if active_app != None:
        active_app.skip()

def fullscreen():
    if active_app != None:
        active_app.fullscreen()

def play():
    if active_app != None:
        active_app.play()

def next_show():
    if active_app != None:
        active_app.next_show()

def forwards():
    if active_app != None:
        active_app.forwards()

def backwards():
    if active_app != None:
        active_app.backwards()


#SOUND OPTIONS
def set_mute():
    global volume
    global last_volume

    try:
        if volume != 0:
            #Save values
            last_volume = volume
            volume = 0
        else:
            #Save values
            volume = last_volume

        call(["amixer", "-D", "pulse", "sset", "Master", str(volume)+"%"])
        set_volume_val()
    except ValueError:
        pass

def set_volume(val):
    global volume
    try:
        volume = val
        if (volume <= 100) and (volume >= 0):
            call(["amixer", "-D", "pulse", "sset", "Master", str(volume)+"%"])
    except ValueError:
        pass

def set_volume_val():
    global volume
    server.emit('volume', volume)

# CONTROL PAD
moving_mouse = False
def mouse_canvas_move(raw_coordinates):
    global mouse
    global moving_mouse

    moving_mouse = True
    raw_chunks = raw_coordinates.split('/')

    for raw_xy in raw_chunks:
        xy_chunks = raw_xy.split(':')
        x = int(xy_chunks[0])
        y = int(xy_chunks[1])

        try:
            mouse.move(x, y)
            time.sleep(0.02)
        except RuntimeError:
            mouse = pynput.mouse.Controller()

    moving_mouse = False
        

def mouse_move(x,y):
    mouse.move(x,y)

def mouse_left():
    mouse.click(m_button.left)

def mouse_right():
    mouse.click(m_button.right)

def key_pressed(key):
    global ctrl_state
    global alt_state
    global keyboard

    try:
        if key == 'enter':
            press_enter()
        elif key == 'space':
            press_space()
        elif key == 'delete':
            press_delete()
        else:
            special_key = key.split(',')
            if len(special_key) <= 1:
                press_letter(key)
            else:
                type_ = special_key[0]
                state = get_state(special_key[1])

                if type_ == 'ctrl':
                    ctrl_state = state
                elif type_ == 'alt':
                    alt_state = state

    except RuntimeError:
        keyboard = pynput.keyboard.Controller()

def get_state(text):
    state = False
    if text.lower() == 'true':
        state = True

    return state

def press_enter():
    keyboard.press(k_key.enter)
    keyboard.release(k_key.enter)

def press_delete():
    keyboard.press(k_key.backspace)
    keyboard.release(k_key.backspace)

def press_space():
    keyboard.press(k_key.space)
    keyboard.release(k_key.space)

def press_letter(letter):
    global ctrl_state
    global alt_state

    if ctrl_state:
        with keyboard.pressed(k_key.ctrl):
            keyboard.press(letter)
            keyboard.release(letter)
    elif alt_state:
        with keyboard.pressed(k_key.alt):
            keyboard.press(letter)
            keyboard.release(letter)
    elif ctrl_state and alt_state:
        with keyboard.pressed(k_key.alt) and keyboard.pressed(k_key.ctrl):
            keyboard.press(letter)
            keyboard.release(letter)
    else:
        keyboard.press(letter)
        keyboard.release(letter)

def scroll(x, y):
    mouse.scroll(x, y)