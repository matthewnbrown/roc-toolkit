from dataclasses import dataclass
from typing import Tuple
import datetime as dt

import rocalert.models.pages.genericpages as gp
import rocalert.enums as rocenums


@dataclass
class RocEvent:
    name: str
    description: str
    date: dt.datetime
    is_active: bool


@dataclass
class RocActivity:
    date: dt.datetime
    activity_text: str


@dataclass
class RocArmy:
    Size: int
    Race: rocenums.RocRace


@dataclass
class BaseDetails:
    keys_found: int = -1
    loot_found: int = -1
    last_active: dt.datetime = None
    highest_rank: Tuple[int, dt.datetime] = None
    army: RocArmy = None
    race_bonuses: list[str] = None
    turn_based_gold: int = -1
    recent_activity: list[RocActivity] = None
    current_events: list[RocEvent] = None
    upcoming_events: list[RocEvent] = None
    server_timestr: str = None
    cards: list = None
    # personal_totals_table: str  # TODO: Fix this type
    # soldier_source_table: str # TODO: Fix this type
    alliance: Tuple[str, str] = None
    commander: Tuple[str, str] = None
    officers: list[Tuple[str, str]] = None


@dataclass
class BasePage(gp.RocPage, gp.ClockBarPage):
    base: BaseDetails
    stats: gp.StatTable
    weapon_distribution: gp.WeaponTroopDistTable
