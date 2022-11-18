from ..roc_settings import TrainerSettings
from .models import ArmoryModel, TrainingModel, TrainingPurchaseModel
import abc


class ROCTrainingPayloadCreatorABC(abc.ABC):
    @abc.abstractmethod
    @staticmethod
    def create_training_payload(tpm: TrainingPurchaseModel):
        raise NotImplementedError


class ROCTrainingPurchaseCreatorABC(abc.ABC):
    @abc.abstractmethod
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None
            ) -> TrainingPurchaseModel:
        raise NotImplementedError


def _gen_basetrainpayload():
    soldtypes = ['attack_soldiers', 'defense_soldiers', 'spies', 'sentries']
    merctypes = ['attack_mercs', 'defense_mercs', 'untrained_mercs']

    res = {f'train[{stype}]': '' for stype in soldtypes}
    for merctype in merctypes:
        res[f'buy[{merctype}]'] = ''

    for stype in soldtypes+merctypes:
        res[f'untrain[{stype}]'] = ''


_BASE_TRAIN_PAYLOAD = _gen_basetrainpayload()


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


class ROCTrainingPurchaseCreator(ROCTrainingPurchaseCreatorABC):
    @classmethod
    def create_purchase(
            cls,
            tsettings: TrainerSettings,
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None
            ) -> TrainingPurchaseModel:

        if not tsettings.training_enabled:
            return TrainingPurchaseModel()

        purchase_counts = {
            'attack': 0,
            'defense': 0,
            'spies': 0,
            'sentries': 0
        }
        if tsettings.match_soldiers_to_weapons:
            gold = cls._soldier_match(
                purchase_counts, gold, {},
                tsettings.soldier_round_amount,
                trainmod, armmod)

        solddumptype = tsettings.soldier_dump_type

        if solddumptype != 'none':
            cls._soldier_dump(gold, purchase_counts, trainmod, solddumptype)

        return TrainingPurchaseModel(
            attack_soldiers=purchase_counts['attack'],
            defense_soldiers=purchase_counts['defense'],
            spies=purchase_counts['spies'],
            sentries=purchase_counts['sentries']
        )

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
                trainmod.attack_soldiers.cost),
            cur_purch['attack'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'defense' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_defense_weapons, roundamt,
                trainmod.defense_soldiers.count,
                trainmod.defense_soldiers.cost),
            cur_purch['defense'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'spy' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_spy_weapons, roundamt,
                trainmod.spies.count,
                trainmod.spies.cost),
            cur_purch['spies'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        if 'sentries' not in skip_match:
            amt, netcost = cls._calc_soldier_match(
                gold, armmod.total_sentry_weapons, roundamt,
                trainmod.sentries.count,
                trainmod.sentries.cost),
            cur_purch['sentries'] += amt
            trainmod.untrained_soldiers -= amt
            gold -= netcost

        return gold

    @classmethod
    def _calc_soldier_match(
            cls,
            gold: int, weapons: int, roundamt: int,
            soldiers: int, soldiercost: int
            ) -> tuple[int, int]:

        reqamt = weapons - soldiers
        if reqamt <= 0:
            return 0

        if reqamt % roundamt == 0:
            desiredamt = reqamt
        else:
            desiredamt = reqamt + roundamt - reqamt % roundamt

        purchamt = min(desiredamt, gold//soldiercost)
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

        purchamt = min(trainmod.untrained_soldiers, gold//cost)

        cur_purch[dumptype] += purchamt
        return gold
