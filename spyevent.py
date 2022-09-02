from rocalert.roc_settings.settingstools import SiteSettings, UserSettings
from rocalert.roc_web_handler import RocWebHandler


def spyevent(
    roc: RocWebHandler,
    sitesets: SiteSettings,
    usersets: UserSettings,
        ) -> None:
    pass


def spyuser(userid: str, homeurl: str) -> None:
    targeturl = homeurl + f'/attack.php?id={userid}&mission_type=recon'
