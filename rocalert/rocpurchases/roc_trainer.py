from ..roc_settings import TrainerSettings
from rocalert.rocpurchases.models import ArmoryModel,\
    TrainingModel, TrainingPurchaseModel
import abc


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
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None
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
            gold: int = 0,
            tmod: TrainingModel = None,
            amod: ArmoryModel = None
            ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def gen_purchase_payload(
            self,
            gold: int = 0,
            tmod: TrainingModel = None,
            amod: ArmoryModel = None
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
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None,
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

        if solddumptype == 'attack':
            cost = trainmod.attack_soldiers.cost
        elif solddumptype == 'defense':
            cost = trainmod.defense_soldiers.cost
        elif solddumptype == 'spies':
            cost = trainmod.spies.cost
        elif solddumptype == 'sentries':
            cost = trainmod.sentries.cost

        if cost <= 0:
            return gold

        purchamt = min(trainmod.untrained_soldiers.count, gold//cost)

        purchase_counts[solddumptype] += purchamt

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * trainmod.attack_soldiers.cost
            + tpm.defense_soldiers * trainmod.defense_soldiers.cost
            + tpm.spies * trainmod.spies.cost
            + tpm.sentries * trainmod.sentries.cost
        )

        return tpm


class ROCTrainingWeaponMatchPurchaseCreator(ROCTrainingPurchaseCreatorABC):
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None,
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
                trainmod, armmod)

        tpm = TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

        tpm.cost = (
            tpm.attack_soldiers * trainmod.attack_soldiers.cost
            + tpm.defense_soldiers * trainmod.defense_soldiers.cost
            + tpm.spies * trainmod.spies.cost
            + tpm.sentries * trainmod.sentries.cost
        )

        return tpm

    @classmethod
    def _soldier_match(
            cls,
            cur_purch: dict[str, int],
            gold: int,
            skip_match: set[str],
            roundamt: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel
            ) -> int:
        if 'attack' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_attack_weapons, roundamt,
                trainmod.attack_soldiers.count,
                trainmod.attack_soldiers.cost,
                trainmod.untrained_soldiers.count)
            cur_purch['attack'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'defense' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_defense_weapons, roundamt,
                trainmod.defense_soldiers.count,
                trainmod.defense_soldiers.cost,
                trainmod.untrained_soldiers.count)
            cur_purch['defense'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'spy' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_spy_weapons, roundamt,
                trainmod.spies.count,
                trainmod.spies.cost,
                trainmod.untrained_soldiers.count)
            cur_purch['spies'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'sentries' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_sentry_weapons, roundamt,
                trainmod.sentries.count,
                trainmod.sentries.cost,
                trainmod.untrained_soldiers.count)
            cur_purch['sentries'] += amt
            trainmod.untrained_soldiers -= amt
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

    @classmethod
    def _soldier_dump(
            cls,
            gold: int,
            cur_purch: dict[str, int],
            trainmod: TrainingModel,
            dumptype: str
            ) -> int:

        if dumptype == 'attack':
            cost = trainmod.attack_soldiers.cost
        elif dumptype == 'defense':
            cost = trainmod.defense_soldiers.cost
        elif dumptype == 'spies':
            cost = trainmod.spies.cost
        elif dumptype == 'sentries':
            cost = trainmod.sentries.cost

        if cost <= 0:
            return gold

        purchamt = min(trainmod.untrained_soldiers.count, gold//cost)

        cur_purch[dumptype] += purchamt
        return gold


class SimpleRocTrainer(ROCTrainerABC):
    def __init__(self, tsettings: TrainerSettings) -> None:
        self._tsettings = tsettings

    def is_training_required(
            self,
            gold: int = 0,
            tmod: TrainingModel = None,
            amod: ArmoryModel = None
            ) -> bool:

        if gold <= 0 or tmod is None or tmod.untrained_soldiers.count == 0\
                or not self._tsettings.training_enabled:
            return False

        return True

    def gen_purchase_payload(
            self,
            gold: int = 0,
            tmod: TrainingModel = None,
            amod: ArmoryModel = None
            ) -> dict[str, str]:

        pmod = TrainingPurchaseModel()

        if gold <= 0 or tmod is None or tmod.untrained_soldiers.count == 0:
            return pmod

        if self._tsettings.match_soldiers_to_weapons and amod is not None:
            pmod = ROCTrainingWeaponMatchPurchaseCreator.create_purchase(
                self._tsettings,
                gold, tmod, amod
            )
        # TODO: Get cost of previous pmod and remove the correct amount of gold from gold
        if self._tsettings.soldier_dump_type != 'none':
            pmod += ROCTrainingDumpPurchaseCreator.create_purchase(
                self._tsettings,
                gold, tmod, amod
            )
        return pmod
