import datetime as dt
import dataclasses

import rocalert.models.pages.genericpages as gp


@dataclasses.dataclass
class KeepDetails:
    repairing: bool
    finish_repair_time: dt.datetime
    key_count: int
    broken_key_count: int


@dataclasses.dataclass
class KeepPage(gp.RocPage, gp.ClockBarPage):
    keep: KeepDetails
