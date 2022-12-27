from typing import Callable
from rocalert.services.rocwebservices import BFPageServiceABC, AttackServiceABC
from rocalert.rocaccount import BattlefieldTarget
from rocalert.roc_web_handler import RocWebHandler, Captcha
from rocalert.rocpurchases import ROCBuyer
from rocalert.services.captchaservices import CaptchaSolverServiceABC, \
    CaptchaSolveException
import time


class BFSellCatch:
    def __init__(
            self,
            bf_pageservce: BFPageServiceABC,
            attack_serv: AttackServiceABC,
            buyer: ROCBuyer,
            roc: RocWebHandler,
            captchasolver: CaptchaSolverServiceABC) -> None:
        self._bfps = bf_pageservce
        self._attackservice = attack_serv
        self._buyer = buyer
        self._roc = roc
        self._capsolver = captchasolver

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

    def _attack_target(self, target: BattlefieldTarget):
        alliance = '-' if target.alliance is None else target.alliance
        print(f'Attacking {target.name} | {alliance}'
              + ' with {target.gold:,} gold')
        self._attackservice.run_service(self._roc, target, self._capsolver)

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
        captcha = self._roc.get_img_captcha(page)

        if captcha is None:
            print('Weird error go check for yourself')
            return None
        if captcha.type and captcha.type == Captcha.CaptchaType.TEXT:
            print('Uhoh text captcha')
            captcha.ans_correct = False

        correct = False
        try:
            captcha = self._capsolver.solve_captcha(captcha)
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

                print(f'Top Page {pnum}: {targets[0]}')

                for target in targets:
                    if shouldhit(target):
                        self._attack_target(target)
                        self._buy()
                    else:
                        break

                time.sleep(pagedelay)
