import unittest
import dataclasses

from rocalert.rocpurchases import ROCTrainingPayloadCreator,\
    ROCTrainingWeaponMatchPurchaseCreator, ROCTrainingDumpPurchaseCreator, \
    SimpleRocTrainer
from rocalert.rocpurchases.models import TrainingPurchaseModel
from rocalert.pages.training import RocTrainingTableEntry
from rocalert.pages.genericpages import WeaponDistTableEntry


@dataclasses.dataclass
class MockWeaponTroopDistTable:
    att_dist: WeaponDistTableEntry = WeaponDistTableEntry(0, 0)
    def_dist: WeaponDistTableEntry = WeaponDistTableEntry(0, 0)
    spy_dist: WeaponDistTableEntry = WeaponDistTableEntry(0, 0)
    sent_dist: WeaponDistTableEntry = WeaponDistTableEntry(0, 0)

    @property
    def attack_wt_dist(self) -> WeaponDistTableEntry:
        return self.att_dist

    @property
    def defense_wt_dist(self) -> WeaponDistTableEntry:
        return self.def_dist

    @property
    def spy_wt_dist(self) -> WeaponDistTableEntry:
        return self.spy_dist

    @property
    def sentry_wt_dist(self) -> WeaponDistTableEntry:
        return self.sent_dist


@dataclasses.dataclass
class MockTrainingPage:
    gold: int = 0
    attacksoldiers: int = 0
    defensesoldiers: int = 0
    spiesamt: int = 0
    sentriesamt: int = 0
    untrained: int = 0
    attacksoldcost: int = 0
    defensesoldcost: int = 0
    spycost: int = 0
    sentrycost: int = 0
    attweps: int = 0
    defweps: int = 0
    spyweps: int = 0
    sentryweps: int = 0
    attmercs: int = 0
    defmercs: int = 0
    untrainedmercs: int = 0

    def __post_init__(self):
        self._weapondisttable = MockWeaponTroopDistTable(
            att_dist=WeaponDistTableEntry(self.attacksoldiers,
                                          self.attweps),
            def_dist=WeaponDistTableEntry(self.defensesoldiers, self.defweps),
            spy_dist=WeaponDistTableEntry(self.spyweps, self.spyweps),
            sent_dist=WeaponDistTableEntry(self.sentriesamt, self.sentrycost)
        )

    @property
    def weapon_distribution_table(self) -> MockWeaponTroopDistTable:
        return self._weapondisttable

    @property
    def attack_soldiers(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.attacksoldiers, 0)

    @property
    def defense_soldiers(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.defensesoldiers, 0)

    @property
    def defense_mercenaries(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.defmercs, 0)

    @property
    def untrained_soldiers(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.untrained, 0)

    @property
    def untrained_mercenaries(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.untrainedmercs, 0)

    @property
    def spies(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.spiesamt, 0)

    @property
    def sentries(self) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(self.sentriesamt, 0)

    @property
    def attack_sold_cost(self) -> int:
        return self.attacksoldcost

    @property
    def defense_sold_cost(self) -> int:
        return self.defensesoldcost

    @property
    def spy_sold_cost(self) -> int:
        return self.spycost

    @property
    def sentry_sold_cost(self) -> int:
        return self.sentrycost


class MockTrainingSettings():
    def __init__(
            self,
            train_soldiers: bool = True,
            sold_weapmatch: bool = False,
            sold_dumptype: str = 'none',
            sold_roundamt: int = 1000,
            min_purch_size: int = 1500,) -> None:
        self._train_soldiers = train_soldiers
        self._sold_weapmaptch = sold_weapmatch
        self._sold_dumptype = sold_dumptype
        self._sold_roundamt = sold_roundamt
        self._min_size = min_purch_size

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

    @property
    def min_training_size(self):
        return self._min_size


class ROCTrainingDumpPurchaseCreatorTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_training_disabled(self):
        mtp = MockTrainingPage(
            gold=10**8,
            untrained=1000,
            attweps=1000
        )

        tset = MockTrainingSettings(False, True, 'defense')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be purchased when training disabled'
        )

    def test_no_soldiers_avail(self):
        mtp = MockTrainingPage(
            gold=10**6,
            )

        tset = MockTrainingSettings(True, True, 'attack', 100)

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Should not buy any soldiers when there are no untrained available'
        )

    def test_no_gold_dump(self):
        mtp = MockTrainingPage(
            untrained=1000
        )

        tset = MockTrainingSettings(True, False, 'defense')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.defense_soldiers,
            0,
            'No soldiers should be bought when no gold is available'
        )

    def test_defense_soldier_dump(self):
        mtp = MockTrainingPage(
            gold=10**6,
            untrained=1000,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000
        )

        tset = MockTrainingSettings(True, False, 'defense')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 1000, 0, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_attack_soldier_dump(self):
        mtp = MockTrainingPage(
            gold=10**6,
            untrained=1000,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000,
        )

        tset = MockTrainingSettings(True, False, 'attack')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (1000, 0, 0, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_spy_soldier_dump(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000
        )

        tset = MockTrainingSettings(True, False, 'spies')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 1000),
            'Only the specified soldier type should be dumped to'
        )

    def test_sentry_soldier_dump(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000
        )

        tset = MockTrainingSettings(True, False, 'sentries')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 1000, 0),
            'Only the specified soldier type should be dumped to'
        )

    def test_gold_shortage(self):
        mtp = MockTrainingPage(
            gold=70500,
            untrained=1000,
            defensesoldcost=1000
        )

        tset = MockTrainingSettings(True, False, 'defense')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.defense_soldiers,
            70,
            'No soldiers should be bought when no gold is available'
        )

    def test_cost_calculation(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=100,
            defensesoldcost=1500
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=False, sold_dumptype='defense')

        tpmod = ROCTrainingDumpPurchaseCreator.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.cost,
            mtp.untrained_soldiers.count * mtp.defense_sold_cost,
            'The cost of a purchase should be properly calculated'
        )


class ROCTrainingWeaponMatchPurchaseCreatorTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.purchasecreater = ROCTrainingWeaponMatchPurchaseCreator

    def test_training_disabled(self):
        mtp = MockTrainingPage(
            gold=10**8,
            untrained=1000,
            attweps=1000
        )

        tset = MockTrainingSettings(False, True, 'defense')

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be purchased when training disabled'
        )

    def test_no_soldiers_avail(self):
        mtp = MockTrainingPage(
            gold=10**6,
            attweps=10000
        )

        tset = MockTrainingSettings(True, True, 'attack', 100)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Should not buy any soldiers when there are no untrained available'
        )

    def test_no_untrained_to_match(self):
        mtp = MockTrainingPage(
            gold=10**6,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000,
            attweps=10000,
        )

        tset = MockTrainingSettings(True, True)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
                tpmod.sentries, tpmod.spies),
            (0, 0, 0, 0),
            'No soldiers should be dumped when no untrained are available'
        )

    def test_soldier_matching_excess_weapons(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldiers=50,
            attacksoldcost=1000,
            attweps=10000,
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            1000,
            'Soldier matching should buyout all untrained when excess weapons'
        )

    def test_soldier_matching_gold_shortage(self):
        mtp = MockTrainingPage(
            gold=50000,
            untrained=1000,
            attacksoldcost=1000,
            attweps=100,
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            50,
            'Soldier matching should not buy more soldiers than it can afford'
        )

    def test_matching_spies_gold_shortage(self):
        mtp = MockTrainingPage(
            gold=50000,
            untrained=1000,
            spycost=2000,
            spyweps=100,
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.spies,
            25,
            'Spy matching should not buy more soldiers than it can afford'
        )

    def test_soldier_match_excess_soldiers(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            attacksoldiers=1000,
            attweps=500
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            0,
            'Soldier matching should not buy weapons when unneeded'
        )

    def test_all_soldier_match(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            defensesoldcost=1000,
            spycost=2000,
            sentrycost=2000,
            attweps=250,
            defweps=250,
            spyweps=250,
            sentryweps=200
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers,
             tpmod.spies, tpmod.sentries),
            (250, 250, 250, 250),
            'Soldier matching should match all soldier types'
        )

    def test_soldier_rounding(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            attweps=125
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=50)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers),
            (150, 0),
            'Soldier matching should match and there is no excess to dump'
        )

    def test_soldier_rounding_one(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1000,
            attweps=125
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertTupleEqual(
            (tpmod.attack_soldiers, tpmod.defense_soldiers),
            (125, 0),
            'Soldier matching should match and there is no excess to dump'
        )

    def test_gold_shortage(self):
        mtp = MockTrainingPage(
            gold=125678,
            untrained=1000,
            attacksoldcost=1000,
            attweps=5000
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.attack_soldiers,
            125,
            'When limited by gold, as many soldiers as possible' +
            ' should be bought'
        )

    def test_cost_calculation(self):
        mtp = MockTrainingPage(
            gold=10**7,
            untrained=4,
            attacksoldcost=1000,
            defensesoldcost=1500,
            spycost=2000,
            sentrycost=2500,
            attweps=1,
            defweps=1,
            spyweps=1,
            sentryweps=1
        )

        tset = MockTrainingSettings(
            True, sold_weapmatch=True, sold_roundamt=1)

        tpmod = self.purchasecreater.create_purchase(
            tset, mtp, mtp.gold
        )

        self.assertEqual(
            tpmod.cost,
            mtp.attack_sold_cost
            + mtp.defense_sold_cost
            + mtp.spy_sold_cost
            + mtp.sentry_sold_cost,
            'The cost of a purchase should be properly calculated'
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


class SimpleRocTrainerTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.trainertype = SimpleRocTrainer
        self._PAYLOAD_SIZE = 14

    def test_payload_size_disabled_training(self):
        tset = MockTrainingSettings(
            False, True, 'attack', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        self.assertEqual(
            len(respayload),
            self._PAYLOAD_SIZE,
            'Payload should have correct number of items'
        )

    def test_payload_size_dump(self):
        tset = MockTrainingSettings(
            True, False, 'attack', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        self.assertEqual(
            len(respayload),
            self._PAYLOAD_SIZE,
            'Payload should have correct number of items'
        )

    def test_payload_size_soldmatch(self):
        tset = MockTrainingSettings(
            True, True, 'none', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        self.assertEqual(
            len(respayload),
            self._PAYLOAD_SIZE,
            'Payload should have correct number of items'
        )

    def test_training_disabled(self):
        tset = MockTrainingSettings(
            False, True, 'attack', 1000)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        for _, val in respayload.items():
            self.assertEqual(
                len(val),
                0,
                'Payload vals should be empty when user has insufficient gold'
            )

    def test_payload_vals_dump(self):
        tset = MockTrainingSettings(
            True, False, 'attack', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=0)

        respayload = trainer.gen_purchase_payload(tpage)

        count_empty = sum(1 for val in respayload.values() if len(val) == 0)

        self.assertEqual(
            count_empty,
            self._PAYLOAD_SIZE - 1,
            'Payload should have correct number of items'
        )

        self.assertEqual(
            respayload['train[attack_soldiers]'],
            '1000',
            'Payload should contain correct amount of soldiers to buy'
        )

    def test_payload_vals_match(self):
        tset = MockTrainingSettings(
            True, True, 'none', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        count_empty = sum(1 for val in respayload.values() if len(val) == 0)

        self.assertEqual(
            count_empty,
            self._PAYLOAD_SIZE - 1,
            'Payload should have correct number of items'
        )

        self.assertEqual(
            respayload['train[attack_soldiers]'],
            '1000',
            'Payload should contain correct amount of soldiers to buy'
        )

    def test_payload_vals_dumpmatch_nonetodump(self):
        tset = MockTrainingSettings(
            True, True, 'defense', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1000,
            attacksoldcost=1,
            defensesoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        count_empty = sum(1 for val in respayload.values() if len(val) == 0)

        self.assertEqual(
            count_empty,
            self._PAYLOAD_SIZE - 1,
            'Payload should have correct number of items'
        )

        self.assertEqual(
            respayload['train[attack_soldiers]'],
            '1000',
            'Payload should contain correct amount of soldiers to buy'
        )

        self.assertEqual(
            respayload['train[defense_soldiers]'],
            '',
            'Payload should contain correct amount of soldiers to buy'
        )

    def test_payload_vals_dumpmatch(self):
        tset = MockTrainingSettings(
            True, True, 'defense', 1000, 0)
        trainer = self.trainertype(tset)
        tpage = MockTrainingPage(
            gold=10**7,
            untrained=1500,
            attacksoldcost=1,
            defensesoldcost=1,
            attweps=1000)

        respayload = trainer.gen_purchase_payload(tpage)

        count_empty = sum(1 for val in respayload.values() if len(val) == 0)

        self.assertEqual(
            count_empty,
            self._PAYLOAD_SIZE - 2,
            'Payload should have correct number of items'
        )

        self.assertEqual(
            respayload['train[attack_soldiers]'],
            '1000',
            'Payload should contain correct amount of soldiers to buy'
        )

        self.assertEqual(
            respayload['train[defense_soldiers]'],
            '500',
            'Payload should contain correct amount of soldiers to buy'
        )

    def test_training_not_reqd_training_disabled(self):
        tset = MockTrainingSettings(
            False, True, 'attack', min_purch_size=1
        )

        trainer = self.trainertype(tset)

        tpage = MockTrainingPage(
            gold=10**7,
            untrained=10000,
            attweps=1000,
            attacksoldcost=1,
            defensesoldcost=1)

        reqd = trainer.is_training_required(tpage=tpage)

        self.assertFalse(reqd)

    def test_training_reqd_dump(self):
        tset = MockTrainingSettings(
            True, False, 'attack', min_purch_size=1
        )

        trainer = self.trainertype(tset)

        tpage = MockTrainingPage(
            gold=10**7,
            untrained=10000,
            attweps=1000,
            attacksoldcost=1,
            defensesoldcost=1)

        reqd = trainer.is_training_required(tpage=tpage)

        self.assertTrue(reqd)

    def test_training_reqd_match(self):
        tset = MockTrainingSettings(
            True, True, 'none', min_purch_size=1
        )

        trainer = self.trainertype(tset)

        tpage = MockTrainingPage(
            gold=10**7,
            untrained=10000,
            attweps=1000,
            attacksoldcost=1,
            defensesoldcost=1)

        reqd = trainer.is_training_required(tpage=tpage)

        self.assertTrue(reqd)

    def test_training_notreqd_too_poor(self):
        tset = MockTrainingSettings(
            True, True, 'attack', min_purch_size=1000
        )

        trainer = self.trainertype(tset)

        tpage = MockTrainingPage(
            gold=60000,
            untrained=10000,
            attweps=1000,
            attacksoldcost=1000)

        reqd = trainer.is_training_required(tpage=tpage)

        self.assertFalse(reqd)

    def test_training_notreqd_toofew_untrained(self):
        tset = MockTrainingSettings(
            False, True, 'attack', min_purch_size=1000
        )

        trainer = self.trainertype(tset)

        tpage = MockTrainingPage(
            gold=10**7,
            untrained=500,
            attweps=1000,
            attacksoldcost=1,
            defensesoldcost=1)

        reqd = trainer.is_training_required(tpage=tpage)

        self.assertFalse(reqd)


if __name__ == "__main__":
    unittest.main()
