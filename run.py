from pyrocalert import RocAlert
from settingstools import SiteSettings, UserSettings

if __name__== '__main__':
    us = UserSettings(filepath='user.settings')
    site = SiteSettings(filepath='site.settings')
    a = RocAlert(us, site)

    a.start()