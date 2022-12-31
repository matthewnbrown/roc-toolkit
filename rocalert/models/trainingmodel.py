import dataclasses
from rocalert.models import ItemCostPair


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
