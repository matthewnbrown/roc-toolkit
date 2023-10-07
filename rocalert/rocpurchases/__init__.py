from .roc_buyer import ROCBuyer
from .rocpurchtools import RocItem, RocItemGroup, ALL_ITEM_DETAILS
from .roc_trainer import (
    ROCTrainingPurchaseCreatorABC,
    ROCTrainingPayloadCreatorABC,
    ROCTrainingPayloadCreator,
    ROCTrainingDumpPurchaseCreator,
    ROCTrainingWeaponMatchPurchaseCreator,
    ROCTrainerABC,
    SimpleRocTrainer,
)

if __name__ == "__main__":
    print("don't run this file")
    ROCBuyer()
    RocItem()
    ROCTrainingPurchaseCreatorABC()
    ROCTrainingPayloadCreatorABC()
    ROCTrainingPayloadCreator()
    ROCTrainingDumpPurchaseCreator()
    ROCTrainingWeaponMatchPurchaseCreator()
    RocItemGroup()
    ROCTrainerABC()
    SimpleRocTrainer()
    ALL_ITEM_DETAILS
