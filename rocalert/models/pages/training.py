from dataclasses import dataclass

import rocalert.models.pages.genericpages as gp


@dataclass
class RocTrainingTableEntry:
    count: int
    income: int


@dataclass
class TrainingDetails:
    attack_soldiers: RocTrainingTableEntry = None
    attack_mercenaries: RocTrainingTableEntry = None
    defense_soldiers: RocTrainingTableEntry = None
    defense_mercenaries: RocTrainingTableEntry = None
    untrained_soldiers: RocTrainingTableEntry = None
    untrained_mercenaries: RocTrainingTableEntry = None
    spies: RocTrainingTableEntry = None
    sentries: RocTrainingTableEntry = None
    zombies: RocTrainingTableEntry = None
    total_soldiers: RocTrainingTableEntry = None
    total_mercenaries: RocTrainingTableEntry = None
    total_covert_force: RocTrainingTableEntry = None
    total_fighting_force: RocTrainingTableEntry = None
    avail_attack_mercs: RocTrainingTableEntry = None
    avail_defense_mercs: RocTrainingTableEntry = None
    avail_untrained_mercs: RocTrainingTableEntry = None
    attack_sold_cost: int = -1
    defense_sold_cost: int = -1
    spy_sold_cost: int = -1
    sentry_sold_cost: int = -1


@dataclass
class TrainingPage(gp.RocPage, gp.ClockBarPage, gp.CaptchaPage):
    training: TrainingDetails
    stats: gp.StatTable
    weapon_distrubtion: gp.WeaponTroopDistTable
