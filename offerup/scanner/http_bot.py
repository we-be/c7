from offerup.scanner.bot import Bot
from c3 import C3, Convo, Status
from offerup.config import cfg


class GraphQLBot(Bot):
    def __init__(self):
        self.c3 = C3('conversations', 'offerup')  # cosmos conversation container
        
    def scan(self):
        pass
    
    def login(self) -> bool:
        """returns a boolean to indicate of the login was successful"""
        pass


if __name__ == "__main__":
    bot = GraphQLBot()
    print('logmeincheif')
    bot.login()    
