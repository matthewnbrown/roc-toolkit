from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup

import rocalert.pages.genericpages as gp


class Officer:
    def __init__(self, name: str, id: str, allianceid: int) -> None:
        self._name = name
        self._id = id
        self._allianceid = allianceid

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> str:
        return self._id

    @property
    def allianceid(self) -> int:
        return self._allianceid


class TargetStat:
    def __init__(self, value: int, detectdate: datetime) -> None:
        self._value = value
        self._detectdate = detectdate

    @property
    def value(self) -> int:
        return self._value

    @property
    def detectdate(self) -> datetime:
        return self._detectdate


# TODO: Add command chain
# TODO: Add profile
# TODO: App spyops
# Todo: App attacks
class RocStatsPage(gp.RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        self._target_gold = None
        self._target_attack = None
        self._target_defense = None
        self._target_spy = None
        self._target_sentry = None

        content = page.find(id="content")
        self._parsetargetinfo(content=content)
        self._parsetarget_metastats(content=content)
        self._parsetarget_stathistory(content=content)

    def _parsetargetinfo(self, content: BeautifulSoup) -> None:
        targetbar = content.find("div", {"class": lambda c: "playercard_name" in c})

        self._is_online = "oindicator" in targetbar.get("class")
        self._target_name = targetbar.find("h1").text

        playeraction = content.find("div", {"class": lambda c: "player_action" in c})
        attackaction = playeraction.find("a", text="Attack")
        self._target_id = attackaction.get("href").split("=")[1]

    def _parsetarget_metastats(self, content: BeautifulSoup) -> None:
        statsbar = content.find("div", {"class": lambda c: "playercard_stats" in c})
        ranktxt = statsbar.find("div", {"class": lambda c: "playercard_rank" in c}).text
        self._rank = gp.rocnum_to_int(ranktxt.split("#")[1])
        alliancecard = statsbar.find(
            "div", {"class": lambda c: "playercard_alliance" in c}
        ).find("a")

        print(alliancecard)
        if alliancecard is None or alliancecard.text.strip() == "":
            self._target_alliance_name = None
            self._target_alliance = None
        else:
            self._target_alliance_name = alliancecard.text
            self._target_alliance = alliancecard.get("href").split("=")[1]

        armytxt = statsbar.find(
            "div", {"class": lambda c: "playercard_size" in c}
        ).text.strip()
        tfftxt, self._target_army_type = armytxt.split(" ", maxsplit=2)
        self._target_tff = gp.rocnum_to_int(tfftxt)

        goldtxt = content.find(
            "div", {"class": lambda c: "playercard_gold" in c}
        ).text.strip()

        if "???" not in goldtxt:
            self._target_gold = TargetStat(
                gp.rocnum_to_int(goldtxt.split(" ")[0]), datetime.now()
            )

    def _parsetarget_commandchain(self, content: BeautifulSoup) -> None:
        raise NotImplementedError()

    def _parsetarget_stathistory(self, content: BeautifulSoup) -> None:
        rows = content.find("table")
        if rows is None:
            return
        for row in rows.find_all("tr"):
            self._set_statvalue(row)

    def _set_statvalue(self, tablerow: BeautifulSoup) -> None:
        statnameitem = tablerow.find("b")
        if statnameitem is None:
            return

        statname = statnameitem.text.replace(":", "").lower().strip()
        statvalue = gp.rocnum_to_int(tablerow.find("td", {"align": "right"}).text)
        statdate = gp.roctimestampstamp_to_datetime(
            tablerow.find("span").get("data-timestamp")
        )

        print(f"{statname} {statvalue} {statdate}")
        if statname == "strike":
            self._target_attack = TargetStat(statvalue, statdate)
        elif statname == "defense":
            self._target_defense = TargetStat(statvalue, statdate)
        elif statname == "spy":
            self._target_spy = TargetStat(statvalue, statdate)
        elif statname == "sentry":
            self._target_sentry = TargetStat(statvalue, statdate)
        elif statname == "gold" and self._target_gold is None:
            self._target_gold = TargetStat(statvalue, statdate)

    def _parsetarget_profile(self, content: BeautifulSoup) -> None:
        raise NotImplementedError()

    def _parsetarget_estimated_tbg(self, content: BeautifulSoup) -> None:
        item = content.find("div", {"id": "recon_tbg"})

        if item is None:
            self._estimated_tbg = None
            return

        self._estimated_tbg = gp.rocnum_to_int(item.text)

    @property
    def target_name(self) -> str:
        return self._target_name

    @property
    def target_id(self) -> str:
        return self._target_id

    @property
    def is_online(self) -> bool:
        return self._is_online

    @property
    def target_rank(self) -> int:
        return self._target_rank

    @property
    def target_alliance_id(self) -> Optional[int]:
        return self._target_alliance

    @property
    def target_alliance_name(self) -> Optional[str]:
        return self._target_alliance_name

    @property
    def target_tff(self) -> int:
        return self._target_tff

    @property
    def army_type(self) -> str:
        return self._target_army_type

    @property
    def target_gold(self) -> Optional[TargetStat]:
        return self._target_gold

    @property
    def target_attack(self) -> Optional[TargetStat]:
        return self._target_attack

    @property
    def target_defense(self) -> Optional[TargetStat]:
        return self._target_defense

    @property
    def target_spy(self) -> Optional[TargetStat]:
        return self._target_spy

    @property
    def target_sentry(self) -> Optional[TargetStat]:
        return self._target_sentry

    @property
    def officers(self) -> list[Officer]:
        raise NotImplementedError()
        # return self._officers

    @property
    def estimated_tbg(self) -> int:
        return self._estimated_tbg
