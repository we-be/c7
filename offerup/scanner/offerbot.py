import time

from selenium import webdriver
from pyOfferUp import fetch
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from offerup.c3 import C3, Convo
from offerup.config import cfg

OPENER = 'Hello! Is this still available?'  # how we start the convos

# Full window - Work on coaxing the correct path
ASK_XPATH = '/html/body/div[1]/div[5]/div[2]/main/div[1]/div/div[1]/div/div[3]/div[2]/div[2]/div[1]/button'
ASK_XPATH_FOOTER = '/html/body/div[1]/div[5]/footer/div/div[3]/div/div/div[1]'  # Small window (ask button in footer)
CHAT_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
NEW_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
SEND_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/button'


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self):
        self.driver = _init_chromedriver()
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container

    def scan(self):
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                # open the listing
                self.driver.get(listing["listingUrl"])

                # maybe add WebDriverWait here
                # click the `Ask` button, it could be in the footer if the window is small enough
                try:
                    elem = self.driver.find_element(By.XPATH, ASK_XPATH)
                except NoSuchElementException:
                    elem = self.driver.find_element(By.XPATH, ASK_XPATH_FOOTER)
                elem.click()

                # wait until we see the chat modal or redirect to the inbox
                wait = WebDriverWait(self.driver, timeout=2, poll_frequency=.2)
                wait.until(lambda d: ('inbox' in self.driver.current_url) or
                           self.driver.find_element(By.XPATH, CHAT_XPATH))

                # if we're in the inbox it means we've already messaged this seller
                if 'inbox' in self.driver.current_url:
                    print("Message already sent for this item", listing["listingId"])
                    continue  # we could check the inbox here to see if we have a message - if so, notify Claude

                # initiate a new conversation
                self.driver.find_element(By.XPATH, CHAT_XPATH).click()
                WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.XPATH, NEW_MSG_XPATH))
                ).send_keys(OPENER)
                # self.driver.find_element(By.XPATH, SEND_MSG_XPATH).click()

                # save the convo with c3
                convo = Convo.new(listing["listingId"], model, OPENER)
                self.c3.new(convo)
                print('done', listing["listingId"])

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
