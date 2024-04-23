from dataclasses import dataclass
from typing import Self
import os
import platform

from pyOfferUp import places
from dotenv import load_dotenv

places.places_dict['South Carolina']['cities']['Bluffton'] = {'lat': 32.237148, 'lon': -80.860390}

if platform.system() == 'Windows':
    CHROME_DATA_PATH = f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
else:
    CHROME_DATA_PATH = f"user-data-dir={os.path.expanduser('~')}/.config/google-chrome"


@dataclass
class Config:
    """Probably want to load this from a config file/app long-term"""
    DEBUG = True
    loaded = False  # dotenv loaded

    valid_iphone_models: list[str]
    location: tuple[str, str]
    listing_limit: int
    chrome_data_path = CHROME_DATA_PATH

    @classmethod
    def default(cls, load=True, **kwargs) -> Self:
        _cfg = cls._default() if not cls.DEBUG else cls._test()
        if load:
            _cfg.load(**kwargs)
        return _cfg

    def load(self, **kwargs) -> None:
        """Load the .env file"""
        self.loaded = True
        load_dotenv(**kwargs)

    @classmethod
    def _default(cls) -> Self:
        return cls(
            valid_iphone_models=["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"],
            location=("Atlanta", "Georgia"),
            listing_limit=100,
        )

    @classmethod
    def _test(cls) -> Self:
        print('Using test configuration')
        return cls(
            valid_iphone_models=["Gamer Guy Bath water"],
            location=("Atlanta", "Georgia"),
            listing_limit=10,
        )

    @property
    def city(self) -> str:
        """City that the bot is operating in"""
        if not isinstance(self.location[0], str):
            raise AttributeError("`city` must be a string, location should be of form (city, state)")
        return self.location[0]

    @property
    def state(self) -> str:
        """US State that the bot is operating in"""
        if not isinstance(self.location[1], str):
            raise AttributeError("`state` must be a string, location should be of form (city, state)")
        return self.location[1]

    @staticmethod
    def cosmos_creds() -> tuple[str, dict[str, str]]:
        """Azure cosmos connection credentials to be passed into a CosmosClient
        like `azure.cosmos.CosmosClient(*config.cosmos_creds())`"""
        url = os.getenv("COSMOS_URI")
        key = {"masterKey": os.getenv("COSMOS_KEY")}
        return url, key


cfg = Config.default()  # global config
