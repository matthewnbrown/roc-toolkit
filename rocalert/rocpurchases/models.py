import dataclasses


@dataclasses.dataclass(frozen=True)
class ItemCostPair:
    count: int = 0
    cost: int = 0

    @property
    def total_cost(self) -> int:
        return self.count * self.cost


@dataclasses.dataclass
class TrainingModel:
    untrained_soldiers: ItemCostPair = ItemCostPair()
    attack_soldiers: ItemCostPair = ItemCostPair()
    defense_soldiers: ItemCostPair = ItemCostPair()
    spies: ItemCostPair = ItemCostPair()
    sentries: ItemCostPair = ItemCostPair()
    attack_mercs: ItemCostPair = ItemCostPair()
    defense_mercs: ItemCostPair = ItemCostPair()
    untrained_mercs: ItemCostPair = ItemCostPair()


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
        return self.dagger + self.maul + self.blade + self.excalibur

    @property
    def total_defense_weapons(self) -> int:
        return self.sai + self.shield + self.mithril + self.dragonskin

    @property
    def total_spy_weapons(self) -> int:
        return self.cloak + self.hook + self.pickaxe

    @property
    def total_sentry_weapons(self) -> int:
        return self.horn + self.guard_dog + self.torch


@dataclasses.dataclass
class TrainingPurchaseModel:
    attack_soldiers: int
    defense_soldiers: int
    spies: int
    sentries: int
    attack_mercs: int
    defense_mercs: int
    untrained_mercs: int
    sell_attack_soldiers: int
    sell_defense_soldiers: int
    sell_spies: int
    sell_sentries: int
    sell_attack_mercs: int
    sell_defense_mercs: int
    sell_untrained_mercs: int


@dataclasses.dataclass
class ArmoryPurchaseModel:
    dagger: int
    maul: int
    blade: int
    excalibur: int
    sai: int
    shield: int
    mithril: int
    dragonskin: int
    cloak: int
    hook: int
    pickaxe: int
    horn: int
    guard_dog: int
    torch: int
