import os
import platform
from libs import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DEBUG = True
port = 8080

# Defualt settings
chromedriver_name = "chromedriver"

data_dir_path = Path('/home/jgcardelus/Desktop/coding-projects/cosmos-tv-settings/chrome-preferences').path
settings_path = Path('/home/jgcardelus/Desktop/coding-projects/cosmos-tv-settings/settings.json').path

system = platform.system()
if system == "Windows":
    chromedriver_name = "chromedriver.exe"
    data_dir_path = Path("C:\\Users/jgcar/Desktop/Coding/AAA_MixedProjects/cosmos-tv-settings").path
    settings_path = Path("C:\\Users/jgcar/Desktop/Coding/AAA_MixedProjects/cosmos-tv-settings/settings.json").path


# SELENIUM DRIVER
driver_path = os.path.join(os.getcwd(), 'chrome-driver', chromedriver_name)