import dataclasses


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
