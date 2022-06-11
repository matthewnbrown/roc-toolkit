import os
import unittest
from datetime import datetime
from settingstools import SettingsSaver

class SettingsSaverTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.filename = 'SettingsSaverTest39920fe4902e79e63f4078fc2e61e481'

    def load_settings(self) -> dict:
        with open(self.filename) as f:
            lines = f.readlines()
        
        settings = {}
        for line in lines:
            setting, val = line.strip().split(':', maxsplit=1)
            settings[setting] = val

        return settings

    def SettingSaveLoad(self, settings) -> dict:
        SettingsSaver.save_settings_toPath(self.filename, settings)
        res = self.load_settings()
        os.remove(self.filename)
        return res

    def test_overwrite_file(self):
        text = 'this should be gone'
        with open(self.filename, 'w') as f:
            f.write(text)
            f.write('\n')
        
        settings = {'a':1, 'b':2, 'c':3}

        SettingsSaver.save_settings_toPath(self.filename, settings)
        
        with open(self.filename, 'r') as f:
            input_text = f.read()
        
        os.remove(self.filename)

        self.assertFalse(text in input_text)

    def test_int_saving(self):
        settings = { 'test': 5 }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], '5')
    
    def test_true_bool_saving(self):
        settings = { 'test': True }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], 'True')

    def test_false_bool_saving(self):
        settings = { 'test': False }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], 'False')

    def test_string_saving(self):
        settings = { 'test': 'abc123' }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], 'abc123')

    def test_time_saving_short(self):
        settings = { 'test': datetime.strptime('12:34', '%H:%M').time() }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], '12:34:00')

    def test_time_saving_long(self):
        settings = { 'test': datetime.strptime('12:34:56', '%H:%M:%S').time() }
        res = self.SettingSaveLoad(settings)
        self.assertEqual(res['test'], '12:34:56')

    def test_proper_number_saved(self):
        settings = { 't1': 1, 't2': True, 't3': 'abc123'}
        res = self.SettingSaveLoad(settings)
        self.assertEqual(len(settings), len(res))

        



#class UserSettingsTest(unittest.TestCase):
#    def __init__(self, methodName: str = ...) -> None:
#        super().__init__(methodName)

if __name__ == "__main__":
    unittest.main()
   # sets = { 213123:'34243234', 3:True, 323232:'FALSERFSDF'}

   # SettingsSaver.save_settings_toPath('mypath.txt', sets)
