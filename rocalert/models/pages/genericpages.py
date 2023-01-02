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


@dataclass
class RocPage:
    page_type: rocenums.RocPageType = rocenums.RocPageType.UNKNOWN
    creation_date: datetime = None
    logged_in: bool = False


@dataclass
class ClockBar:
    name: str
    rank: int
    gold: int
    turns: int
    next_turn: datetime


@dataclass
class ClockBarPage:
    clock_bar: ClockBar = None


@dataclass
class CaptchaPage:
    captcha_hash: str = None


@dataclass
class StatTableEntry:
    bonus: float
    action: int
    rank: int


@dataclass
class StatTable:
    strike: StatTableEntry
    defense: StatTableEntry
    spy: StatTableEntry
    sentry: StatTableEntry
    kills: int
    kill_ratio: float


@dataclass
class StatTablePage:
    stat_table: StatTable = None


@dataclass
class WeaponDistTableEntry:
    soldiers: int
    weapon_count: Optional[int] = None


@dataclass
class WeaponTroopDistTable:
    attack_wt_dist: WeaponDistTableEntry
    defense_wt_dist: WeaponDistTableEntry
    spy_wt_dist: WeaponDistTableEntry
    sentry_wt_dist: WeaponDistTableEntry
    total_covert_force: WeaponDistTableEntry
    untrained_soldiers: WeaponDistTableEntry
    total_fighting_force: WeaponDistTableEntry


@dataclass
class WeaponTroopDistPage:
    weapon_dist_table: WeaponTroopDistTable = None
