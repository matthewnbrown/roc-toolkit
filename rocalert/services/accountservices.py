from rocalert.rocaccount import ROCTraining, RocItem, ROCAccount, ROCArmory, ROCStats
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases.rocpurchtools import ALL_ITEM_DETAILS
from rocalert.services.rocservice import RocService
from bs4 import BeautifulSoup


def __get_amount(number: str) -> int:
    return int(number.strip().replace(',', ''))


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
            return {'response': 'failure', 'error': 'ROC is not logged in'}

        roc.go_to_armory()
        resp = roc.get_response()

        if resp.status_code != 200:
            return {'response': 'failure', 'error':
                    'Received status code:{resp.status_code}'}

        soup = BeautifulSoup(resp.text, 'html.parser')
        gold = soup.find('s_gold')
        gold = __get_amount(gold)

        if gold >= 0:
            return {'response': 'success', 'result': gold}
        else:
            return {'response': 'failure', 'error':
                    f'Invalid gold amount: {gold}'}


_training_ids = {
    'attack_solders': 'cell_untrain_attack_soldiers',
    'defense_soldiers': 'cell_untrain_defense_soldiers',
    'spies': 'cell_untrain_spies',
    'sentries': 'cell_untrain_sentries',
    'attack_mercs': 'cell_fire_attack_mercs',
    'defense_mercs': 'cell_fire_defense_mercs',
    'untrained_mercs': 'cell_fire_untrained_mercs'
}


class GetTraining(RocService):
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:
        """_summary_

        Args:
            roc (RocWebHandler, optional): _description_. Defaults to None.
            settings (UserSettings, optional): _description_. Not Required
            custom_settings (dict, optional): _description_. Not required

        Returns:
            dict: _description_
                Contains 'response' and either 'result' or 'error'
                'response': 'success' or 'failure'
                'error': Exists if response == 'failure', contains a
                    description of the error
                'result': Exists if response != 'failure', contains the
                    resulting ROCTraining object
        """
        bad_params_resp = cls.__check_params(roc, settings, custom_settings)
        if bad_params_resp:
            return bad_params_resp

        if not roc.is_logged_in():
            return {'response': 'failure', 'error': 'ROC is not logged in'}

        roc.go_to_training()
        resp = roc.get_response()

        if resp.status_code != 200:
            return {'response': 'failure', 'error':
                    'Received status code:{resp.status_code}'}

        soup = BeautifulSoup(resp, 'html.parser')

        counts = {}

        for name, id in _training_ids.items():
            item = soup.find(id=id)
            count = item.find('span', {'class': 'amount'})
            count = __get_amount(count)

            counts[name] = count

        result = ROCTraining(counts)

        return {'response': 'success', 'result': result}


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

        if not roc.is_logged_in():
            return {'response': 'failure', 'error': 'ROC is not logged in'}

        roc.go_to_armory()
        resp = roc.get_response()

        if resp.status_code != 200:
            return {'response': 'failure', 'error':
                    'Received status code:{resp.status_code}'}

        counts = {}
        soup = BeautifulSoup(resp, 'html.parser')
        for key, weapon in ALL_ITEM_DETAILS.items():
            code = weapon.code
            wepsoup = soup.find(id=f'weapon{code}')
            amount = int(wepsoup.find('span',
                                      {'class': 'amount'}).replace(',', ''))

            counts[key] = amount

        arm = ROCArmory(counts)

        return {'response': 'success', 'result': arm}


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
