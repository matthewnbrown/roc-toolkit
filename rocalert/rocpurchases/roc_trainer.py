from ..roc_web_handler import RocWebHandler
from ..roc_settings import TrainerSettings


def _gen_basetrainpayload():
    soldtypes = ['attack_soldiers', 'defense_soldiers', 'spies', 'sentries']
    merctypes = ['attack_mercs', 'defense_mercs', 'untrained_mercs']

    res = {f'train[{stype}]': '' for stype in soldtypes}
    for merctype in merctypes:
        res[f'buy[{merctype}]'] = ''

    for stype in soldtypes+merctypes:
        res[f'untrain[{stype}]'] = ''


_BASE_TRAIN_PAYLOAD = _gen_basetrainpayload()


class ROCTrainer:
    def __init__(
            self,
            roc_handler: RocWebHandler,
            trainersettings: TrainerSettings
            ) -> None:
        if roc_handler is None:
            raise Exception("Parameter roc_handler must not be None")
        elif trainersettings is None:
            raise Exception('Parameter trainersettings must not be None')

        self.roc = roc_handler
        self.trainersettings = trainersettings

    def __make_order(gold) -> dict[str, int]:
        pass

    def purchase_required(self, current_gold: int, account_details):
        ts = self.trainersettings
        if (not ts.training_enabled
                or ts.soldier_dump_type != ts.SoldierTypes.NONE):
            return False

        return ts.soldier_dump_type

    def create_order_payload(self, gold):
        order = self.__make_order__(gold)
        payload = _BASE_TRAIN_PAYLOAD.copy()

        for item, count in order.items():
            payload[item] = str(count)
