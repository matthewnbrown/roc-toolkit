import abc

from ..roc_settings import TrainerSettings
from rocalert.models import TrainingPurchaseModel
import rocalert.models.pages as pages


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
            tpage: pages.TrainingPage,
            gold: int,
            untrained_soldiers: int,
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
            tpage: pages.TrainingPage,
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def gen_purchase_payload(
            self,
            tpage: pages.TrainingPage,
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
            tpage: pages.TrainingPage,
            gold: int,
            untrained_soldiers: int = None,
    ) -> TrainingPurchaseModel:
        if not tsettings.training_enabled or gold <= 0:
            return TrainingPurchaseModel()

        solddumptype = tsettings.soldier_dump_type

        if untrained_soldiers is not None:
            unt_soldiers = untrained_soldiers
        else:
            unt_soldiers = tpage.training.untrained_soldiers.count

        purchase_counts = {
            'attack': 0,
            'defense': 0,
            'spies': 0,
            'sentries': 0
        }
        cost = 0
        if solddumptype == 'attack':
            cost = tpage.training.attack_sold_cost
        elif solddumptype == 'defense':
            cost = tpage.training.defense_sold_cost
        elif solddumptype == 'spies':
            cost = tpage.training.spy_sold_cost
        elif solddumptype == 'sentries':
            cost = tpage.training.sentry_sold_cost

        if cost <= 0:
            return TrainingPurchaseModel()

        purchamt = min(unt_soldiers, gold//cost)

        purchase_counts[solddumptype] += purchamt

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * tpage.training.attack_sold_cost
            + tpm.defense_soldiers * tpage.training.defense_sold_cost
            + tpm.spies * tpage.training.spy_sold_cost
            + tpm.sentries * tpage.training.sentry_sold_cost
        )

        return tpm


class ROCTrainingWeaponMatchPurchaseCreator(ROCTrainingPurchaseCreatorABC):
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            tpage: pages.TrainingPage,
            gold: int,
            untrained_soldiers: int = None
    ) -> TrainingPurchaseModel:

        if not tsettings.training_enabled or gold <= 0:
            return TrainingPurchaseModel()

        skipmatch = {}

        if untrained_soldiers is not None:
            unt_soldiers = untrained_soldiers
        else:
            unt_soldiers = tpage.training.untrained_soldiers.count

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
                tpage, unt_soldiers)

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * tpage.training.attack_sold_cost
            + tpm.defense_soldiers * tpage.training.defense_sold_cost
            + tpm.spies * tpage.training.spy_sold_cost
            + tpm.sentries * tpage.training.sentry_sold_cost
        )

        return tpm

    @classmethod
    def _soldier_match(
            cls,
            cur_purch: dict[str, int],
            gold: int,
            skip_match: set[str],
            roundamt: int,
            tpage: pages.TrainingPage,
            unt_soldiers: int
    ) -> int:

        attweps = tpage.weapon_dist_table.attack_wt_dist.weapon_count
        defweps = tpage.weapon_dist_table.defense_wt_dist.weapon_count
        spyweps = tpage.weapon_dist_table.spy_wt_dist.weapon_count
        sentweps = tpage.weapon_dist_table.sentry_wt_dist.weapon_count

        if 'attack' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, attweps, roundamt,
                tpage.training.attack_soldiers.count,
                tpage.training.attack_sold_cost,
                unt_soldiers)
            cur_purch['attack'] += amt
            unt_soldiers -= amt
            gold -= netcost

        if 'defense' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, defweps, roundamt,
                tpage.training.defense_soldiers.count,
                tpage.training.defense_sold_cost,
                unt_soldiers)
            cur_purch['defense'] += amt
            unt_soldiers -= amt
            gold -= netcost

        if 'spy' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, spyweps, roundamt,
                tpage.training.spies.count,
                tpage.training.spy_sold_cost,
                unt_soldiers)
            cur_purch['spies'] += amt
            unt_soldiers -= amt
            gold -= netcost

        if 'sentries' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, sentweps, roundamt,
                tpage.training.sentries.count,
                tpage.training.sentry_sold_cost,
                unt_soldiers)
            cur_purch['sentries'] += amt
            unt_soldiers -= amt
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
            tpage: pages.TrainingPage
    ) -> bool:

        if tpage is None or not self._tsettings.training_enabled:
            return False

        if tpage.clock_bar.gold <= 0 or tpage.training.untrained_soldiers.count == 0:
            return False

        if self._tsettings.min_training_size > tpage.training.untrained_soldiers.count:
            return False

        purchase = self._calculate_purchase(tpage)
        size = purchase.total_mercs + purchase.total_soldiers

        return size > self._tsettings.min_training_size

    def _calculate_purchase(
            self,
            tpage: pages.TrainingPage
    ) -> TrainingPurchaseModel:
        pmod = TrainingPurchaseModel()

        if tpage is None or tpage.clock_bar.gold == 0 \
                or tpage.training.untrained_soldiers.count == 0:
            return pmod

        gold = tpage.clock_bar.gold
        if self._tsettings.match_soldiers_to_weapons:
            pmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
                self._tsettings,
                tpage, gold
            )

        gold -= pmod.cost
        untrained = tpage.training.untrained_soldiers.count - pmod.total_soldiers
        if self._tsettings.soldier_dump_type != 'none':
            pmod += ROCTrainingDumpPurchaseCreator.create_purchase(
                self._tsettings,
                tpage, gold, untrained
            )

        return pmod

    def gen_purchase_payload(
            self,
            tpage: pages.TrainingPage
    ) -> dict[str, str]:

        pmod = self._calculate_purchase(tpage=tpage)
        return ROCTrainingPayloadCreator.create_training_payload(pmod)
