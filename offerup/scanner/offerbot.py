import time

from selenium import webdriver
from pyOfferUp import fetch
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from offerup.config import cfg

# Small window (ask button in footer)
ASK_XPATH_FOOTER = '/html/body/div[1]/div[5]/footer/div/div[3]/div/div/div[1]'

# Full window - Work on coaxing the correct path
ASK_XPATH = '/html/body/div[1]/div[5]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[2]/div[2]/div[1]/button'
# ASK_XPATH = '/html/body/div[1]/div[5]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[2]/div[2]'
CHAT_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
# CHAT_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/div/div/div[2]/div'
NEW_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
# NEW_MSG_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
SEND_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/button'
# SEND_MSG_XPATH = '/html/body/div[3]/div[3]/div/div[3]/form/button'


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self):
        self.driver = _init_chromedriver()

    def scan(self):
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                url = listing["listingUrl"]
                self.driver.get(url)

                # maybe add WebDriverWait here
                try:
                    elem = self.driver.find_element(By.XPATH, ASK_XPATH)
                except NoSuchElementException:
                    elem = self.driver.find_element(By.XPATH, ASK_XPATH_FOOTER)
                elem.click()

                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located((By.XPATH, CHAT_XPATH))
                    ).click()
                except TimeoutException:
                    time.sleep(30)  # TODO CHECK FOR 'inbox' in URL BEFORE THIS OR HERE OR JUST ASSUME AND MESSAGE

                msg_txt = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.XPATH, NEW_MSG_XPATH))
                )
                msg_txt.send_keys('Hello! Is this still available?')
                self.driver.find_element(By.XPATH, SEND_MSG_XPATH).click()
                time.sleep(1000)

    @staticmethod
    def get_listings() -> dict[str, list[dict]]:
        all_listings = {}
        for model in cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=cfg.state, city=cfg.city,
                                                     limit=cfg.listing_limit)
        return all_listings


def _init_chromedriver():
    chrome_options = Options()
    chrome_options.add_argument(cfg.chrome_data_path)
    return webdriver.Chrome(options=chrome_options)


if __name__ == '__main__':
    bot = OfferBot()
    bot.scan()
