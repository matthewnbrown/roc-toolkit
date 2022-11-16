from ..roc_settings import TrainerSettings
from models import ArmoryModel, TrainingModel, TrainingPurchaseModel
import abc


class ROCTrainingPayloadCreatorABC(abc.ABC):
    @abc.abstractmethod
    @staticmethod
    def create_training_payload(tpm: TrainingPurchaseModel):
        raise NotImplementedError


class ROCTrainingPurchaseCreatorABC(abc.ABC):
    @abc.abstractmethod
    @staticmethod
    def create_purchase(
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
    @staticmethod
    def create_purchase(
            tsettings: TrainerSettings,
            gold: int,
            trainmod: TrainingModel,
            armmod: ArmoryModel = None
            ) -> TrainingPurchaseModel:
        raise NotImplementedError
