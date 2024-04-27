from enum import Enum
from typing import Optional
from dataclasses import dataclass

from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy

from offerup.config import cfg


class MessageRole(Enum):
    User = "User"
    Assistant = "Assistant"


@dataclass
class MessageContent:
    type: Optional[str]
    content: str


@dataclass
class Message:
    role: MessageRole
    content: MessageContent


class C3:
    """A cosmos conversation container"""
    def __init__(self, db: str, container: str):
        self.client: CosmosClient = CosmosClient(*cfg.cosmos_creds())
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.container: ContainerProxy = self.db.get_container_client(container)

    def new(self, listing: dict, search_term: str):
        pass


if __name__ == '__main__':
    c = C3('conversations', 'offerup')
    print(c)
