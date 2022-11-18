import unittest

from rocalert.rocpurchases import ROCTrainingPayloadCreator,\
    ROCTrainingPurchaseCreator
from rocalert.rocpurchases.models import ArmoryModel,\
    TrainingModel, TrainingPurchaseModel, ItemCostPair as ICP


class MockTrainingSettings():
    def __init__(
            self,
            train_soldiers: bool = True,
            sold_weapmatch: bool = False,
            sold_dumptype: str = 'attack',
            sold_roundamt: int = 100) -> None:
        self._train_soldiers = train_soldiers
        self._sold_weapmaptch = sold_weapmatch
        self._sold_dumptype = sold_dumptype
        self._sold_roundamt = sold_roundamt

    @property
    def training_enabled(self):
        return self._train_soldiers

    @property
    def match_soldiers_to_weapons(self):
        return self._sold_weapmaptch

    @property
    def soldier_dump_type(self):
        return self._sold_dumptype

    @property
    def soldier_round_amount(self):
        return self._sold_roundamt


class ROCTrainingPurchaseCreatorTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._att_cost = 1000
        self._def_cost = 1000
        self._spy_cost = 2000
        self._spy_cost = 2000

    def test_no_soldiers_true(self):
        tm = TrainingModel()
        am = ArmoryModel(excalibur=ICP(10000, 10))
        tset = MockTrainingSettings(True, True, 'attack', 100)
        gold = 10**6

        tpmod = ROCTrainingPurchaseCreator.create_purchase(tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Should not buy any soldiers when no untrained available'
        )


if __name__ == "__main__":
    unittest.main()
