import dataclasses
import typing


@dataclasses.dataclass
class TrainingModel:
    untrained_soldiers: typing.Tuple(int, int)
    attack_soldiers: typing.Tuple(int, int)
    defense_soldiers: typing.Tuple(int, int)
    spies: typing.Tuple(int, int)
    sentries: typing.Tuple(int, int)
    attack_mercs: typing.Tuple(int, int)
    defense_mercs: typing.Tuple(int, int)
    untrained_mercs: typing.Tuple(int, int)


@dataclasses.dataclass
class ArmoryModel:
    dagger: typing.Tuple(int, int)
    maul: typing.Tuple(int, int)
    blade: typing.Tuple(int, int)
    excalibur: typing.Tuple(int, int)
    sai: typing.Tuple(int, int)
    shield: typing.Tuple(int, int)
    mithril: typing.Tuple(int, int)
    dragonskin: typing.Tuple(int, int)
    cloak: typing.Tuple(int, int)
    hook: typing.Tuple(int, int)
    pickaxe: typing.Tuple(int, int)
    horn: typing.Tuple(int, int)
    guard_dog: typing.Tuple(int, int)
    torch: typing.Tuple(int, int)


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
