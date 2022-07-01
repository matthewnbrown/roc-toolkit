import os
import unittest
from rocalert.captcha.captcha_logger import Captcha, CaptchaLogger


class CaptchaLoggerTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.logFileName = 'logs/test_logging.txt'
        self.defaultHash = '0a2beecfce8c28306104357ba856e5dc'

    def read_logfile_lines(self) -> str:
        with open(self.logFileName, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        return lines

    def delete_logfile(self) -> None:
        os.remove(self.logFileName)

    def make_simple_logger(self) -> CaptchaLogger:
        logger = CaptchaLogger(
            self.logFileName,
            timestamp=False,
            log_correctness=False)
        return logger

    def test_simple_true(self):
        ans = '6'
        c = Captcha(self.defaultHash, None, ans, True)
        logger = self.make_simple_logger()
        logger.log_captcha(c)
        res = self.read_logfile_lines()[0].strip()
        self.delete_logfile()

        self.assertEqual('{0}:{1}'.format(c.hash, ans), res)

    def test_cyrillic(self):
        ans = u'\u0421'
        c = Captcha(self.defaultHash, None, ans, False)
        logger = self.make_simple_logger()
        logger.log_captcha(c)
        res = self.read_logfile_lines()[0].strip()
        self.delete_logfile()

        self.assertEqual('{0}:{1}'.format(c.hash, ans), res)


if __name__ == "__main__":
    unittest.main()
