import time

from selenium import webdriver
from pyOfferUp import fetch
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from offerup.config import Config

ASK_XPATH = '/html/body/div[1]/div[5]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[2]/div[2]'


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self, cfg: Config | None = None):
        self.cfg = cfg or Config.default()  # this needs to be set before we called init chromedriver
        self.driver = self._init_chromedriver()

    def _init_chromedriver(self):
        chrome_options = Options()
        chrome_options.add_argument(self.cfg.chrome_data_path)
        return webdriver.Chrome(options=chrome_options)

    def scan(self):
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                url = listing["listingUrl"]
                self.driver.get(url)
                button = self.driver.find_element(By.XPATH, ASK_XPATH)
                button.click()
                time.sleep(1000)

    def get_listings(self) -> dict[str, list[dict]]:
        all_listings = {}
        for model in self.cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=self.cfg.state, city=self.cfg.city,
                                                     limit=self.cfg.listing_limit)
        return all_listings