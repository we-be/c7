import os
from dataclasses import dataclass
from typing import Self

from selenium import webdriver
from pyOfferUp import fetch
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Config:
    """Probably want to load this from a config file/app long-term"""
    valid_iphone_models: list[str]
    location: tuple[str, str]
    listing_limit: int

    @classmethod
    def default(cls) -> Self:
        return cls(
            valid_iphone_models=["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"],
            location=("Atlanta", "Georgia"),
            listing_limit=100,
        )

    @property
    def city(self) -> str:
        if not isinstance(self.location[0], str):
            raise AttributeError("`city` must be a string, location should be of form (city, state)")
        return self.location[0]

    @property
    def state(self) -> str:
        if not isinstance(self.location[1], str):
            raise AttributeError("`state` must be a string, location should be of form (city, state)")
        return self.location[1]


class OfferBot:
    """Ask questions and make offers"""
    def __init__(self, cfg: Config | None = None):
        self.cfg = cfg or Config.default()
        self.driver = self._init_chromedriver()

    @staticmethod
    def _init_chromedriver():
        chrome_options = Options()
        chrome_options.add_argument(
            f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data")
        return webdriver.Chrome(options=chrome_options)

    def wait_for_login(self, timeout=60):
        # Wait for the presence of an element that indicates successful login
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "your_login_success_selector"))
        )

    def scan(self):
        # self.wait_for_login()  # Wait for the user to log in
        listings = self.get_listings()
        for model in listings.keys():
            for listing in listings[model]:
                url = listing["listingUrl"]
                self.driver.get(url)

    def get_listings(self) -> dict[str, list[dict]]:
        all_listings = {}
        for model in self.cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=self.cfg.state, city=self.cfg.city,
                                                     limit=self.cfg.listing_limit)
        return all_listings


if __name__ == '__main__':
    bot = OfferBot()
    bot.scan()
