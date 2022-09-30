import os
import unittest
from datetime import datetime
from rocalert.roc_settings.settingstools import SettingsSaver,\
    SettingsLoader, Setting


class SettingsSaverTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.filename = 'SettingsSaverTest39920fe4902e79e63f4078fc2e61e481'

    def __del__(self):
        if os.path.exists(self.filename):
            print('Warning: File cleanup required')
            os.remove(self.filename)

    def load_settings(self) -> dict:
        with open(self.filename) as f:
            lines = f.readlines()

        settings = {}
        for line in lines:
            setting, val = line.strip().split(':', maxsplit=1)
            settings[setting] = val

        return settings

    def settings_saveload(self, settings) -> dict:
        SettingsSaver.save_settings_toPath(self.filename, settings)
        res = SettingsLoader.load_settings_from_path(self.filename, {})
        os.remove(self.filename)
        return res

    def test_overwrite_file(self):
        text = 'this should be gone'
        with open(self.filename, 'w') as f:
            f.write(text)
            f.write('\n')

        settings = {
            'a': Setting('aset', 'asetn', 15, int),
            'b': Setting('bset', 'bsetn', 'bsetting', str),
            'c': Setting('cset', 'csetn', 15.33, float)
            }

        SettingsSaver.save_settings_toPath(self.filename, settings)

        with open(self.filename, 'r') as f:
            input_text = f.read()

        os.remove(self.filename)

        self.assertFalse(text in input_text)

    def test_int_saving(self):
        settings = {'test': Setting('TestSet', 'test', 5, int)}
        res = self.settings_saveload(settings)
        self.assertEqual(int(res['test'].value), 5)

    def test_true_bool_saving(self):
        settings = {'test': Setting('TestSet', 'test', True, bool)}
        res = self.settings_saveload(settings)
        self.assertEqual(res['test'].value, 'True')

    def test_false_bool_saving(self):
        settings = {'test': Setting('TestSet', 'test', False, bool)}
        res = self.settings_saveload(settings)
        self.assertEqual(res['test'].value, 'False')

    def test_string_saving(self):
        settings = {'test': Setting('TestSet', 'test', 'abc123', str)}
        res = self.settings_saveload(settings)
        self.assertEqual(res['test'].value, 'abc123')

    def test_time_saving_short(self):
        settings = {'test': Setting
                    ('TestSet', 'test',
                     datetime.strptime('12:34', '%H:%M').time(), datetime)}
        res = self.settings_saveload(settings)
        self.assertEqual(res['test'].value, '12:34:00')

    def test_time_saving_long(self):
        settings = {'test': Setting
                    ('TestSet', 'test',
                     datetime.strptime('12:34:56', '%H:%M:%S').time(),
                     datetime)}
        res = self.settings_saveload(settings)
        self.assertEqual(res['test'].value, '12:34:56')

    def test_proper_number_saved(self):
        settings = {'t1': Setting('TestSet', 't1', 1, int),
                    't2': Setting('TestSet', 't2', True, bool),
                    't3': Setting('TestSet', 't3', 'abc123', str)
                    }
        res = self.settings_saveload(settings)
        self.assertEqual(len(settings), len(res))

    def test_settings_key_match(self):
        settings = {'t1': Setting('TestSet', 't1', 1, int),
                    't2': Setting('TestSet', 't2', True, bool),
                    't3': Setting('TestSet', 't3', 'abc123', str)
                    }
        res = self.settings_saveload(settings)

        matches = True
        for setting in settings:
            if setting not in res:
                matches = False
        self.assertTrue(matches)

    def test_settings_values_match(self):
        settings = {'t1': Setting('TestSet', 't1', 1, int),
                    't2': Setting('TestSet', 't2', True, bool),
                    't3': Setting('TestSet', 't3', 'abc123', str)
                    }
        res = self.settings_saveload(settings)

        matches = True
        for setting in settings:
            if setting not in res:
                matches = False
                break
            if settings[setting].valtype(res[setting].value) \
                    != settings[setting].value:
                matches = False
                break

        self.assertTrue(matches)


class SettingsLoaderTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)


class UserSettingsTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)


class SiteSettingsTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)


if __name__ == "__main__":
    unittest.main()
