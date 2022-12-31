from dataclasses import dataclass

import rocalert.models.pages.genericpages as gp


@dataclass
class RocTrainingTableEntry:
    count: int
    income: int


@dataclass
class TrainingDetails:
    attack_soldiers: RocTrainingTableEntry
    attack_mercenaries: RocTrainingTableEntry
    defense_soldiers: RocTrainingTableEntry
    defense_mercenaries: RocTrainingTableEntry
    untrained_soldiers: RocTrainingTableEntry
    untrained_mercenaries: RocTrainingTableEntry
    spies: RocTrainingTableEntry
    sentries: RocTrainingTableEntry
    zombies: RocTrainingTableEntry
    total_soldiers: RocTrainingTableEntry
    total_mercenaries: RocTrainingTableEntry
    total_covert_force: RocTrainingTableEntry
    total_fighting_force: RocTrainingTableEntry
    avail_attack_mercs: RocTrainingTableEntry
    avail_defense_mercs: RocTrainingTableEntry
    avail_untrained_mercs: RocTrainingTableEntry
    attack_sold_cost: int
    defense_sold_cost: int
    spy_sold_cost: int
    sentry_sold_cost: int


@dataclass
class TrainingPage(gp.RocPage, gp.TurnBoxPage, gp.CaptchaPage):
    training: TrainingDetails
    stats: gp.StatTable
    weapon_distrubtion: gp.WeaponTroopDistTable
