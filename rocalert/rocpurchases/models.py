import dataclasses


@dataclasses.dataclass(frozen=True)
class ItemCostPair:
    count: int = 0
    cost: int = -1

    @property
    def total_cost(self) -> int:
        return self.count * self.cost

    def __add__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count + other, self.cost)
        elif type(other) == ItemCostPair:
            return ItemCostPair(self.count + other.count, self.cost)
        return self + other

    def __sub__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count - other, self.cost)
        elif type(other) == ItemCostPair:
            return ItemCostPair(self.count - other.count, self.cost)
        return self + other

    def __mul__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count * other, self.cost)
        return self * other


@dataclasses.dataclass
class TrainingModel:
    untrained_soldiers: ItemCostPair = ItemCostPair()
    attack_soldiers: ItemCostPair = ItemCostPair(cost=1000)
    defense_soldiers: ItemCostPair = ItemCostPair(cost=1000)
    spies: ItemCostPair = ItemCostPair(cost=2000)
    sentries: ItemCostPair = ItemCostPair(cost=2000)
    attack_mercs: ItemCostPair = ItemCostPair(cost=2500)
    defense_mercs: ItemCostPair = ItemCostPair(cost=2500)
    untrained_mercs: ItemCostPair = ItemCostPair(cost=2000)


@dataclasses.dataclass
class ArmoryModel:
    dagger: ItemCostPair = ItemCostPair()
    maul: ItemCostPair = ItemCostPair()
    blade: ItemCostPair = ItemCostPair()
    excalibur: ItemCostPair = ItemCostPair()
    sai: ItemCostPair = ItemCostPair()
    shield: ItemCostPair = ItemCostPair()
    mithril: ItemCostPair = ItemCostPair()
    dragonskin: ItemCostPair = ItemCostPair()
    cloak: ItemCostPair = ItemCostPair()
    hook: ItemCostPair = ItemCostPair()
    pickaxe: ItemCostPair = ItemCostPair()
    horn: ItemCostPair = ItemCostPair()
    guard_dog: ItemCostPair = ItemCostPair()
    torch: ItemCostPair = ItemCostPair()

    @property
    def total_attack_weapons(self) -> int:
        total = self.dagger + self.maul + self.blade + self.excalibur
        return total.count

    @property
    def total_defense_weapons(self) -> int:
        total = self.sai + self.shield + self.mithril + self.dragonskin
        return total.count

    @property
    def total_spy_weapons(self) -> int:
        total = self.cloak + self.hook + self.pickaxe
        return total.count

    @property
    def total_sentry_weapons(self) -> int:
        total = self.horn + self.guard_dog + self.torch
        return total.count


@dataclasses.dataclass
class TrainingPurchaseModel:
    attack_soldiers: int = 0
    defense_soldiers: int = 0
    spies: int = 0
    sentries: int = 0
    attack_mercs: int = 0
    defense_mercs: int = 0
    untrained_mercs: int = 0
    sell_attack_soldiers: int = 0
    sell_defense_soldiers: int = 0
    sell_spies: int = 0
    sell_sentries: int = 0
    sell_attack_mercs: int = 0
    sell_defense_mercs: int = 0
    sell_untrained_mercs: int = 0


@dataclasses.dataclass
class ArmoryPurchaseModel:
    dagger: int = 0
    maul: int = 0
    blade: int = 0
    excalibur: int = 0
    sai: int = 0
    shield: int = 0
    mithril: int = 0
    dragonskin: int = 0
    cloak: int = 0
    hook: int = 0
    pickaxe: int = 0
    horn: int = 0
    guard_dog: int = 0
    torch: int = 0

