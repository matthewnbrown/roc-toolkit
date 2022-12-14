
import abc
from rocalert.roc_settings import BuyerSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases.rocpurchtools \
    import ALL_ITEM_DETAILS as ITEM_DETAILS
from .models import ArmoryModel, ArmoryPurchaseModel


class ArmoryPurchaseError(Exception):
    pass


class ROCArmoryPurchaseGeneratorABC(abc.ABC):
    def generate_purchase(
            bsettings: BuyerSettings, gold: int, armmod: ArmoryModel
            ) -> ArmoryPurchaseModel:
        raise NotImplementedError


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

    def __make_armory_order(self, gold) -> dict:
        weaps = self.buyersettings.get_weapons_to_buy()
        return self.__create_order(weaps, gold)

    def __create_order(self, items, gold) -> dict:
        total = sum(items.values())

        netcost = 0

        for item, amt in items.items():
            if amt == 0:
                continue
            count = (gold // total * amt) // ITEM_DETAILS[item].cost
            netcost += ITEM_DETAILS[item].cost * amt
            items[item] = count

        if netcost > gold:
            print(items)
            raise ArmoryPurchaseError("Purchase cost of {netcost} is greater than gold ({gold})")
        return items

    def create_order_payload(self) -> dict:
        gold = self.roc.current_gold()
        order = self.__make_armory_order(gold)

        payload = BASE_ARMORY_PAYLOAD.copy()

        for item, count in order.items():
            payload[f"buy[{ITEM_DETAILS[item].code}]"] = str(count)

        return payload
