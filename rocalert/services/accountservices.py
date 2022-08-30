from urllib import request
from rocalert.rocaccount import ROCTraining, RocItem, ROCAccount, ROCArmory, ROCStats
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.rocservice import RocService
from bs4 import BeautifulSoup


class GetGold(RocService):
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:

        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        if not roc.is_logged_in():
            return { 'response': 'failure', 'error': 'ROC is not logged in'}

        roc.go_to_armory()
        resp = roc.get_response()

        if resp.status_code != 200:
            return {'response': 'failure', 'error':
                    'Received status code:{resp.status_code}'}

        soup = BeautifulSoup(resp.text, 'html.parser')
        gold = soup.find('s_gold').replace(',', '').strip()
        gold = int(gold)

        if gold >= 0:
            return {'response': 'success', 'result': gold}
        else:
            return {'response': 'failure', 'error':
                    f'Invalid gold amount: {gold}'}


class GetTraining(RocService):
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:

        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        raise NotImplementedError


class GetArmory(RocService):
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:

        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        raise NotImplementedError


class GetStats(RocService):
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:

        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        raise NotImplementedError


class GetAccount(RocService):
    """Gets a ROC Account with gold, stats, training and armory"""

    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:

        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        r, e = 'result', 'error'
        try:
            gold_res = GetGold.run_service(roc, settings, custom_settings)
            train_res = GetTraining.run_service(roc, settings, custom_settings)
            armory_res = GetArmory.run_service(roc, settings, custom_settings)
            stat_res = GetStats.run_service(roc, settings, custom_settings)

            failure_res = []
            if gold_res[r] == 'failure':
                failure_res.append(('gold', gold_res[e]))
            elif train_res[r] == 'failure':
                failure_res.append(('training', train_res[e]))
            elif armory_res[r] == 'failure':
                failure_res.append(('armory', armory_res[e]))
            elif stat_res[r] == 'failure':
                failure_res.append(('stats', stat_res[e]))

            if len(failure_res) > 0:
                allerrors = ''
                for name, error in failure_res:
                    allerrors += f'{name}:{error}&'
                return {r: 'failure', e: allerrors[:-1]}

            account = ROCAccount(
                gold_res['response'],
                stat_res['response'],
                train_res['response'],
                armory_res['response'])

            return {r: 'success', 'response': account}
        except Exception as ex:
            return {r: 'failure', e: ex.args[0]}
