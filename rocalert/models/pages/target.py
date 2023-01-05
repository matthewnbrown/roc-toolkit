import dataclasses
import datetime as dt
import typing

import rocalert.models.common as commonmodels
import rocalert.models.pages.genericpages as gp


@dataclasses.dataclass
class TargetStatItem:
    value: int
    timestamp: dt.datetime


@dataclasses.dataclass
class TargetStatsTable:
    strike: TargetStatItem
    defense: TargetStatItem
    spy: TargetStatItem
    sentry: TargetStatItem
    gold: TargetStatItem


@dataclasses.dataclass
class RecentSpyOp:
    timestamp: dt.datetime
    success: bool
    report_id: str
    

@dataclasses.dataclass
class LatestSpyOpsTable:
    recent_ops: list[RecentSpyOp]
    

@dataclasses.dataclass
class RecentAttack:
    timestamp: dt.datetime
    success: bool
    gold_won: typing.Optional[int]
    report_id: str


@dataclasses.dataclass
class LastAttacksTable:
    last_attacks: list[RecentAttack]
    attacks_shown: int
    total_attacks: int


@dataclasses.dataclass
class CommandChain:
    top: commonmodels.NameIdPair = None
    commander: commonmodels.NameIdPair = None
    is_online: bool = False
    officers: list[commonmodels.Officer] = None


@dataclasses.dataclass
class TargetPage(gp.ClockBarPage):
    name: str = None
    id: str = None
    is_online: bool = True
    gold: int = -1
    rank: int = -1
    alliance_name: str = None
    alliance_id: int = -1
    tff: int = -1
    estimated_tbg: int = -1
    
    stats_table: TargetStatsTable = None
    recent_spy_ops: LatestSpyOpsTable = None
    recent_attacks: LastAttacksTable = None
    command_chain: CommandChain = None
    