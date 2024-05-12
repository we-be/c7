import dataclasses
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import json

from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey

from offerup.config import cfg


class MessageRole(str, Enum):
    User = "User"
    Assistant = "Assistant"


class Status(str, Enum):
    ACTIVE = "active"  # active conversation, they have responded at least once and we are awaiting response
    PENDING = "pending"  # active conversation, the seller was the last one to respond
    NEW = "new"  # We have messages the customer but have not received a response yet
    TEST = "test"  # We saved the message as for testing purposes, but likely didn't actually send anything
    STALE = "stale"  # Have not received a response from the customer in some time
    HI = "human intervention"  # needs triage by an authorized human being


GRADES = ["A", "B", "C", "D"]


@dataclass
class MessageContent:
    type: str
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
    status: Status
    grade: Optional[str] = None

    @classmethod
    def new(cls, _id: str, opener: str, item_type: str, status=Status.NEW):
        opener_content = MessageContent('text', opener)
        opener_msg = Message(MessageRole.User, opener_content)
        return cls(_id, item_type, [opener_msg], status)


class C3:
    """A cosmos conversation container"""
    def __init__(self, db: str, container: str):
        if db != 'conversations' or container != 'offerup':
            print('Warning: C3 starting with nonstandard db and/or container:', db, container)

        self.client: CosmosClient = CosmosClient(*cfg.cosmos_creds)
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.partition_key = PartitionKey(path="/status")
        self.container: ContainerProxy = self.db.create_container_if_not_exists(container, self.partition_key)

    def new(self, convo: Convo):
        # TODO except exceptions.CosmosResourceExistsError
        d3 = json.dumps(dataclasses.asdict(convo))
        self.container.create_item(json.loads(d3))

    def print_convos(self):
        for c in self.container.read_all_items():
            print(c)

    def reset(self):
        _id = self.container.id
        self.db.delete_container(_id)
        del self.container
        self.__init__(self.db.id, _id)


if __name__ == '__main__':
    c3 = C3('conversations', 'offerup')
    c3.print_convos()
