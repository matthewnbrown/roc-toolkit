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


@dataclasses.dataclass
class TrainingPurchaseModel:
    attack_soldiers: int = ItemCostPair()
    defense_soldiers: int = ItemCostPair()
    spies: int = ItemCostPair()
    sentries: int = ItemCostPair()
    attack_mercs: int = ItemCostPair()
    defense_mercs: int = ItemCostPair()
    untrained_mercs: int = ItemCostPair()
    sell_attack_soldiers: int = ItemCostPair()
    sell_defense_soldiers: int = ItemCostPair()
    sell_spies: int = ItemCostPair()
    sell_sentries: int = ItemCostPair()
    sell_attack_mercs: int = ItemCostPair()
    sell_defense_mercs: int = ItemCostPair()
    sell_untrained_mercs: int = ItemCostPair()


@dataclasses.dataclass
class ArmoryPurchaseModel:
    dagger: int = ItemCostPair()
    maul: int = ItemCostPair()
    blade: int = ItemCostPair()
    excalibur: int = ItemCostPair()
    sai: int = ItemCostPair()
    shield: int = ItemCostPair()
    mithril: int = ItemCostPair()
    dragonskin: int = ItemCostPair()
    cloak: int = ItemCostPair()
    hook: int = ItemCostPair()
    pickaxe: int = ItemCostPair()
    horn: int = ItemCostPair()
    guard_dog: int = ItemCostPair()
    torch: int = ItemCostPair()
