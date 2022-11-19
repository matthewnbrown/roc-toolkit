import unittest

from rocalert.rocpurchases import ROCTrainingPayloadCreator,\
    ROCTrainingWeaponMatchPurchaseCreator, ROCTrainingDumpPurchaseCreator
from rocalert.rocpurchases.models import ArmoryModel,\
    TrainingModel, TrainingPurchaseModel, ItemCostPair as ICP


class MockTrainingSettings():
    def __init__(
            self,
            train_soldiers: bool = True,
            sold_weapmatch: bool = False,
            sold_dumptype: str = 'none',
            sold_roundamt: int = 1000) -> None:
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


class ROCTrainingDumpPurchaseCreatorTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._att_cost = 1000
        self._def_cost = 1000
        self._spy_cost = 2000
        self._spy_cost = 2000

    def test_training_disabled(self):
        tm = TrainingModel(untrained_soldiers=ICP(1000))
        am = ArmoryModel(dagger=ICP(1000))
        tset = MockTrainingSettings(False, True, 'defense')
        gold = 10**8

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be purchased when training disabled'
        )

    def test_no_soldiers_avail(self):
        tm = TrainingModel()
        am = ArmoryModel(excalibur=ICP(10000, 10))
        tset = MockTrainingSettings(True, True, 'attack', 100)
        gold = 10**6

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Should not buy any soldiers when there are no untrained available'
        )

    def test_no_gold_dump(self):
        tm = TrainingModel(untrained_soldiers=ICP(1000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'defense')
        gold = 0

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.defense_soldiers,
            0,
            'No soldiers should be bought when no gold is available'
        )

    def test_defense_soldier_dump(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000), defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000), sentries=ICP(0, 2000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'defense')
        gold = 10**6

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 1000, 0, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_attack_soldier_dump(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000), defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000), sentries=ICP(0, 2000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'attack')
        gold = 10**6

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (1000, 0, 0, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_spy_soldier_dump(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000), defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000), sentries=ICP(0, 2000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'spies')
        gold = 10**7

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 1000),
            'Only the specified soldier type should be dumped to'
        )

    def test_sentry_soldier_dump(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000), defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000), sentries=ICP(0, 2000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'sentries')
        gold = 10**7

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 1000, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_gold_shortage(self):
        tm = TrainingModel(untrained_soldiers=ICP(1000))
        am = ArmoryModel()
        tset = MockTrainingSettings(True, False, 'defense')
        gold = 70500

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.defense_soldiers,
            70,
            'No soldiers should be bought when no gold is available'
        )


class ROCTrainingWeaponMatchPurchaseCreatorTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._att_cost = 1000
        self._def_cost = 1000
        self._spy_cost = 2000
        self._spy_cost = 2000

    def test_training_disabled(self):
        tm = TrainingModel(untrained_soldiers=ICP(1000))
        am = ArmoryModel(dagger=ICP(1000))
        tset = MockTrainingSettings(False, True, 'defense')
        gold = 10**8

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be purchased when training disabled'
        )

    def test_no_soldiers_avail(self):
        tm = TrainingModel()
        am = ArmoryModel(excalibur=ICP(10000, 10))
        tset = MockTrainingSettings(True, True, 'attack', 100)
        gold = 10**6

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Should not buy any soldiers when there are no untrained available'
        )

    def test_no_untrained_to_match(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(0),
            attack_soldiers=ICP(0, 1000), defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000), sentries=ICP(0, 2000))
        am = ArmoryModel(dagger=ICP(10000))
        tset = MockTrainingSettings(True, True)
        gold = 10**6

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be dumped when no untrained are available'
        )

    def test_soldier_matching_excess_weapons(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(50, 1000))
        am = ArmoryModel(dagger=ICP(10000, 10))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True)
        gold = 10**7

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            1000,
            'Soldier matching should buyout all untrained when excess weapons'
        )

    def test_soldier_matching_gold_shortage(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000))
        am = ArmoryModel(dagger=ICP(100, 50))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True)
        gold = 50000

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            50,
            'Soldier matching should not buy more soldiers than it can afford'
        )

    def test_soldier_match_excess_soldiers(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(1000, 1000))
        am = ArmoryModel(dagger=ICP(500, 10))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True)
        gold = 10**7

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Soldier matching should not buy weapons when unneeded'
        )

    def test_all_soldier_match(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000),
            defense_soldiers=ICP(0, 1000),
            spies=ICP(0, 2000),
            sentries=ICP(0, 2000))
        am = ArmoryModel(
            dagger=ICP(250), shield=ICP(250),
            hook=ICP(250), guard_dog=ICP(250))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)
        gold = 10**7

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
             tpmod.spies, tpmod.sentries),
            (250, 250, 250, 250),
            'Soldier matching should match all soldier types'
        )

    def test_soldier_rounding(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000))
        am = ArmoryModel(dagger=ICP(125, 10))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=50)
        gold = 10**7

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers),
            (150, 0),
            'Soldier matching should match and there is no excess to dump'
        )

    def test_soldier_rounding_one(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000))
        am = ArmoryModel(dagger=ICP(125, 10))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)
        gold = 10**7

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers),
            (125, 0),
            'Soldier matching should match and there is no excess to dump'
        )

    def test_gold_shortage(self):
        tm = TrainingModel(
            untrained_soldiers=ICP(1000),
            attack_soldiers=ICP(0, 1000))
        am = ArmoryModel(dagger=ICP(5000, 10))
        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)
        gold = 125678

        tpmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
            tset, gold, tm, am)

        self.assertEqual(
            tpmod.attack_soldiers,
            125,
            'When limited by gold, as many soldiers as possible' +
            ' should be bought'
        )


class ROCTrainingPayloadCreatorTest(unittest.TestCase):
    def test_empty_purchase(self):
        purchase = TrainingPurchaseModel()

        payload = ROCTrainingPayloadCreator.create_training_payload(purchase)

        for _, val in payload.items():
            self.assertEqual(
                val,
                '',
                'Payload should be empty and purchase contains nothing.'
            )

    def test_number_of_items(self):
        purchase = TrainingPurchaseModel()

        payload = ROCTrainingPayloadCreator.create_training_payload(purchase)

        self.assertEqual(
            len(payload),
            14,
            'Payload should contain correct number of items'
        )

    def test_all_items(self):
        purchase = TrainingPurchaseModel(
            attack_soldiers=1,
            defense_soldiers=2,
            spies=3,
            sentries=4,
            attack_mercs=5,
            defense_mercs=6,
            untrained_mercs=7,
            sell_attack_soldiers=8,
            sell_defense_soldiers=9,
            sell_spies=10,
            sell_sentries=11,
            sell_attack_mercs=12,
            sell_defense_mercs=13,
            sell_untrained_mercs=14
        )

        payload = ROCTrainingPayloadCreator.create_training_payload(purchase)
        self.maxDiff = 2000

        self.assertDictEqual(
            payload,
            {
                'train[attack_soldiers]': '1',
                'train[defense_soldiers]': '2',
                'train[spies]': '3',
                'train[sentries]': '4',
                'buy[attack_mercs]': '5',
                'buy[defense_mercs]': '6',
                'buy[untrained_mercs]': '7',
                'untrain[attack_soldiers]': '8',
                'untrain[defense_soldiers]': '9',
                'untrain[spies]': '10',
                'untrain[sentries]': '11',
                'untrain[attack_mercs]': '12',
                'untrain[defense_mercs]': '13',
                'untrain[untrained_mercs]': '14'
            },
            'Payload should contain expected values'
        )


if __name__ == "__main__":
    unittest.main()
