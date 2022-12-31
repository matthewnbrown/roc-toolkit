from dataclasses import dataclass
from typing import Optional
from datetime import datetime

import rocalert.enums as rocenums


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(' ')[0].strip()
    value = value.replace(',', '')
    return int(value)


def int_to_rocnum(num: int):
    return f'{num:,}'


@dataclass(frozen=True)
class RocPage:
    page_type: rocenums.RocPageType
    creation_date: datetime
    logged_in: bool


@dataclass(frozen=True)
class TurnBox:
    name: str
    rank: int
    gold: int
    turns: int
    next_turn: datetime


@dataclass(frozen=True)
class CaptchaStatus:
    captcha_hash: str


@dataclass(frozen=True)
class StatTableEntry:
    bonus: float
    action: int
    rank: int


@dataclass(frozen=True)
class StatTable:
    strike: StatTableEntry
    defense: StatTableEntry
    spy: StatTableEntry
    sentry: StatTableEntry
    kills: int
    kill_ratio: float


@dataclass(frozen=True)
class WeaponDistTableEntry:
    soldiers: int
    weapon_count: Optional[int] = None


@dataclass(frozen=True)
class WeaponTroopDistTable:
    attack_wt_dist: WeaponDistTableEntry
    defense_wt_dist: WeaponDistTableEntry
    spy_wt_dist: WeaponDistTableEntry
    sentry_wt_dist: WeaponDistTableEntry
    total_covert_force: WeaponDistTableEntry
    untrained_soldiers: WeaponDistTableEntry
    total_fighting_force: WeaponDistTableEntry
