
from rocalert.roc_settings.settingstools import BuyerSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases.rocpurchtools import RocItem

BASE_PAYLOAD = {
    'sell[7]': '',
    'sell[8]': '',
    'sell[11]': '',
    'sell[13]': '',
    'sell[14]': '',
    }
for i in range(1, 15):
    k = 'buy[{}]'.format(str(i))
    BASE_PAYLOAD[k] = ''

ITEM_DETAILS = {
    'dagger': RocItem('Dagger', 1000, 30, RocItem.ItemType.ATTACK, 1),
    'maul': RocItem('Maul', 15000, 300, RocItem.ItemType.ATTACK, 2),
    'blade': RocItem('Blade', 200000, 3000, RocItem.ItemType.ATTACK, 3),
    'excalibur': RocItem('Excalibur', 1000000, 12000,
                         RocItem.ItemType.ATTACK, 4),
    'cloak': RocItem('Cloak', 50000, 30, RocItem.ItemType.SPY, 9),
    'hook': RocItem('Hook', 100000, 50, RocItem.ItemType.SPY, 10),
    'pickaxe': RocItem('Pickaxe', 300000, 120, RocItem.ItemType.SPY, 11),
    'sai': RocItem('Sai', 1000, 30, RocItem.ItemType.DEFENSE, 5),
    'shield': RocItem('Shield', 15000, 300, RocItem.ItemType.DEFENSE, 6),
    'mithril': RocItem('Mithril', 200000, 3000, RocItem.ItemType.DEFENSE, 7),
    'dragonskin': RocItem('Dragonskin', 1000000, 12000,
                          RocItem.ItemType.DEFENSE, 8),
    'horn': RocItem('Horn', 50000, 30, RocItem.ItemType.SENTRY, 12),
    'guard_dog': RocItem('Guard Dog', 100000, 50, RocItem.ItemType.SENTRY, 13),
    'torch': RocItem('Torch', 300000, 120, RocItem.ItemType.SENTRY, 14)
}


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

        payload = BASE_PAYLOAD.copy()

        for item, count in order.items():
            payload[f"buy[{ITEM_DETAILS[item].code}]"] = str(count)

        return payload


class ROCTrainer():
    def __init__(
            self,
            roc_handler: RocWebHandler,
            buyersettings: BuyerSettings
            ) -> None:
        if roc_handler is None:
            raise Exception("Parameter roc_handler must not be None")

        self.roc = roc_handler
        self.buyersettings = buyersettings