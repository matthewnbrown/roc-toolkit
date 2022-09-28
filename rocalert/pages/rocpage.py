from typing import Union
from datetime import datetime
from bs4 import BeautifulSoup


class RocNumber:
    def __init__(self, value: Union[int, str]) -> None:
        if type(value) == int:
            self._value = value
        elif type(value) == str:
            value = value.strip().split(' ')[0].strip()
            value = value.replace(',', '')
            self._value = int(value)
        else:
            raise ValueError("Value must be a string or integer!")

    @property
    def vajlue(self) -> int:
        return self._value

    def get_prettyvalue(self) -> str:
        return f'{self._value:,}'


class RocPage:
    def __init__(self, page: BeautifulSoup) -> None:
        logform = page.find(id='login_form')
        self._loggedin = logform is None

    def _timestamp_to_datetime(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp)

    @property
    def logged_in(self) -> bool:
        return self._loggedin


class RocUserPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        clockbar = page.find(id='clock_bar')
        self._name = clockbar.find(id='topnav_right').text.strip()
        self._rank = clockbar.find(id='s_rank').text
        self._gold = RocNumber(clockbar.find(id='s_gold').text)
        self._turns = RocNumber(clockbar.find(id='s_turns').text)

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def gold(self) -> RocNumber:
        return self._gold

    @property
    def turns(self) -> RocNumber:
        return self._turns

    @property
    def next_turn(self) -> datetime:
        return self._nextturn


class RocRecruitPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        recruit_form = page.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'})
        self._spm = int(spmtext.split(':')[1].strip())
        self._captcha = self._extractcaptcha(
            recruit_form.find(id='captcha_image'))

        if self._captcha is None:
            resettime = recruit_form.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
            self._nextcaptchatime = self._timestamp_to_datetime(int(resettime))
            self._getnorefresh(recruit_form)
        else:
            self._nextcaptchatime = datetime.now()
            self._getrefresh(recruit_form)

    def _extractcaptcha(captchasoup: BeautifulSoup) -> str:
        if captchasoup is None:
            return None

        return captchasoup.get('src').split('=')[1]

    @property
    def spm(self) -> int:
        """_summary_

        Returns:
            int: _description_ Soldiers per minute
        """
        return self._spm

    @property
    def captcha_hash(self) -> str:
        return self._captcha

    @property
    def next_captcha_time(self) -> datetime:
        return self._nextcaptchatime


class RocTrainingPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        # content = page.find(id='content')
        raise NotImplementedError


class RocArmoryPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        # content = page.find(id='content')
        raise NotImplementedError


class RocKeepPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        raise NotImplementedError

    @property
    def repairing(self) -> bool:
        return self._repfinishtime is not None

    @property
    def finish_repair_time(self) -> datetime:
        return self._repfinishtime

    @property
    def key_count(self) -> int:
        return self._keycount

    @property
    def broken_key_count(self) -> int:
        return self._brokenkeycount