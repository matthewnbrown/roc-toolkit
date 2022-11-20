from ._trainingsettings import TrainerSettings
from ._site_settings import SiteSettings
from ._usersettings import UserSettings
from ._buyersettings import BuyerSettings
from ._settings import Setting, Settings, SettingsSetupHelper,\
    SettingsLoader, SettingsSaver, SettingsError

if __name__ == '__main__':
    print('dont run this')
    TrainerSettings()
    SiteSettings()
    UserSettings()
    BuyerSettings()
    Setting()
    Settings()
    SettingsSetupHelper()
    SettingsLoader()
    SettingsSaver()
    SettingsError()
