from typing import Dict, Tuple, Union
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

    def __add__(self, other):
        return RocNumber(self.value + other.value)

    def __sub__(self, other):
        return RocNumber(self.value - other.value)

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

    @property
    def attack_soldiers(self) -> RocNumber:
        return self._attacksold

    @property
    def attack_mercenaries(self) -> RocNumber:
        return self._attackmercs

    @property
    def defense_soldiers(self) -> RocNumber:
        return self._defensesold

    @property
    def defense_mercenaries(self) -> RocNumber:
        return self._defensemercs

    @property
    def untrained_soldiers(self) -> RocNumber:
        return self._untrainedsold

    @property
    def untrained_mercenaries(self) -> RocNumber:
        return self._untrainedmercs

    @property
    def spies(self) -> RocNumber:
        return self._spies

    @property
    def sentries(self) -> RocNumber:
        return self._sentries

    @property
    def zombies(self) -> RocNumber:
        return self._zombies

    @property
    def total_soldiers(self) -> RocNumber:
        return self.attack_soldiers \
                + self.defense_soldiers \
                + self.untrained_soldiers

    @property
    def total_mercenaries(self) -> RocNumber:
        return self._attackmercs \
                + self._defensemercs \
                + self._untrainedmercs

    @property
    def total_covert_force(self) -> RocNumber:
        return self._spies + self._sentries

    @property
    def total_fighting_force(self) -> RocNumber:
        return self.total_soldiers + self.total_mercenaries

    @property
    def avail_attack_mercs(self) -> Tuple[RocNumber, RocNumber]:
        return (self._availmercs['attack'], self._merccost['attack'])

    @property
    def avail_defense_mercs(self) -> Tuple[RocNumber, RocNumber]:
        return (self._availmercs['defense'], self._merccost['defense'])

    @property
    def avail_untrained_mercs(self) -> Tuple[RocNumber, RocNumber]:
        return (self._availmercs['untrained'], self._merccost['untrained'])


class RocArmoryPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        armory = content.find(id='armory')
        self._parseweapons(armory)

        raise NotImplementedError

    def _parseweapons(self, armory: BeautifulSoup) -> None:
        self._weapons = {}

        weaponmap = {
            1: 'dagger',
            2: 'maul',
            3: 'blade',
            4: 'excalibur',
            5: 'sai',
            6: 'shield',
            7: 'mithril',
            8: 'dragonskin',
            9: 'cloak',
            10: 'hook',
            11: 'pickaxe',
            12: 'horn',
            13: 'guard_dog',
            14: 'torch'
        }
        for i in range(1, len(weaponmap)+1):
            weapon = armory.find(id=f'weapon{i}')
            count = weapon.find('span', {'class': 'amount'})
            self._weapons[weaponmap[i]] = RocNumber(count)

    @property
    def get_weapons(self) -> Dict[str, RocNumber]:
        return self._weapons


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
