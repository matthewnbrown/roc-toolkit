import unittest

import rocalert.rocpurchases.roc_buyer as roc_buyer
from rocalert.rocpurchases.rocpurchtools \
    import ALL_ITEM_DETAILS as ITEM_DETAILS


class MockRocWebHandler:
    def __init__(self, current_gold=None,) -> None:
        self._currentgold = current_gold

    def current_gold(self) -> int:
        if self._currentgold is None:
            raise ValueError('Gold value was not set')

        return self._currentgold


class MockBuyerSettings:
    def __init__(
            self,
            min_gold_to_buy=None,
            buying_enabled=True,
            dagger=0, maul=0, blade=0, excalibur=0,
            cloak=0, hook=0, pickaxe=0, sai=0,
            shield=0, mithril=0, dragonskin=0,
            horn=0, guard_dog=0, torch=0
            ) -> None:
        self._minbuygold = min_gold_to_buy
        self._buyingenabled = buying_enabled
        self._weaponbuydict = {
            'dagger': dagger, "maul": maul,
            "blade": blade, "excalibur": excalibur,
            "cloak": cloak, "hook": hook, "pickaxe": pickaxe,
            "sai": sai, "shield": shield, "mithril": mithril,
            "dragonskin": dragonskin, "horn": horn, "guard_dog": guard_dog,
            "torch": torch
        }

    def min_gold_to_buy(self) -> int:
        if self._minbuygold is None:
            raise ValueError("Min gold not set")
        return self._minbuygold

    def get_weapons_to_buy(self) -> dict[str, int]:
        d = {}
        for settingid, setting in self._weaponbuydict.items():
            if settingid != 'buy_weapons' and settingid != 'min_gold' \
                    and setting > 0:
                d[settingid] = setting
        return d

    def buying_enabled(self) -> bool:
        return self._buyingenabled


class RocBuyerTests(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_purchase_should_be_required_when_enough_gold(self):
        roc = MockRocWebHandler(current_gold=50000)
        buyersettings = MockBuyerSettings(
            min_gold_to_buy=1,
            dagger=1)
        buyer = roc_buyer.ROCBuyer(roc, buyersettings)

        purchase_required = buyer.check_purchase_required()

        self.assertTrue(purchase_required)

    def test_purchase_should_notbe_required_when_not_enough_gold(self):
        roc = MockRocWebHandler(current_gold=1000)
        buyersettings = MockBuyerSettings(
            min_gold_to_buy=10000,
            dagger=1)
        buyer = roc_buyer.ROCBuyer(roc, buyersettings)

        purchase_required = buyer.check_purchase_required()

        self.assertFalse(purchase_required)

    def test_even_two_item_split_purchase_order(self):
        roc = MockRocWebHandler(current_gold=3*10**8)
        buyersettings = MockBuyerSettings(
            min_gold_to_buy=1,
            mithril=8,
            hook=2
        )
        buyer = roc_buyer.ROCBuyer(roc, buyersettings)

        payload = buyer.create_order_payload()

        self.assertTupleEqual(
            (payload[f"buy[{ITEM_DETAILS['mithril'].code}]"],
                payload[f"buy[{ITEM_DETAILS['hook'].code}]"]),
            ('1200', '600')
        )


if __name__ == "__main__":
    unittest.main()
