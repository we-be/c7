from typing import Optional

import azure.cosmos
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy

from config import Config


class Cosmos:
    """A cosmos container"""
    def __init__(self, cfg: Optional[Config], client: Optional[CosmosClient], db: str, container: str):
        self.cfg: Config = cfg or Config.default()
        self.client: CosmosClient = client or CosmosClient(*cfg.cosmos_creds())
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.container: ContainerProxy = self.db.get_container_client(container)


class Conversation:
    """Class for storing and retrieving conversation data in Cosmos"""
    def __init__(self, cfg: Optional[Config], cosmos: Optional[Cosmos]):
        self.cfg: Config = cfg or Config.default()
        self.cosmos: Cosmos = cosmos or Cosmos(self.cfg, cosmos, 'conversations', 'offerup')


if __name__ == '__main__':
    convo = Conversation(None, None)
    print(convo)
