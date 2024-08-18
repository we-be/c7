import requests
from redis import Redis

from offerup.scanner.bot import Bot
from offerup.scanner.headers import HTTPHeaders
from c3 import C3, Convo, Status
from offerup.config import cfg

class GraphQLBot(Bot):
    def __init__(self):
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container
        self.redis = Redis()
        
        self.headers = HTTPHeaders.from_redis(self.redis, 'offerup')
        
    def scan(self):
        pass
    
    def login(self) -> bool:
        """returns a boolean to indicate of the login was successful"""
        pass
    
    def search(self, search_term: str):
        resp = requests.get(cfg.offerup_url + f'/search?q={search_term.replace(' ', '+')}', 
                            headers=self.headers.to_dict())
        with open('output.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)  # write response to file
        print(f'got {resp.status_code}')
        print(f'Response content written to output.html')

if __name__ == "__main__":
    bot = GraphQLBot()
    bot.get_listings()