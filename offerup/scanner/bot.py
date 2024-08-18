from abc import ABC, abstractmethod

from offerup.config import cfg

from pyOfferUp import fetch


class Bot(ABC):
    
    @abstractmethod
    def scan():
        pass
    
    @staticmethod
    def get_listings() -> dict[str, list[dict]]:
        all_listings = {}
        for model in cfg.valid_iphone_models:
            all_listings[model] = fetch.get_listings(query=model, state=cfg.state, city=cfg.city,
                                                     limit=cfg.listing_limit)
        return all_listings
