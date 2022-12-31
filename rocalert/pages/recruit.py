import datetime as dt
import dataclasses

import rocalert.pages.genericpages as gp
import rocalert.models as rocmodels


@dataclasses.dataclass
class RecruitDetails:
    soldiers_per_minute: int
    next_captcha_time: dt.datetime
    captcha: rocmodels.Captcha
    requires_captcha: bool


class RecruitPage(gp.RocPage, gp.TurnBoxPage):
    recruit: RecruitDetails
