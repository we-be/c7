from enum import Enum
from typing import Optional
from dataclasses import dataclass

from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy

from config import Config


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


class Cosmos:
    """A cosmos container"""
    def __init__(self, cfg: Optional[Config], client: Optional[CosmosClient], db: str, container: str):
        self.cfg: Config = cfg or Config.default()
        self.client: CosmosClient = client or CosmosClient(*self.cfg.cosmos_creds())
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.container: ContainerProxy = self.db.get_container_client(container)


class Conversation:
    """Class for storing and retrieving conversation data in Cosmos"""
    def __init__(self, cfg: Optional[Config] = None,
                 cosmos: Optional[Cosmos] = None,
                 convo_id: Optional[str] = None):
        self.cfg: Config = cfg or Config.default()
        self.cosmos: Cosmos = cosmos or Cosmos(self.cfg, cosmos, 'conversations', 'offerup')

        self.id: str = convo_id or self.start_convo()
        self.messages: list[Message] = [] if not convo_id else self.load_messages(convo_id)

    def start_convo(self) -> str:
        pass

    def load_messages(self, convo_id: str) -> list[Message]:
        pass


if __name__ == '__main__':
    convo = Conversation()
    print(convo)
