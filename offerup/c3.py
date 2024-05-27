import dataclasses
from enum import Enum
from typing import Optional, Self, Any
from dataclasses import dataclass
import json

from azure.core.paging import ItemPaged
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from azure.cosmos.exceptions import ResourceExistsError

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
    def new(cls, _id: str, item_type: str, status=Status.NEW) -> Self:
        return cls(_id, item_type, [], status)


class C3:
    """A cosmos conversation container"""
    def __init__(self, db: str, container: str):
        if db != 'conversations' or container != 'offerup':
            print('Warning: C3 starting with nonstandard db and/or container:', db, container)

        self.client: CosmosClient = CosmosClient(*cfg.cosmos_creds)
        self.db: DatabaseProxy = self.client.get_database_client(db)
        self.partition_key = PartitionKey(path="/status")
        self.container: ContainerProxy = self.db.create_container_if_not_exists(container, self.partition_key)

    def new(self, convo: Convo, skip_conflicts=True) -> None:
        d3 = json.dumps(dataclasses.asdict(convo))

        try:
            self.container.create_item(json.loads(d3))
        except ResourceExistsError as e:
            if skip_conflicts:
                print("Skipping conflict for ", convo.id)
            else:
                raise e

    def update(self, listing_id: str, partition='test', **kwargs) -> None:
        ops = []
        for k, v in kwargs.items():
            ops.append({'op': 'add', 'path': '/' + k, 'value': v})
        self.container.patch_item(item=listing_id, partition_key=partition, patch_operations=ops)

    def print_convos(self) -> None:
        for c in self.container.read_all_items():
            print(c)

    def reset(self) -> None:
        _id = self.container.id
        self.db.delete_container(_id)
        del self.container
        self.__init__(self.db.id, _id)

    def get_ungraded(self, max_item_count=30) -> ItemPaged[dict[str, Any]]:
        return self.container.query_items("SELECT * FROM c WHERE c.grade = null",
                                          enable_cross_partition_query=True,
                                          max_item_count=max_item_count)


if __name__ == '__main__':
    c3 = C3('conversations', 'offerup')
    x = c3.get_ungraded(5)
    print(list(x))
