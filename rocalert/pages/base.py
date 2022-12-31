from dataclasses import dataclass
from typing import Tuple
import rocalert.pages.genericpages as gp
import datetime as dt


@dataclass(frozen=True)
class RocEvent:
    name: str
    description: str
    date: dt.datetime
    is_active: bool


@dataclass(frozen=True)
class RocActivity:
    date: dt.datetime
    activity_text: str


@dataclass(frozen=True)
class BaseDetails:
    alliance: Tuple[str, str]
    commander: Tuple[str, str]
    officers: list[Tuple[str, str]]
    current_events: list[RocEvent]
    upcoming_events: list[RocEvent]
    all_events: list[RocEvent]
    recent_activity: list[RocActivity]
    server_timestr: str
    personal_totals_table: int  # TODO: Fix this type
    soldier_source_table: int  # TODO: Fix this type
    keys_found: int
    loot_found: int
    last_active: dt.datetime
    best_rank: Tuple[int, dt.datetime]
    army: str
    race_bonuses: list[str]
    turn_based_gold: int


@dataclass
class BasePage(gp.RocPage, gp.TurnBoxPage):
    base: BaseDetails
    stats: gp.StatTable
    weapon_distribution: gp.WeaponTroopDistTable
