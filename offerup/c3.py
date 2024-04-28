import dataclasses
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


@dataclass
class Convo:
    id: str
    itemType: str
    messages: list[Message]

    @classmethod
    def new(cls, _id: str, opener: str, item_type: str):
        opener_content = MessageContent(None, opener)
        opener_msg = Message(MessageRole.User, opener_content)
        return cls(_id, item_type, [opener_msg])


class C3:
    """A cosmos conversation container"""
    def __init__(self, db: str, container: str):
        self.client: CosmosClient = CosmosClient(*cfg.cosmos_creds())
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.container: ContainerProxy = self.db.get_container_client(container)

    def new(self, convo: Convo):
        # TODO except exceptions.CosmosResourceExistsError
        d3 = dataclasses.asdict(convo)
        self.container.create_item(d3)


if __name__ == '__main__':
    c1 = C3('conversations', 'offerup')
    c2 = Convo("test-id", "test item", [])
    c1.new(c2)
