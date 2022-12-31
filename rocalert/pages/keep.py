import datetime as dt
import dataclasses

import rocalert.pages.genericpages as gp


@dataclasses.dataclass(frozen=True)
class KeepDetails:
    repairing: bool
    finish_repair_time: dt.datetime
    key_count: int
    broken_key_count: int


@dataclasses.dataclass(frozen=True)
class KeepPage(gp.RocPage, gp.TurnBox):
    keep: KeepDetails
