from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pyOfferUp import fetch

from offerup.c3 import C3, Convo
from offerup.config import cfg

OPENER = 'Hello! Is this still available?'  # how we start the convos

# Full window - Work on coaxing the correct path
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

                # Locate and click the 'Ask' button
                self.ask()

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


def _init_chromedriver():
    chrome_options = Options()
    chrome_options.add_argument(cfg.chrome_data_path)
    return webdriver.Chrome(options=chrome_options)


if __name__ == '__main__':
    bot = OfferBot()
    bot.scan()
    bot.driver.quit()
