from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from bs4 import BeautifulSoup


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(" ")[0].strip()
    value = value.replace(",", "")
    return int(value)


def roctimestampstamp_to_datetime(date_as_str: str):
    return datetime.fromtimestamp(int(date_as_str))


def int_to_rocnum(num: int):
    return f"{num:,}"


class RocPage:
    def __init__(self, page: BeautifulSoup) -> None:
        logform = page.find(id="login_form")
        self._loggedin = logform is None

    def _timestamp_to_datetime(self, timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp)

    @property
    def logged_in(self) -> bool:
        return self._loggedin


class RocUserPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        self._name = page.find(id="topnav_right").text.strip()
        clockbar = page.find(id="clock_bar")
        self._rank = int(clockbar.find(id="s_rank").text)
        self._gold = rocnum_to_int(clockbar.find(id="s_gold").text)
        self._turns = rocnum_to_int(clockbar.find(id="s_turns").text)

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

        captchasoup = page.find(id="captcha_image")

        if captchasoup is None:
            self._captcha_hash = None
        else:
            self._captcha_hash = captchasoup.get("src").split("=")[1]

    @property
    def captcha_hash(self) -> str:
        return self._captcha_hash


class StatTable:
    def __init__(self, table: BeautifulSoup) -> None:
        rows = table.find_all("tr")

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

    def _parseaction(self, row: BeautifulSoup) -> Tuple[float, rocnum_to_int, int]:
        label = row.contents[1].text
        if "+" in label:
            bonus = float(label[label.index("+") + 1 : label.index("%")])
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


@dataclass(frozen=True)
class WeaponDistTableEntry:
    soldiers: int
    weapon_count: Optional[int] = None


class WeaponTroopDistTable:
    def __init__(self, table: BeautifulSoup) -> None:
        tbody = table.find("tbody")
        table = tbody if tbody else table

        rows = table.find_all("tr")

        self._att_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[2].contents[5].text.split(" ")[0]),
            rocnum_to_int(rows[2].contents[3].text),
        )

        self._def_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[3].contents[5].text.split(" ")[0]),
            rocnum_to_int(rows[3].contents[3].text),
        )

        self._spy_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[4].contents[5].text),
            rocnum_to_int(rows[4].contents[3].text),
        )

        self._sentry_wtdist = WeaponDistTableEntry(
            rocnum_to_int(rows[5].contents[5].text),
            rocnum_to_int(rows[5].contents[3].text),
        )

        tffeles = rows[6].find_all("td")
        self._tff = WeaponDistTableEntry(rocnum_to_int(tffeles[2].text))
        tcfeles = rows[7].find_all("td")
        self._tcf = WeaponDistTableEntry(rocnum_to_int(tcfeles[2].text))
        self._untrained = WeaponDistTableEntry(
            self._extract_untrained(rows[2].contents[5].text)
        )

    def _extract_untrained(self, attacksoldiers: str) -> int:
        split = attacksoldiers.split(" ")
        if len(split) != 3:
            return 0
        num = split[1]
        return rocnum_to_int(num.split("+", maxsplit=1)[1])

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
