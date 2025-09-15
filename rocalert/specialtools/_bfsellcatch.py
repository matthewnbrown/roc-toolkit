from datetime import datetime
from typing import Callable
from rocalert.captcha.captchaprovider import CaptchaProvider
from rocalert.services.rocwebservices import BFPageServiceABC, AttackServiceABC
from rocalert.rocaccount import BattlefieldTarget
from rocalert.roc_web_handler import RocWebHandler, Captcha
from rocalert.rocpurchases import ROCBuyer
from rocalert.services.captchaservices import CaptchaSolveException
import time


class BFSellCatch:
    def __init__(
            self,
            bf_pageservce: BFPageServiceABC,
            attack_serv: AttackServiceABC,
            buyer: ROCBuyer,
            roc: RocWebHandler,
            captcha_provider: CaptchaProvider) -> None:
        self._bfps = bf_pageservce
        self._attackservice = attack_serv
        self._buyer = buyer
        self._roc = roc
        self._captcha_provider = captcha_provider

    def _get_all_users(self) -> None:
        pagenum = 1
        self._battlefield = self._battlefield if self._battlefield else []

        while True:
            user_resp = self._bfps.run_service(self._roc, pagenum)
            pagenum += 1
            if user_resp['response'] == 'error':
                break

            newuser = self._filterusers(user_resp['result'])
            self._battlefield.extend(newuser)

    def _attack_target(self, target: BattlefieldTarget) -> bool:
        alliance = '-' if target.alliance is None else target.alliance
        print(f'Attacking {target.name} | {alliance}'
              + f' with {target.formatted_gold()} gold')

        start = datetime.now()
        captcha = self._captcha_provider.get_solved_captcha()
        captcha_get_time = datetime.now() - start

        if captcha_get_time.total_seconds() > 1.5:
            print("took to long to get captcha.. resetting")
            return False

        self._attackservice.run_service(
            self._roc, target, captcha)

        return True

    def _buy(self):
        payload = self._buyer.create_order_payload()

        itemcount = 0
        for ic in payload.values():
            if len(ic) > 0:
                itemcount += int(ic)

        if itemcount == 0:
            print('Purchase payload is only 0 items.')
            return True

        print(f'Purchasing {itemcount} items')

        page = 'roc_armory'

        correct = False
        try:
            captcha = self._captcha_provider.get_solved_captcha()

            correct = self._roc.submit_captcha(
                captcha, captcha.ans, page, payload)
        except CaptchaSolveException as e:
            print(f'Error solving captcha: {e}')

        if correct:
            print("Correct answer")
            self.consecutive_captcha_failures = 0
            captcha.ans_correct = True
        else:
            print("Incorrect answer?????")
            self.consecutive_captcha_failures += 1
        return captcha

    def run(
            self,
            shouldhit: Callable[[BattlefieldTarget], bool],
            pagedelay: float = 0.01,
            lowpage: int = 1,
            highpage: int = 2
    ) -> None:

        while True:
            for pnum in range(lowpage, highpage+1):
                targets = self._bfps.run_service(self._roc, pnum)['result']
                targets.sort(reverse=True, key=lambda x: x.gold)

                if len(targets) == 0:
                    print(f'Top Page {pnum}: No Targets')
                else:
                    print(f'Top Page {pnum}: {targets[0]}')

                for target in targets:
                    if shouldhit(target):
                        hittarget = self._attack_target(target)
                        if hittarget:
                            self._buy()
                            break

                time.sleep(pagedelay)
