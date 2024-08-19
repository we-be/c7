from dataclasses import dataclass
from typing import Self
import os
import platform

from dotenv import load_dotenv


PHONES = list(reversed(["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"]))
MODELS = list(reversed(["Pro", "ProMax", "Reg", "Plus", ""]))
if platform.system() == 'Windows':
    CHROME_DATA_PATH = f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
else:
    CHROME_DATA_PATH = f"user-data-dir={os.path.expanduser('~')}/.config/google-chrome"

if platform.system() == 'Windows':
    raise OSError("Windows Firefox webdriver not supported")
else:
    FIREFOX_DATA_PATH = f"{os.path.expanduser('~')}/snap/firefox/common/.mozilla/firefox/cd3jw6g1.default"
    FIREFOX_BINARY_PATH = '/snap/firefox/4259/usr/lib/firefox/firefox'


@dataclass
class Config:
    """Probably want to load this from a config file/app long-term"""
    loaded = False  # dotenv loaded

    valid_iphone_models: list[str]
    location: tuple[str, str]
    listing_limit: int

    chrome_data_path = CHROME_DATA_PATH
    firefox_data_path = FIREFOX_DATA_PATH
    firefox_binary_path = FIREFOX_BINARY_PATH

    @classmethod
    def default(cls, load=True, debug=False, **kwargs) -> Self:
        _cfg = cls._default() if not debug else cls._test()
        if load:
            _cfg.load(**kwargs)
        return _cfg

    def load(self, **kwargs) -> None:
        """Load the .env file"""
        self.loaded = True
        load_dotenv(**kwargs)

    def __getitem__(self, item):
        return os.environ[item]

    @classmethod
    def _default(cls) -> Self:
        return cls(
            valid_iphone_models=PHONES,
            valid_iphone_size=MODELS,
            location=("Atlanta", "Georgia"),
            listing_limit=30,
        )

    @classmethod
    def _test(cls) -> Self:
        print('Using test configuration')
        return cls(
            # valid_iphone_models=["Gamer Guy Bath water"],
            valid_iphone_models=PHONES,
            valid_iphone_size=MODELS,
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

    @property
    def cosmos_creds(self) -> tuple[str, dict[str, str]]:
        """Azure cosmos connection credentials to be passed into a CosmosClient
        like `azure.cosmos.CosmosClient(*config.cosmos_creds())`"""
        url = self["COSMOS_URI"]
        key = {"masterKey": self["COSMOS_KEY"]}
        return url, key

    @property
    def anthropic_key(self) -> str:
        return self["ANTHROPIC_KEY"]


cfg = Config.default()  # global config
