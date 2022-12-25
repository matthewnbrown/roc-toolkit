import unittest

import tests.mocks as mock
import rocalert.rocpurchases.roc_buyer as roc_buyer
from rocalert.rocpurchases.rocpurchtools \
    import ALL_ITEM_DETAILS as ITEM_DETAILS


class RocBuyerTests(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_purchase_should_be_required_when_enough_gold(self):
        roc = mock.RocWebHandler(current_gold=50000)
        buyersettings = mock.BuyerSettings(
            min_gold_to_buy=1,
            dagger=1)
        buyer = roc_buyer.ROCBuyer(roc, buyersettings)

        purchase_required = buyer.check_purchase_required()

        self.assertTrue(purchase_required)

    def test_purchase_should_notbe_required_when_not_enough_gold(self):
        roc = mock.RocWebHandler(current_gold=1000)
        buyersettings = mock.BuyerSettings(
            min_gold_to_buy=10000,
            dagger=1)
        buyer = roc_buyer.ROCBuyer(roc, buyersettings)

        purchase_required = buyer.check_purchase_required()

        self.assertFalse(purchase_required)

    def test_even_two_item_split_purchase_order(self):
        roc = mock.RocWebHandler(current_gold=3*10**8)
        buyersettings = mock.BuyerSettings(
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

    def test_low_gold_buying_blades_should_buy_nothing(self):
        roc = mock.RocWebHandler(current_gold=91929)
        buyersettings = mock.BuyerSettings(
            min_gold_to_buy=90000000,
            blade=1
        )

        buyer = roc_buyer.ROCBuyer(roc, buyersettings)
        payload = buyer.create_order_payload()

        self.assertEqual(payload[f"buy[{ITEM_DETAILS['blade'].code}]"], '0')


if __name__ == "__main__":
    unittest.main()
