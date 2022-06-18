import os
import unittest
from rocalert.captcha.captcha_logger import Captcha, CaptchaLogger

class SettingsSaverTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.logFileName = 'logs/test_logging.txt'
        self.defaultHash = '0a2beecfce8c28306104357ba856e5dc'

    def read_logfile_contents(self) -> str:
        return ''

    def delete_logfile(self) -> None:
        os.remove(self.logFileName)

    def test_cyrillic_(self): 
        ans = u'\u0421'
        c = Captcha(self.defaultHash, None, ans, False)
        logger = CaptchaLogger(self.logFileName, timestamp=False, log_correctness=False)
        logger.log_captcha(c)

        res = self.read_logfile_contents()
        self.delete_logfile()

        self.assertEqual('{0}:{1}'.format(self.defaultHash, ans), res)