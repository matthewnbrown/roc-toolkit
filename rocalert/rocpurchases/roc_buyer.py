
from rocalert.roc_settings.settingstools import BuyerSettings, TrainerSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases.rocpurchtools \
    import ALL_ITEM_DETAILS as ITEM_DETAILS
from abc import abstractclassmethod

BASE_ARMORY_PAYLOAD = {
    'sell[7]': '',
    'sell[8]': '',
    'sell[11]': '',
    'sell[13]': '',
    'sell[14]': '',
    }
for i in range(1, 15):
    k = 'buy[{}]'.format(str(i))
    BASE_ARMORY_PAYLOAD[k] = ''


def gen_basetrainpayload():
    soldtypes = ['attack_soldiers', 'defense_soldiers', 'spies', 'sentries']
    merctypes = ['attack_mercs', 'defense_mercs', 'untrained_mercs']

    res = {f'train[{stype}]': '' for stype in soldtypes}
    for merctype in merctypes:
        res[f'buy[{merctype}]'] = ''

    for stype in soldtypes+merctypes:
        res[f'untrain[{stype}]'] = ''


BASE_TRAIN_PAYLOAD = gen_basetrainpayload()


class ROCPurchaser():
    """Generic class for a ROC purchasing tool"""

    """Checks if purchase condition is met"""
    @abstractclassmethod
    def check_purchase_required(
            self,
            roc: RocWebHandler = None,
            settings: BuyerSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError

    """Creates purchase order dictionary"""
    @abstractclassmethod
    def __create_order(self, items, gold) -> dict:
        raise NotImplementedError

    """Creates payload for purchase request"""
    @abstractclassmethod
    def create_order_payload(self) -> dict:
        raise NotImplementedError


class ROCBuyer():
    def __init__(
            self,
            roc_handler: RocWebHandler,
            buyersettings: BuyerSettings
            ) -> None:
        if roc_handler is None:
            raise Exception("Parameter roc_handler must not be None")

        self.roc = roc_handler
        self.buyersettings = buyersettings

    def check_purchase_required(self) -> bool:
        if not self.buyersettings.buying_enabled():
            return False

        gold = self.roc.current_gold()
        return gold >= self.buyersettings.min_gold_to_buy()

    def __make_soldier_order(self, gold) -> dict:
        pass

    def __make_armory_order(self, gold) -> dict:
        weaps = self.buyersettings.get_weapons_to_buy()
        return self.__create_order(weaps, gold)

    def __create_order(self, items, gold) -> dict:
        total = sum(items.values())

        for item, amt in items.items():
            if amt == 0:
                continue
            count = (gold // total * amt) // ITEM_DETAILS[item].cost
            gold -= count * ITEM_DETAILS[item].cost
            total -= amt
            items[item] = count

        return items

    def create_order_payload(self) -> dict:
        gold = self.roc.current_gold()
        order = self.__make_armory_order(gold)

        payload = BASE_ARMORY_PAYLOAD.copy()

        for item, count in order.items():
            payload[f"buy[{ITEM_DETAILS[item].code}]"] = str(count)

        return payload


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

        return ts.soldier_dump

    def create_order_payload(self, gold):
        order = self.__make_order__(gold)
        payload = BASE_TRAIN_PAYLOAD.copy()

        for item, count in order.items():
            payload[item] = str(count)
