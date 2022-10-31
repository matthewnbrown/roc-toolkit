
from ._settings import Setting, Settings, SettingsValidator, SettingsError
from urllib.parse import urlparse


def __validurl__(urlstr: str) -> bool:
    try:
        result = urlparse(urlstr)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class SiteSettings(Settings):
    DEFAULT_SETTINGS = {
        'roc_home':
            Setting('ROC Index Page', 'roc_home', 'ENTER_HOME_URL',
                    str, 'Index page of ROC.',
                    validation_func=__validurl__),
        'roc_login':
            Setting('ROC Login Page', 'roc_login', 'ENTER_LOGIN_URL',
                    str, 'Login page likely homepage + /login.php',
                    validation_func=__validurl__),
        'roc_recruit':
            Setting('ROC Recruit Page', 'roc_recruit', 'ENTER_RECRUIT_URL',
                    str, 'Recruit captcha page',
                    validation_func=__validurl__),
        'roc_armory':
            Setting('ROC Armory Page', 'roc_armory', 'ENTER_ARMORY_URL',
                    str, 'Armory page of ROC',
                    validation_func=__validurl__),
        'roc_training':
            Setting('ROC Training Page', 'roc_training', 'ENTER_TRAINING_URL',
                    str, 'Soldier training page',
                    validation_func=__validurl__)
    }

    def __init__(self, name: str = None, filepath: str = None) -> None:
        if name is None:
            name = 'Site Settings'

        super().__init__(name, filepath)

        self.mandatory = {'roc_home', 'roc_recruit'}

        if filepath is not None:
            SettingsValidator.check_mandatories(
                self.settings, self.mandatory, quit_if_bad=True)
            validUrls = True

            for id, setting in self.settings.items():
                if id not in SiteSettings.DEFAULT_SETTINGS:
                    continue
                url = setting.value

                validurl = self.DEFAULT_SETTINGS[id].validation_func(url)
                if not validurl:
                    print(f'{setting.pname} is invalid')

                validUrls &= validurl

            if not validUrls:
                raise SettingsError('Site settings are not set correctly. '
                                    + 'Ensure URLs are valid. Exiting')

            if 'training' in self.settings['roc_training'].value:
                raise SettingsError(
                    'Training URL should not be training.php,' +
                    'it was changed to train.php. Please update site.settings.'
                    )

    def get_page(self, page: str) -> str:
        return self.get_value(page)

    def get_home(self) -> str:
        return self.get_page('roc_home')

    def get_recruit(self) -> str:
        return self.get_page('roc_recruit')

    def get_armory(self) -> str:
        return self.get_page('roc_armory')

    def get_training(self) -> str:
        return self.get_page('roc_training')

    def get_login_url(self) -> str:
        return self.get_page('roc_login')
