from rocalert.services.remote_lookup import RemoteCaptcha
import rocalert.services.captchaservices as captchaservices
from rocalert.rocpurchases import ROCBuyer, SimpleRocTrainer
from rocalert.roc_settings import BuyerSettings,\
    SettingsSetupHelper, UserSettings, TrainerSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator
from rocalert.pagegenerators.bs4 import BeautifulSoupPageGenerator
from rocalert.logging import DateTimeGeneratorABC, DateTimeNowGenerator


_user_settings_fp = 'user.settings'
_trainer_settings_fp = 'trainer.settings'
_buyer_settings_fp = 'buyer.settings'


class ServiceConfigurationException():
    pass


def _settings_are_valid() -> bool:
    filepaths = {
        'trainer': (_trainer_settings_fp, TrainerSettings),
        'user': (_user_settings_fp, UserSettings),
        'buyer': (_buyer_settings_fp, BuyerSettings)
    }

    settings_file_error = False

    for settype, infotuple in filepaths.items():
        path, settingtype = infotuple
        if SettingsSetupHelper.needs_setup(path):
            settings_file_error = True
            SettingsSetupHelper.create_default_file(
                path, settingtype.DEFAULT_SETTINGS)
            print(f"Created settings file {path}.")

    if settings_file_error:
        print("Exiting. Please fill out settings files")
        return False

    return True


def _get_parser() -> str:
    return 'lxml'


def _get_timegenerator() -> DateTimeGeneratorABC:
    return DateTimeNowGenerator()


def configure_services() -> dict[str, object]:

    if not _settings_are_valid():
        msg = 'Error configuring services. Settings are invalid.'
        raise ServiceConfigurationException(msg)

    user_settings = UserSettings(filepath=_user_settings_fp)
    services = {}

    services['user_settings'] = user_settings
    services['gen_captcha_logger'] = CaptchaLogger(
        'logs/captcha_answers.log', timestamp=True)

    services['correct_captcha_logger'] = CaptchaLogger(
        'logs/correct_ans.log', log_correctness=False)

    services['default_headers'] = _get_default_headers()

    services['remote_captcha'] = RemoteCaptcha(
        user_settings.get_value('remote_captcha_add'),
        user_settings.get_value('remote_captcha_lookup'))

    services['urlgenerator'] = ROCDecryptUrlGenerator()

    if user_settings.get_setting('auto_solve_captchas').value:
        savepath = user_settings.get_setting('captcha_save_path').value
        apikey = user_settings.get_setting('auto_captcha_key').value
        services['capsolver'] = captchaservices.TwocaptchaSolverService(
            api_key=apikey, savepath=savepath)
    else:
        services['capsolver'] = captchaservices.ManualCaptchaSolverService()

    services['rochandler'] = RocWebHandler(
        urlgenerator=services['urlgenerator'],
        default_headers=services['default_headers'])

    services['buyer'] = ROCBuyer(
        services['rochandler'],
        BuyerSettings(filepath=_buyer_settings_fp),
    )

    services['trainer'] = SimpleRocTrainer(
        TrainerSettings(filepath=_trainer_settings_fp)
    )

    services['parser'] = _get_parser()
    services['timegenerator'] = _get_timegenerator()
    services['page_generator'] = BeautifulSoupPageGenerator(
        services['parser'],
        services['timegenerator']
    )

    return services


def _get_default_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml'
                  + ';q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                      + 'Chrome/107.0.0.0 Safari/537.36',
    }
