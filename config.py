import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DEBUG = True
port = 8080

# SELENIUM DRIVER
driver_path = os.path.join(os.getcwd(), 'chrome-driver', 'chromedriver')
# data_dir_path = os.path.join(os.getcwd(), 'chrome-driver', 'chrome-preferences')
data_dir_path = '/home/jgcardelus/Desktop/Coding_Projects/CosmosTv-Settings/chrome-preferences'
settings_path = '/home/jgcardelus/Desktop/Coding_Projects/CosmosTv-Settings/settings.json'