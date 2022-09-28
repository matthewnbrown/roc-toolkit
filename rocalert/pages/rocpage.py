from collections import defaultdict
from typing import Dict, Union
from datetime import datetime
from bs4 import BeautifulSoup


class RocNumber:
    def __init__(self, value: Union[int, str] = 0) -> None:
        if type(value) == int:
            self._value = value
        elif type(value) == str:
            value = value.strip().split(' ')[0].strip()
            value = value.replace(',', '')
            self._value = int(value)
        else:
            raise ValueError("Value must be a string or integer!")

    @property
    def value(self) -> int:
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


class RocImageCaptchaPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)

        captchasoup = page.find(id='captcha_image')

        if captchasoup is None:
            self._captcha = None
        else:
            self._captcha = captchasoup.get('src').split('=')[1]


class RocRecruitPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        recruit_form = page.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'})
        self._spm = int(spmtext.split(':')[1].strip())

        if self._captcha is None:
            resettime = recruit_form.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
            self._nextcaptchatime = self._timestamp_to_datetime(int(resettime))
            self._getnorefresh(recruit_form)
        else:
            self._nextcaptchatime = datetime.now()
            self._getrefresh(recruit_form)

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


class RocTrainingPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        # content = page.find(id='content')
        raise NotImplementedError


class RocArmoryPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        armory = content.find(id='armory')
        self._getweapons(armory)

        raise NotImplementedError

    def _getweapons(self, armory: BeautifulSoup) -> None:
        self._weapons = {}

        for i in range(1, 15):
            id = f'weapon{i}'
            weapon = armory.find(id=id)
            count = weapon.find('span', {'class':'amount'})
            self._weapons[id] = RocNumber(count)

    @property
    def get_armory_stats(self) -> Dict[str, int]:
        pass

    @property
    def get_weapontroop_dist(self) -> Dict[str, int]:
        pass

class RocKeepPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')

        keycounts = content.find_all('b')
        keytypes = content.find_all('small')

        self._keycount = 0
        self._brokenkeycount = 0

        for i in len(keycounts):
            count = keycounts[i].text
            keytype = keytypes[i].text

            if 'broken' in keytype:
                self._brokenkeycount += count
            else:
                self._keycount += count

        cd = content.find('span', {'class': 'countdown'})
        if cd:
            fintimestr = int(cd.get('data-timestamp'))
            self._repfinishtime = self._timestamp_to_datetime(fintimestr)
        else:
            self._repfinishtime = None

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
