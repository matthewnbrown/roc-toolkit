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


ALL_ITEM_DETAILS = {
    'dagger': RocItem('Dagger', 1000, 30, RocItem.ItemType.ATTACK, 1),
    'maul': RocItem('Maul', 15000, 300, RocItem.ItemType.ATTACK, 2),
    'blade': RocItem('Blade', 200000, 3000, RocItem.ItemType.ATTACK, 3),
    'excalibur': RocItem('Excalibur', 1000000, 12000,
                         RocItem.ItemType.ATTACK, 4),
    'cloak': RocItem('Cloak', 50000, 30, RocItem.ItemType.SPY, 9),
    'hook': RocItem('Hook', 100000, 50, RocItem.ItemType.SPY, 10),
    'pickaxe': RocItem('Pickaxe', 300000, 120, RocItem.ItemType.SPY, 11),
    'sai': RocItem('Sai', 1000, 30, RocItem.ItemType.DEFENSE, 5),
    'shield': RocItem('Shield', 15000, 300, RocItem.ItemType.DEFENSE, 6),
    'mithril': RocItem('Mithril', 200000, 3000, RocItem.ItemType.DEFENSE, 7),
    'dragonskin': RocItem('Dragonskin', 1000000, 12000,
                          RocItem.ItemType.DEFENSE, 8),
    'horn': RocItem('Horn', 50000, 30, RocItem.ItemType.SENTRY, 12),
    'guard_dog': RocItem('Guard Dog', 100000, 50, RocItem.ItemType.SENTRY, 13),
    'torch': RocItem('Torch', 300000, 120, RocItem.ItemType.SENTRY, 14)
}


# Soldier / Mercenaries
class Soldier:
    def __init__(self, count) -> None:
        self._count = count
        self._id = 'none'
        self._cost = 0

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, newcount: int) -> None:
        if type(newcount) != int or newcount < 0:
            raise Exception('Invalid soldier count')

        self._count = newcount

    @property
    def soldier_id(self) -> str:
        return self._id

    @property
    def cost(self) -> int:
        return self._cost

    @cost.setter
    def cost(self, newcost: int) -> None:
        if type(newcost) != int or newcost < 0:
            raise Exception('Invalid cost')

        self._cost = newcost


class AttackSoldier(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self._cost = 1000
        self._id = 'attack_soldiers'


class DefenseSoldier(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self._cost = 1000
        self._id = 'defense_soldiers'


class Spy(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self._cost = 2000
        self._id = 'spies'


class Sentry(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self._cost = 2000
        self._id = 'sentries'


class AttackMerc(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self._cost = 2500
        self._id = 'attack_mercs'


class DefenseMerc(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self.cost = 2500
        self._id = 'defense_mercs'


class UntrainedMerc(Soldier):
    def __init__(self, count) -> None:
        super().__init__(count)
        self.cost = 2000
        self._id = 'untrained_mercs'
