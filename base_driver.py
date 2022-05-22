from selenium import webdriver


class Driver():
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)  # seconds
        self.driver.maximize_window()
        self.driver.get(url)


