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
        return NotImplemented

    def __sub__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count - other, self.cost)
        elif type(other) == ItemCostPair:
            return ItemCostPair(self.count - other.count, self.cost)
        return NotImplemented

    def __mul__(self, other):
        if type(other) == int:
            return ItemCostPair(self.count * other, self.cost)
        return NotImplemented

    def __iadd__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count + other, self.cost)
            return self
        elif type(other) == ItemCostPair:
            self = ItemCostPair(self.count + other.count, self.cost)
            return self
        return NotImplemented

    def __isub__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count - other, self.cost)
            return self
        elif type(other) == ItemCostPair:
            self = ItemCostPair(self.count - other.count, self.cost)
            return self
        return NotImplemented

    def __imul__(self, other):
        if type(other) == int:
            self = ItemCostPair(self.count * other, self.cost)
            return self
        return NotImplemented


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
    cost: int = 0

    @property
    def total_soldiers(self) -> int:
        return self.attack_soldiers + self.defense_soldiers \
            + self.spies + self.sentries

    @property
    def total_mercs(self) -> int:
        return self.attack_mercs + self.defense_mercs + self.untrained_mercs

    def __add__(self, other):
        if type(other) == TrainingPurchaseModel:
            return TrainingPurchaseModel(
                self.attack_soldiers + other.attack_soldiers,
                self.defense_soldiers + other.defense_soldiers,
                self.spies + other.spies,
                self.sentries + other.sentries,
                self.attack_mercs + other.attack_mercs,
                self.defense_mercs + other.defense_mercs,
                self.untrained_mercs + other.untrained_mercs,
                self.sell_attack_soldiers + other.sell_attack_soldiers,
                self.sell_defense_soldiers + other.sell_defense_soldiers,
                self.sell_spies + other.sell_spies,
                self.sell_sentries + other.sell_sentries,
                self.sell_attack_mercs + other.sell_attack_mercs,
                self.sell_defense_mercs + other.sell_defense_mercs,
                self.sell_untrained_mercs + other.sell_untrained_mercs,
                self.cost + other.cost,
            )
        return NotImplemented

    def __imul__(self, other):
        if type(other) == int:
            self.attack_soldiers += other.attack_soldiers
            self.defense_soldiers += other.defense_soldiers
            self.spies += other.spies
            self.sentries += other.sentries
            self.attack_mercs += other.attack_mercs
            self.defense_mercs += other.defense_mercs
            self.untrained_mercs += other.untrained_mercs
            self.sell_attack_soldiers += other.sell_attack_soldiers
            self.sell_defense_soldiers += other.sell_defense_soldiers
            self.sell_spies += other.sell_spies
            self.sell_sentries + other.sell_sentries
            self.sell_attack_mercs += other.sell_attack_mercs
            self.sell_defense_mercs += other.sell_defense_mercs
            self.sell_untrained_mercs += other.sell_untrained_mercs
            self.cost += other.cost
            return self
        return NotImplemented


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
    cost: int = 0
