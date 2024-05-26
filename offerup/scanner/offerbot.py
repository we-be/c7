from typing import Literal

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pyOfferUp import fetch

from offerup.c3 import C3, Convo, Status
from offerup.config import cfg

CHAT_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
NEW_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/div/div/div[2]/div/textarea'
SEND_MSG_XPATH = '/html/body/div[4]/div[3]/div/div[3]/form/button'


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self, browser: Literal['chrome', 'firefox']):
        self.driver = _init_webdriver(browser)
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container

    def scan(self):
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                # open the listing
                self.driver.get(listing["listingUrl"])

                # Locate and click the 'Ask' button
                self.ask()

                # wait until we see the chat modal or redirect to the inbox
                # if the code fails here, we're probably not logged in
                wait = WebDriverWait(self.driver, timeout=10, poll_frequency=.2)
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
                )

                # save the convo with c3
                convo = Convo.new(listing["listingId"], model, Status.NEW)
                self.c3.new(convo)
                print('done', listing["listingId"])

    def ask(self) -> None:
        """From a listing page, find and click the 'Ask' button"""
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.text == "Ask":
                return button.click()
        else:
            raise NoSuchElementException("Could not find ask button.")

    @staticmethod
    def get_listings() -> dict[str, list[dict]]:
        all_listings = {}
        for model in cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=cfg.state, city=cfg.city,
                                                     limit=cfg.listing_limit)
        return all_listings


def _init_webdriver(browser: Literal['chrome', 'firefox']):
    if browser.lower() == 'chrome':
        chrome_options = ChromeOptions()
        chrome_options.add_argument(cfg.chrome_data_path)
        return webdriver.Chrome(options=chrome_options)
    elif browser.lower() == 'firefox':
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("-profile")
        firefox_options.add_argument(cfg.firefox_data_path)
        firefox_options.binary_location = cfg.firefox_binary_path
        return webdriver.Firefox(options=firefox_options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")


if __name__ == '__main__':
    bot = OfferBot('chrome')
    bot.scan()
    bot.driver.quit()
