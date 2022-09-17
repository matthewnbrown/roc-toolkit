from rocalert.roc_settings.settingstools import SiteSettings, UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.manualcaptchaservice import ManualCaptchaService


def spyevent(
    roc: RocWebHandler,
    sitesets: SiteSettings,
    usersets: UserSettings,
        ) -> None:
    pass


def spyuser(roc: RocWebHandler, userid: str, homeurl: str) -> bool:
    targeturl = homeurl + f'/attack.php?id={userid}&mission_type=recon'
    captcha = roc.get_url_img_captcha(roc, targeturl)
    if captcha is None:
        return False

    captchares = ManualCaptchaService().run_service(
        roc, None, {'captcha': captcha})

    validans = {str(i) for i in range(1, 10)}
    if 'error' in captchares or captchares['captcha'].ans not in validans:
        return False

    payload = {
        'defender_id': id,
        'mission_type': 'recon',
        'reconspies': 1
    }

    return roc.submit_captcha_url(captcha, targeturl, payload, 'roc_spy')
