from bs4 import BeautifulSoup

import rocalert.pages.genericpages as gp


class RocAttackPage(gp.RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id="content")
        self._parseturns(content)
        self._parsetargetinfo(content)

    def _parseturns(self, content: BeautifulSoup) -> None:
        attackinput = content.find("input", {"name": "attacks"})
        self._max_attack_turns = int(attackinput.get("value"))

    def _parsetargetinfo(self, content: BeautifulSoup) -> None:
        targetbar = content.find("div", {"class": lambda c: "playercard_name" in c})

        self._is_online = "oindicator" in targetbar.get("class")
        self._target_name = targetbar.find("a").text
        self._target_id = targetbar.find("a").get("href").split("=")[1]

    @property
    def max_attack_turns(self) -> int:
        return self._max_attack_turns

    @property
    def target_name(self) -> str:
        return self._target_name

    @property
    def target_id(self) -> str:
        return self._target_id

    @property
    def is_online(self) -> bool:
        return self._is_online
