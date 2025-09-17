import abc
from collections import deque
import datetime
from typing import Iterable, List, Tuple
from bs4 import BeautifulSoup
from requests import Response

from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.services.captchaservices import (
    CaptchaSolverServiceABC,
    CaptchaSolveException,
)


# TODO: Rework captcha services to use ABC
def _cleanstr_to_int(num: str) -> int:
    return int(num.strip().replace(",", ""))


class BFPageServiceABC(abc.ABC):
    @classmethod
    @abc.abstractclassmethod
    def run_service(cls, roc: RocWebHandler, pagenum: int) -> dict:
        raise NotImplementedError

    @classmethod
    @abc.abstractclassmethod
    def get_page_range(cls, roc: RocWebHandler) -> Tuple[int, int]:
        raise NotImplementedError


class BattlefieldPageService(BFPageServiceABC):
    @classmethod
    def run_service(cls, roc: RocWebHandler, pagenum: int) -> dict:
        pageurl = roc.url_generator.get_home() + f"battlefield.php?p={pagenum}"

        roc.go_to_page(pageurl)

        soup = BeautifulSoup(roc.r.text, "html.parser")
        content = soup.find("div", id="content")

        if not cls._checkvalidpage(content, pagenum):
            return {"response": "error", "error": f"Invalid page number {pagenum}"}

        players = content.find("ul", {"class", "players"}).findChildren(recursive=False)

        targets = cls._get_alltargets(players)

        return {"response": "success", "result": targets}

    @classmethod
    def get_page_range(cls, roc: RocWebHandler) -> Tuple[int, int]:
        pageurl = roc.url_generator.get_home() + f"battlefield.php?p={1}"

        roc.go_to_page(pageurl)
        soup = BeautifulSoup(roc.r.text, "html.parser")
        content = soup.find("div", id="content")
        pagerangetext = content.contents[1].contents[1].text.strip()

        pairs = pagerangetext.split(" of ")
        lower = int(pairs[0].strip().split(" ")[1])
        upper = int(pairs[1].strip().split(" ")[0])
        return (lower, upper)

    @classmethod
    def _checkvalidpage(cls, content: BeautifulSoup, pagenum: int) -> bool:
        pagerangetext = content.contents[1].contents[1].text
        user_count_text = pagerangetext[pagerangetext.index("(") + 1 : pagerangetext.index(")")]
        user_count_text = user_count_text.strip().replace(",", "")
        usercount = int(
            user_count_text
        )
        pagecount = usercount // 50 if usercount % 50 == 0 else 1 + usercount // 50

        return 1 <= pagenum <= pagecount

    @classmethod
    def _get_alltargets(cls, players: Iterable) -> List[BattlefieldTarget]:
        result = []

        for playitem in players:
            player = cls._get_bftarget(playitem)

            result.append(player)

        return result

    @classmethod
    def _get_bftarget(cls, usercontent: BeautifulSoup) -> BattlefieldTarget:
        id = usercontent.get("id").split("_")[1]

        children = usercontent.find_all("div", recursive=False)

        rank = _cleanstr_to_int(children[0].get("id").split("_")[1])
        name_alli = children[1].find_all("a")
        name = name_alli[0].text
        alliance = None if len(name_alli) <= 1 else name_alli[1].text

        tff_gold = children[2].find_all("div", recursive=False)
        tfftext = tff_gold[0].text.strip().split(" ")

        tff = _cleanstr_to_int(tfftext[0])
        tfftype = tfftext[1]

        try: 
            gold = (
                -1
                if "?" in tff_gold[1].text
                else _cleanstr_to_int(tff_gold[1].text.strip().split()[0])
            )
        except Exception as e:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            print(f"Error getting gold. saving html to error_{timestamp}.html: {e}")
            
            with open(f"logs/error_{timestamp}.html", "w") as f:
                f.write(usercontent.prettify())
            raise e

        return BattlefieldTarget(id, rank, name, alliance, tff, tfftype, gold)


class AttackServiceABC(abc.ABC):
    @abc.abstractclassmethod
    def run_service(cls, roc: RocWebHandler, target: BattlefieldTarget):
        raise NotImplementedError


class AttackService(AttackServiceABC):
    @staticmethod
    def run_service(
        roc: RocWebHandler, target: BattlefieldTarget, solvedcaptcha: Captcha
    ):
        attack_url = roc.url_generator.get_attack(target.id)
        attack_page = roc.get_attack_page(target.id)

        payload = {
            "defender_id": target.id,
            "mission_type": "attack",
            "attacks": attack_page.max_attack_turns,
        }
        return roc.submit_captcha_url(solvedcaptcha, attack_url, payload, RocWebHandler.Pages.ATTACK)


class SpyResult:
    SUCCESS = 0
    FAILURE = 1
    WRONG_CAPTCHA = 2
    ADMIN = 3
    UNKNOWN = -1
    ERROR = -2

    def __init__(self, result: int, resp: Response = None, error: str = None) -> None:
        self.result = result
        self.response = resp
        self.error = error


class SpyService:
    def __init__(
        self, roc: RocWebHandler, targets: list[Tuple[BattlefieldTarget, Captcha]] = []
    ) -> None:
        self._roc = roc
        self._targets = deque(targets)

    def _get_spy_url(self, user: BattlefieldTarget) -> str:
        return (
            self._roc.url_generator.get_home()
            + f"attack.php?id={user.id}&mission_type=recon"
        )

    def _get_result(self, resp: Response) -> SpyResult:
        text = resp.text

        if "report_id" in resp.url:
            if "has been alerted" in text:
                return SpyResult(SpyResult.FAILURE, resp)
            elif "spy enters undetected" in text:
                return SpyResult(SpyResult.SUCCESS, resp)
        if "non-player Administrator account" in text:
            return SpyResult(SpyResult.ADMIN, resp)

        return SpyResult(SpyResult.UNKNOWN, resp)

    def _spy_user(self, targetcap: Tuple[BattlefieldTarget, Captcha]) -> SpyResult:
        target, captcha = targetcap

        if captcha.hash is None:
            return SpyResult(SpyResult.ERROR, error="Captcha has no hash")
        if captcha.ans is None:
            return SpyResult(SpyResult.ERROR, error="No answer provided")
        if target.id is None:
            return SpyResult(SpyResult.ERROR, error="Target has no ID")

        targeturl = self._get_spy_url(target)

        payload = {"defender_id": target.id, "mission_type": "recon", "reconspies": 1}

        valid_captcha = self._roc.submit_captcha_url(
            captcha, targeturl, payload, RocWebHandler.Pages.SPY
        )

        if not valid_captcha:
            return SpyResult(SpyResult.WRONG_CAPTCHA, resp=self._roc.r)

        return self._get_result(self._roc.r)

    def add_targets(self, targets: List[Tuple[BattlefieldTarget, Captcha]]):
        self._targets.append(targets)

    def run_service(self) -> List[SpyResult]:
        res = []
        for targetcap in self._targets:
            res.append(self._spy_user(targetcap))

        targetcap = deque()
        return res
