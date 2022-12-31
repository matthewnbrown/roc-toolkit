import datetime as dt
import dataclasses

import rocalert.models.pages.genericpages as gp
import rocalert.models as rocmodels


@dataclasses.dataclass
class RecruitDetails:
    soldiers_per_minute: int = -1
    next_captcha_time: dt.datetime = None
    captcha: rocmodels.Captcha = None
    requires_captcha: bool = False


class RecruitPage(gp.RocPage, gp.TurnBoxPage):
    recruit: RecruitDetails
