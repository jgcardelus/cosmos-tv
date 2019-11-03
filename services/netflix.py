from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import server
import config

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
        self.show_name = None
        self.episode = None
        self.season = None

    def start(self):
        self.driver = webdriver.Chrome(executable_path=config.driver_path, chrome_options=config.chrome_options)
        self.driver.get(self.url)

    def focus(self):
        self.driver.maximize_window()
       
    def close(self):
        self.driver.quit()



