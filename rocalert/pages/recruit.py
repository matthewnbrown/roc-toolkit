import datetime as dt
import dataclasses

import rocalert.pages.genericpages as gp


@dataclasses.dataclass
class RecruitDetails:
    soldiers_per_minute: int
    next_captcha_time: dt.datetime
    requires_captcha: bool


class RecruitPage(gp.RocPage, gp.TurnBox, gp.CaptchaStatus):
    recruit: RecruitDetails
