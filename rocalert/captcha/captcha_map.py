import os
from roc_settings.settingstools import SettingsSaver, SettingsLoader


class CaptcahMap:
    def __init__(self, filename='captcha/map.txt') -> None:
        self.filename = filename
        self.map = {}
        self.__load_map()

    def __contains__(self, key):
        return key in self.map

    def __load_map(self):
        if not os.path.exists(self.filename):
            SettingsSaver.save_settings_toPath(self.filename, self.map)
            return
        SettingsLoader.load_settings_from_path(self.filename, self.map, False)

    def __save_map(self):
        SettingsSaver.save_settings_toPath(self.filename, self.map)

    def __append_captcha(self, hash: str, val: str):
        pass

    def add_captcha(self, hash: str, val: str, append_to_file: True):
        self.map[hash] = val

        if append_to_file:
            self.__append_captcha(hash, val)
