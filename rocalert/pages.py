from typing import Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(' ')[0].strip()
    value = value.replace(',', '')
    return int(value)


def int_to_rocnum(num: int):
    return f'{num:,}'


class RocPage:
    def __init__(self, page: BeautifulSoup) -> None:
        logform = page.find(id='login_form')
        self._loggedin = logform is None

    def _timestamp_to_datetime(self, timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp)

    @property
    def logged_in(self) -> bool:
        return self._loggedin


class RocUserPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        self._name = page.find(id='topnav_right').text.strip()
        clockbar = page.find(id='clock_bar')
        self._rank = int(clockbar.find(id='s_rank').text)
        self._gold = rocnum_to_int(clockbar.find(id='s_gold').text)
        self._turns = rocnum_to_int(clockbar.find(id='s_turns').text)

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def turns(self) -> int:
        return self._turns

    @property
    def next_turn(self) -> datetime:
        return self._nextturn


class RocImageCaptchaPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)

        captchasoup = page.find(id='captcha_image')

        if captchasoup is None:
            self._captcha_hash = None
        else:
            self._captcha_hash = captchasoup.get('src').split('=')[1]

    @property
    def captcha_hash(self) -> str:
        return self._captcha_hash


class RocRecruitPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        recruit_form = page.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'}).text
        self._spm = int(spmtext.split(':')[1].strip())

        if self._captcha_hash is None:
            self._get_oncooldown(recruit_form)
        else:
            self._nextcaptchatime = datetime.now()

    def _get_oncooldown(self, recruit_form: BeautifulSoup) -> None:
        no_refresh = recruit_form.find(id='spm_no_refresh')
        resettime = no_refresh.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
        self._nextcaptchatime = self._timestamp_to_datetime(int(resettime))

    @property
    def soldiers_per_minute(self) -> int:
        return self._spm

    @property
    def next_captcha_time(self) -> datetime:
        return self._nextcaptchatime


class StatTable:
    def __init__(self, table: BeautifulSoup) -> None:
        rows = table.find_all('tr')

        self._strike = self._parseaction(rows[1])
        self._defense = self._parseaction(rows[2])
        self._spy = self._parseaction(rows[3])
        self._sentry = self._parseaction(rows[4])
        self._kills = rocnum_to_int(rows[5].contents[3].text)
        self._killratio = float(rows[6].contents[3].text)

    class StatTableEntry:
        def __init__(self, bonus: float, action: int, rank: int) -> None:
            self._bonus = bonus
            self._action = action
            self._rank = rank

        @property
        def bonus(self) -> float:
            return self._bonus

        @property
        def action(self) -> int:
            return self._action

        @property
        def rank(self) -> int:
            return self._rank

    def _parseaction(
            self, row: BeautifulSoup
            ) -> Tuple[float, rocnum_to_int, int]:

        label = row.contents[1].text
        if '+' in label:
            bonus = float(label[label.index('+')+1: label.index('%')])
        else:
            bonus = 0.0
        action = rocnum_to_int(row.contents[3].text)
        rank = int(row.contents[5].text[1:])

        return StatTable.StatTableEntry(bonus, action, rank)

    @property
    def strike(self) -> StatTableEntry:
        return self._strike

    @property
    def defense(self) -> StatTableEntry:
        return self._defense

    @property
    def spy(self) -> StatTableEntry:
        return self._spy

    @property
    def sentry(self) -> StatTableEntry:
        return self._sentry

    @property
    def kills(self) -> int:
        return self._kills

    @property
    def kill_ratio(self) -> float:
        return self._killratio


class WeaponDistTableEntry:
    def __init__(
            self,
            soldiers: int,
            weaponcount: Optional[int] = None
            ) -> None:
        self._soldiers = soldiers
        self._weaponcount = weaponcount

    @property
    def soldiers(self) -> int:
        return self._soldiers

    @property
    def weapon_count(self) -> Optional[int]:
        return self._weaponcount


class WeaponTroopDistTable:
    def __init__(self, table: BeautifulSoup) -> None:
        tbody = table.find('tbody')
        table = tbody if tbody else table

        rows = table.find_all('tr')

        self._att_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[2].contents[5].text.split(' ')[0]),
            rocnum_to_int(rows[2].contents[3].text))

        self._def_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[3].contents[5].text.split(' ')[0]),
            rocnum_to_int(rows[3].contents[3].text))

        self._spy_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[4].contents[5].text),
            rocnum_to_int(rows[4].contents[3].text))

        self._sentry_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[5].contents[5].text),
            rocnum_to_int(rows[5].contents[3].text))

        tffeles = rows[6].find_all('td')
        self._tff = WeaponDistTableEntry(rocnum_to_int(tffeles[2].text))
        tcfeles = rows[7].find_all('td')
        self._tcf = WeaponDistTableEntry(rocnum_to_int(tcfeles[2].text))
        self._untrained = WeaponDistTableEntry(
            self._extract_untrained(rows[2].contents[5].text))

    def _extract_untrained(self, attacksoldiers: str) -> int:
        split = attacksoldiers.split(' ')
        if len(split) != 3:
            return 0
        num = split[1]
        return rocnum_to_int(num.split('+', maxsplit=1)[1])

    @property
    def attack_wt_dist(self) -> WeaponDistTableEntry:
        return self._att_wtdist

    @property
    def defense_wt_dist(self) -> WeaponDistTableEntry:
        return self._def_wtdist

    @property
    def spy_wt_dist(self) -> WeaponDistTableEntry:
        return self._spy_wtdist

    @property
    def sentry_wt_dist(self) -> WeaponDistTableEntry:
        return self._sentry_wtdist

    @property
    def total_covert_force(self) -> WeaponDistTableEntry:
        return self._tcf

    @property
    def untrained_soldiers(self) -> WeaponDistTableEntry:
        return self._untrained

    @property
    def total_fighting_force(self) -> WeaponDistTableEntry:
        return self._tff


class RocTrainingTableEntry:
    def __init__(self, count: int, cost: rocnum_to_int) -> None:
        self._count = count
        self._cost = cost

    @property
    def income(self) -> int:
        return self._cost

    @property
    def count(self) -> int:
        return self._count


class RocTrainingPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)

        content = page.find(id='content')
        fpc = content.find_all('div', {'class': 'flexpanel_container'})
        self._get_mercs_avail(fpc[0])

        fpctables = fpc[1].find_all('table')
        self._stattable = StatTable(fpctables[0])
        self._weapondisttable = WeaponTroopDistTable(fpctables[2])

        self._get_troops_table(fpctables[1])

    def _get_mercs_avail(self, content: BeautifulSoup) -> None:
        attspans = content.find(id='cell_merc_attack_mercs').find_all('span')
        attcountstr = attspans[0].text.split(' ')[1]
        self._availattmercs = RocTrainingTableEntry(
            rocnum_to_int(attcountstr), rocnum_to_int(attspans[1].text))

        defspans = content.find(id='cell_merc_defense_mercs').find_all('span')
        defcountstr = defspans[0].text.split(' ')[1]
        self._availdefmercs = RocTrainingTableEntry(
            rocnum_to_int(defcountstr), rocnum_to_int(defspans[1].text))

        untspan = content.find(id='cell_merc_untrained_mercs').find_all('span')
        untcountstr = untspan[0].text.split(' ')[1]
        self._availuntmercs = RocTrainingTableEntry(
            rocnum_to_int(untcountstr), rocnum_to_int(untspan[1].text))

    def _parse_row(self, row: BeautifulSoup) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(
                rocnum_to_int(row.contents[3].text),
                rocnum_to_int(row.contents[5].text))

    def _get_troops_table(self, table: BeautifulSoup) -> None:
        rows = table.find_all('tr')
        self._attacksold = self._parse_row(rows[2])
        self._attackmercs = self._parse_row(rows[3])
        self._defensesold = self._parse_row(rows[4])
        self._defensemercs = self._parse_row(rows[5])
        self._untrainedsold = self._parse_row(rows[6])
        self._untrainedmercs = self._parse_row(rows[7])
        self._spies = self._parse_row(rows[8])
        self._sentries = self._parse_row(rows[9])
        self._zombies = self._parse_row(rows[10])
        self._totalmercs = self._parse_row(rows[11])
        self._totalsoldiers = self._parse_row(rows[12])
        self._totalcovert = self._parse_row(rows[13])
        self._tff = self._parse_row(rows[14])

    @property
    def attack_soldiers(self) -> RocTrainingTableEntry:
        return self._attacksold

    @property
    def attack_mercenaries(self) -> RocTrainingTableEntry:
        return self._attackmercs

    @property
    def defense_soldiers(self) -> RocTrainingTableEntry:
        return self._defensesold

    @property
    def defense_mercenaries(self) -> RocTrainingTableEntry:
        return self._defensemercs

    @property
    def untrained_soldiers(self) -> RocTrainingTableEntry:
        return self._untrainedsold

    @property
    def untrained_mercenaries(self) -> RocTrainingTableEntry:
        return self._untrainedmercs

    @property
    def spies(self) -> RocTrainingTableEntry:
        return self._spies

    @property
    def sentries(self) -> RocTrainingTableEntry:
        return self._sentries

    @property
    def zombies(self) -> RocTrainingTableEntry:
        return self._zombies

    @property
    def total_soldiers(self) -> RocTrainingTableEntry:
        return self._totalsoldiers

    @property
    def total_mercenaries(self) -> RocTrainingTableEntry:
        return self._totalmercs

    @property
    def total_covert_force(self) -> RocTrainingTableEntry:
        return self._totalcovert

    @property
    def total_fighting_force(self) -> RocTrainingTableEntry:
        return self._tff

    @property
    def avail_attack_mercs(self) -> RocTrainingTableEntry:
        return self._availattmercs

    @property
    def avail_defense_mercs(self) -> RocTrainingTableEntry:
        return self._availdefmercs

    @property
    def avail_untrained_mercs(self) -> RocTrainingTableEntry:
        return self._availuntmercs


class RocArmoryPage(RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        armory = content.find(id='armory')
        self._parseweapons(armory)

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
            count = weapon.find('span', {'class': 'amount'}).text
            self._weapons[weaponmap[i]] = rocnum_to_int(count)

    def _get_weapon(self, name: str) -> int:
        return self._weapons(name)

    @property
    def daggers(self) -> int:
        return self._get_weapon('dagger')

    @property
    def mauls(self) -> int:
        return self._get_weapon('maul')

    @property
    def blades(self) -> int:
        return self._get_weapon('blade')

    @property
    def excaliburs(self) -> int:
        return self._get_weapon('excalibur')

    @property
    def sais(self) -> int:
        return self._get_weapon('sai')

    @property
    def shields(self) -> int:
        return self._get_weapon('shield')

    @property
    def mithrils(self) -> int:
        return self._get_weapon('mithril')

    @property
    def dragonskins(self) -> int:
        return self._get_weapon('dragonskin')

    @property
    def horns(self) -> int:
        return self._get_weapon('horn')

    @property
    def guard_dogs(self) -> int:
        return self._get_weapon('guard_dog')

    @property
    def torches(self) -> int:
        return self._get_weapon('torch')

    @property
    def cloaks(self) -> int:
        return self._get_weapon('cloak')

    @property
    def hooks(self) -> int:
        return self._get_weapon('hook')

    @property
    def pickaxes(self) -> int:
        return self._get_weapon('pickaxe')


class RocKeepPage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        keystatusarea = content.contents[5]
        keyspan = keystatusarea.find('span')

        keycounts = keyspan.find_all('b')
        keytypes = keyspan.find_all('small')

        self._keycount = 0
        self._brokenkeycount = 0

        for i in range(len(keycounts)):
            count = int(keycounts[i].text)
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


class RocBasePage(RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)