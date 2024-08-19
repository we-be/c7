import json
from typing import Optional, Literal
from urllib.parse import urlencode

from redis import Redis
import requests
from pyOfferUp import fetch

from offerup.scanner.bot import Bot
from offerup.scanner.headers import HTTPHeaders
from offerup.config import cfg, PHONES
from c3 import C3, Convo, Status


TEMP_QUERY = 'iphone 15'
TEMP_NUM_LISTINGS = 1  # will remove this when done testing


class GraphQLBot(Bot):
    def __init__(self):
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container
        self.redis = Redis()
        
        self.headers = HTTPHeaders.from_redis(self.redis, 'offerup')
        self.graphql_url = 'https://offerup.com/api/graphql'
        
    def scan(self):
        for listing in self.get_model_listings(TEMP_QUERY)[:TEMP_NUM_LISTINGS]:
            
            # check to see if we already have an entry for this device
            listing_id = listing['listingId']
            stored_listing = self.c3.get(listing_id)
            if stored_listing:
                print('we already have an entry for this phone, will implement message logic here')
                continue
            
            # start the conversation
            print('nothing yet stored for', listing_id, 'initiating convo...')
            resp = self.get_listing_by_id(listing_id)
            _id = resp['data']['listing']['id']  # this is an integer, different than `listingId`
    
    def login(self) -> bool:
        """returns a boolean to indicate of the login was successful"""
        pass

    def get_listing_by_id(self, listing_id: str) -> dict:
        headers = self.headers.to_dict()
        headers.update({
            'Content-Type': 'application/json',
            'x-ou-operation-name': 'GetListingDetailByListingId',
        })

        payload = {
            "operationName": "GetListingDetailByListingId",
            "variables": {
                "listingId": listing_id
            },
            "query": """
            query GetListingDetailByListingId($listingId: ID!) {
              listing(listingId: $listingId) {
                id
                title
                description
                price
                condition
                photos {
                  uuid
                  detail {
                    url
                    width
                    height
                  }
                }
                owner {
                  profile {
                    name
                  }
                }
                locationDetails {
                  locationName
                }
              }
            }
            """
        }

        response = requests.post(self.graphql_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
        
    def start_chat(self, listing_id: str, text: str, suggested_message_uuid: Optional[str] = None) -> Optional[str]:
        headers = {
            'Content-Type': 'application/json',
            'x-ou-operation-name': 'StartChat',
            # Add other necessary headers from self.headers if needed
        }

        payload = {
            "operationName": "StartChat",
            "variables": {
                "listingId": listing_id,
                "text": text,
                "suggestedMessageUuid": suggested_message_uuid
            },
            "query": """
            mutation StartChat($listingId: ID!, $text: String!, $suggestedMessageUuid: String) {
              postFirstMessage(
                data: {itemId: $listingId, text: $text, suggestedMessageUuid: $suggestedMessageUuid}
              ) {
                id: discussionId
                __typename
              }
            }
            """
        }

        try:
            response = requests.post(self.graphql_url, headers=headers, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            data = response.json()
            if 'data' in data and 'postFirstMessage' in data['data']:
                return data['data']['postFirstMessage']['id']
            else:
                print("Unexpected response structure:", data)
                return None
        except requests.RequestException as e:
            print(f"Error starting chat: {e}")
            return None
        
    def get_price(self, model: Literal['iphone 15', 'iphone 14', 'iphone 13', 'iphone 12', 'iphone 11', 'iphone x', 'iphone xs', 'iphone xr'],
                unlocked: bool = True,
                grade: Literal['swap', 'a', 'b', 'c', 'd', 'doa'] = 'b',
                storage: Literal['64gb', '128gb', '256gb', '512gb'] = '128gb') -> Optional[float]:
        """
        Get the price for a specific iPhone model using the pricing API.
        
        :param model: The iPhone model
        :param unlocked: Whether the phone is unlocked or not
        :param grade: The condition grade of the phone
        :param storage: The storage capacity of the phone
        :return: The price as a float, or None if the request fails
        """
        params = {
            'unlocked': 'true' if unlocked else 'false',
            'grade': grade,
            'storage': storage
        }
        
        url = f"{cfg['PRICING_API_URL']}/api/iphone-used/{model}?{urlencode(params)}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return float(response.text[1:]) - 100  # response includes dollar sign, like "$490"
        except requests.RequestException as e:
            print(f"Error fetching price: {e}")
            return None



if __name__ == "__main__":
    bot = GraphQLBot()
    p = bot.get_price('iphone 15'); print(p)
