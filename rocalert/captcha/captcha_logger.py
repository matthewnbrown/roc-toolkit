from rocalert.roc_web_handler import Captcha
from datetime import datetime
import os 

class CaptchaLogger:
    def __init__(self, savefile: str, timestamp: bool = False, log_correctness: bool = True) -> None:
        self._savefile = savefile
        self._timestamp = timestamp
        self._add_answer_correctness = log_correctness

        dirname = os.path.dirname(savefile)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            
    @property
    def set_savefile(self, savefile: str): self._savefile = savefile

    @property
    def get_savefile(self): return self._savefile

    def set_timestamp(self, timestamp: bool): self._timestamp = timestamp
    def set_log_correctness(self, log_correctness: bool): self._add_answer_correctness = log_correctness

    def __create_line(self, captcha: Captcha) -> str:
        msg = '{0}:{1}'.format(captcha.hash, captcha.ans)
        if self._add_answer_correctness:
            msg = '{0}:{1}'.format(msg, captcha.ans_correct)
        
        if self._timestamp:
            ts = datetime.now().strftime("%H:%M:%S")
            return '{0}: {1}\n'.format(ts, msg)
        else:
            return '{0}\n'.format(msg)

    def log_captcha(self, captcha: Captcha) -> None:
        with open(self._savefile, 'a+', encoding="utf-8") as f:
            message = self.__create_line(captcha)
            f.write(message)
        