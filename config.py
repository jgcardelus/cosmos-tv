import os
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DEBUG = True
port = 8080

chromedriver_name = "chromedriver"

data_dir_path = '/home/jgcardelus/Desktop/coding-projects/cosmos-tv-settings/chrome-preferences'
settings_path = '/home/jgcardelus/Desktop/coding-projects/cosmos-tv-settings/settings.json'

system = platform.system()
if platform == "Windows":
    chromedriver_name = "chromedriver.exe"
    data_dir_path = "C:/Users/jgcar/Desktop/Coding/AAA_MixedProjects/cosmos-tv-settings"
    settings_path = "C:/Users/jgcar/Desktop/Coding/AAA_MixedProjects/settings.json"


# SELENIUM DRIVER
driver_path = os.path.join(os.getcwd(), 'chrome-driver', chromedriver_name)