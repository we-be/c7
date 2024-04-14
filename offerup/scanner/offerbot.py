import time
from typing import Optional

from selenium import webdriver
from pyOfferUp import fetch
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from offerup.config import Config

ASK_XPATH = '/html/body/div[1]/div[5]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[2]/div[2]'
CHAT_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/div/div/div[2]/div'
NEW_MSG_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
SEND_MSG_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/button'


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self, cfg: Optional[Config]):
        self.cfg = cfg or Config.default()
        self.driver = _init_chromedriver(self.cfg)

    def scan(self):
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                url = listing["listingUrl"]
                self.driver.get(url)

                self.driver.find_element(By.XPATH, ASK_XPATH).click()

                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, CHAT_XPATH))
                ).click()

                msg_txt = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, NEW_MSG_XPATH))
                )
                msg_txt.send_keys('Hello! Is this still available?')
                self.driver.find_element(By.XPATH, SEND_MSG_XPATH).click()
                time.sleep(1000)

    def get_listings(self) -> dict[str, list[dict]]:
        all_listings = {}
        for model in self.cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=self.cfg.state, city=self.cfg.city,
                                                     limit=self.cfg.listing_limit)
        return all_listings


def _init_chromedriver(cfg: Config):
    chrome_options = Options()
    chrome_options.add_argument(cfg.chrome_data_path)
    return webdriver.Chrome(options=chrome_options)
