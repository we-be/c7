import requests
import json
from redis import Redis
from offerup.scanner.bot import Bot
from offerup.scanner.headers import HTTPHeaders
from offerup.config import cfg
from c3 import C3, Convo, Status


class GraphQLBot(Bot):
    def __init__(self):
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container
        self.redis = Redis()
        
        self.headers = HTTPHeaders.from_redis(self.redis, 'offerup')
        self.graphql_url = 'https://offerup.com/api/graphql'
        
    def scan(self):
        pass
    
    def login(self) -> bool:
        """returns a boolean to indicate of the login was successful"""
        pass
    
    def search(self, search_term: str):
        resp = requests.get(cfg.offerup_url + f'/search?q={search_term.replace(' ', '+')}', 
                            headers=self.headers.to_dict())
        with open('output.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print(f'got {resp.status_code}')
        print(f'Response content written to output.html')

    def get_listing_by_id(self, listing_id: str):
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
            print(f"Error: {response.status_code}")
            print(response.text)
            return None


if __name__ == "__main__":
    bot = GraphQLBot()
    listing_id = "210c8e23-a910-3ef5-b9d3-d2fc11b165e3"  # Example listing ID
    listing_details = bot.get_listing_by_id(listing_id)
    
    if listing_details:
        print(json.dumps(listing_details, indent=2))
    else:
        print("Failed to fetch listing details")
