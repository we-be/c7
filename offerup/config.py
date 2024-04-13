from dataclasses import dataclass
from typing import Self
import os

from pyOfferUp import places

places.places_dict['South Carolina']['cities']['Bluffton'] = {'lat': 32.237148, 'lon': -80.860390}


@dataclass
class Config:
    """Probably want to load this from a config file/app long-term"""
    DEBUG = True
    valid_iphone_models: list[str]
    location: tuple[str, str]
    listing_limit: int
    chrome_data_path: str

    @classmethod
    def default(cls) -> Self:
        assert isinstance(Config.DEBUG, bool)
        return cls._default() if not cls.DEBUG else cls._test()

    @classmethod
    def _default(cls) -> Self:
        return cls(
            valid_iphone_models=["iphone 11", "iphone 12", "iphone 13", "iphone 14", "iphone 15"],
            location=("Atlanta", "Georgia"),
            listing_limit=100,
            chrome_data_path=f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
        )

    @classmethod
    def _test(cls) -> Self:
        return cls(
            valid_iphone_models=["totallylegit"],
            location=("Bluffton", "South Carolina"),
            listing_limit=10,
            chrome_data_path=f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data"
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
