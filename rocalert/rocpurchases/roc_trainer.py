import abc

from ..roc_settings import TrainerSettings
from rocalert.rocpurchases.models import TrainingPurchaseModel
import rocalert.pages as pages


class ROCTrainingPayloadCreatorABC(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def create_training_payload(tpm: TrainingPurchaseModel):
        raise NotImplementedError


class ROCTrainingPurchaseCreatorABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            tpage: pages.RocTrainingPage,
            gold: int
            ) -> TrainingPurchaseModel:
        raise NotImplementedError


class ROCTrainerABC(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        super().__init__()
        raise NotImplementedError

    @abc.abstractmethod
    def is_training_required(
            self,
            tpage: pages.RocTrainingPage,
            ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def gen_purchase_payload(
            self,
            tpage: pages.RocTrainingPage,
            ) -> dict[str, str]:
        raise NotImplementedError


class ROCTrainingPayloadCreator(ROCTrainingPayloadCreatorABC):
    def _get_count_str(count: int):
        return str(count) if count != 0 else ''

    @staticmethod
    def create_training_payload(tpm: TrainingPurchaseModel):
        gts = ROCTrainingPayloadCreator._get_count_str
        return {
            'train[attack_soldiers]': gts(tpm.attack_soldiers),
            'train[defense_soldiers]': gts(tpm.defense_soldiers),
            'train[spies]': gts(tpm.spies),
            'train[sentries]': gts(tpm.sentries),
            'buy[attack_mercs]': gts(tpm.attack_mercs),
            'buy[defense_mercs]': gts(tpm.defense_mercs),
            'buy[untrained_mercs]': gts(tpm.untrained_mercs),
            'untrain[attack_soldiers]': gts(tpm.sell_attack_soldiers),
            'untrain[defense_soldiers]': gts(tpm.sell_defense_soldiers),
            'untrain[spies]': gts(tpm.sell_spies),
            'untrain[sentries]': gts(tpm.sell_sentries),
            'untrain[attack_mercs]': gts(tpm.sell_attack_mercs),
            'untrain[defense_mercs]': gts(tpm.sell_defense_mercs),
            'untrain[untrained_mercs]': gts(tpm.sell_untrained_mercs),
        }


class ROCTrainingDumpPurchaseCreator(ROCTrainingPurchaseCreatorABC):
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            tpage: pages.RocTrainingPage,
            gold: int
            ) -> TrainingPurchaseModel:
        if not tsettings.training_enabled or gold <= 0:
            return TrainingPurchaseModel()

        solddumptype = tsettings.soldier_dump_type

        purchase_counts = {
            'attack': 0,
            'defense': 0,
            'spies': 0,
            'sentries': 0
        }
        cost = 0
        if solddumptype == 'attack':
            cost = tpage.attack_sold_cost
        elif solddumptype == 'defense':
            cost = tpage.defense_sold_cost
        elif solddumptype == 'spies':
            cost = tpage.spy_sold_cost
        elif solddumptype == 'sentries':
            cost = tpage.sentry_sold_cost

        if cost <= 0:
            return TrainingPurchaseModel()

        purchamt = min(tpage.untrained_soldiers.count, gold//cost)

        purchase_counts[solddumptype] += purchamt

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * tpage.attack_sold_cost
            + tpm.defense_soldiers * tpage.defense_sold_cost
            + tpm.spies * tpage.spy_sold_cost
            + tpm.sentries * tpage.sentry_sold_cost
        )

        return tpm


class ROCTrainingWeaponMatchPurchaseCreator(ROCTrainingPurchaseCreatorABC):
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            tpage: pages.RocTrainingPage,
            gold: int
            ) -> TrainingPurchaseModel:

        if not tsettings.training_enabled or gold <= 0:
            return TrainingPurchaseModel()

        skipmatch = {}

        purchase_counts = {
            'attack': 0,
            'defense': 0,
            'spies': 0,
            'sentries': 0
        }

        if tsettings.match_soldiers_to_weapons:
            gold = cls._soldier_match(
                purchase_counts, gold, skipmatch,
                tsettings.soldier_round_amount,
                tpage)

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * tpage.attack_sold_cost
            + tpm.defense_soldiers * tpage.defense_sold_cost
            + tpm.spies * tpage.spy_sold_cost
            + tpm.sentries * tpage.sentry_sold_cost
        )

        return tpm

    @classmethod
    def _soldier_match(
            cls,
            cur_purch: dict[str, int],
            gold: int,
            skip_match: set[str],
            roundamt: int,
            tpage: pages.RocTrainingPage
            ) -> int:

        untrained = tpage.untrained_soldiers.count
        attweps = tpage.weapon_distribution_table.attack_wt_dist.weapon_count
        defweps = tpage.weapon_distribution_table.defense_wt_dist.weapon_count
        spyweps = tpage.weapon_distribution_table.spy_wt_dist.weapon_count
        sentweps = tpage.weapon_distribution_table.sentry_wt_dist.weapon_count

        if 'attack' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, attweps, roundamt,
                tpage.attack_soldiers.count,
                tpage.attack_sold_cost,
                untrained)
            cur_purch['attack'] += amt
            untrained -= amt
            gold -= netcost

        if 'defense' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, defweps, roundamt,
                tpage.defense_soldiers.count,
                tpage.defense_sold_cost,
                untrained)
            cur_purch['defense'] += amt
            untrained -= amt
            gold -= netcost

        if 'spy' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, spyweps, roundamt,
                tpage.spies.count,
                tpage.spy_sold_cost,
                untrained)
            cur_purch['spies'] += amt
            untrained -= amt
            gold -= netcost

        if 'sentries' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, sentweps, roundamt,
                tpage.sentries.count,
                tpage.sentry_sold_cost,
                untrained)
            cur_purch['sentries'] += amt
            untrained -= amt
            gold -= netcost

        return gold

    @classmethod
    def _calc_soldier_match(
            cls,
            gold: int, weapons: int, roundamt: int,
            soldiers: int, soldiercost: int,
            untrainedsold: int
            ) -> tuple[int, int]:

        if soldiercost <= 0:
            return (0, 0)

        reqamt = weapons - soldiers
        if reqamt <= 0:
            return (0, 0)

        if reqamt % roundamt == 0:
            desiredamt = reqamt
        else:
            desiredamt = reqamt + roundamt - reqamt % roundamt

        purchamt = min(desiredamt, gold//soldiercost, untrainedsold)
        netcost = purchamt * soldiercost

        return (purchamt, netcost)


class SimpleRocTrainer(ROCTrainerABC):
    def __init__(
            self,
            tsettings: TrainerSettings,
            ) -> None:
        self._tsettings = tsettings
        self._converter = None

    def is_training_required(
            self,
            tpage: pages.RocTrainingPage
            ) -> bool:

        gold = tpage.gold

        if gold <= 0 or tpage is None or tpage.untrained_soldiers.count == 0\
                or not self._tsettings.training_enabled:
            return False

        return True

    def gen_purchase_payload(
            self,
            tpage: pages.RocTrainingPage
            ) -> dict[str, str]:

        pmod = TrainingPurchaseModel()

        if tpage is None or tpage.gold == 0 \
                or tpage.untrained_soldiers.count == 0:
            return pmod

        gold = tpage.gold
        if self._tsettings.match_soldiers_to_weapons:
            pmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
                self._tsettings,
                tpage, gold
            )

        gold -= pmod.cost

        if self._tsettings.soldier_dump_type != 'none':
            pmod += ROCTrainingDumpPurchaseCreator.create_purchase(
                self._tsettings,
                tpage, gold
            )
        return ROCTrainingPayloadCreator.create_training_payload(pmod)
