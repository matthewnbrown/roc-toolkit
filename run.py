from rocalert.pyrocalert import RocAlert
from rocalert.roc_settings.settingstools import SettingsFileMaker, SiteSettings, UserSettings

if __name__== '__main__':
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'

    if SettingsFileMaker.needs_user_setup(user_settings_fp, site_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    us = UserSettings(filepath=user_settings_fp)
    site = SiteSettings(filepath=site_settings_fp)
    a = RocAlert(us, site)

    a.start()