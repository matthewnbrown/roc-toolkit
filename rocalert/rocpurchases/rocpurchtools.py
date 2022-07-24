from enum import Enum


class RocItemGroup:
    def __init__(
            self,
            groupname: str,
            description: str,
            items: dict
            ) -> None:
        self.__name = groupname
        self.__desc = description
        self.items = items


class RocItem():
    class ItemType(Enum):
        ATTACK = 1
        DEFENSE = 2
        SPY = 3
        SENTRY = 4

    def __init__(
            self,
            name: str,
            cost: int,
            stat_val: int,
            stat_type: ItemType,
            item_code: str
            ) -> None:
        self.name = name
        self.cost = cost
        self.stat_val = stat_val
        self.stat_type = stat_type
        self.code = item_code