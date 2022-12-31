import typing
import datetime as dt
import dataclasses

from rocalert.models.pages.training import RocTrainingTableEntry
from rocalert.models.pages.genericpages import WeaponDistTableEntry


@dataclasses.dataclass
class WeaponTroopDistTable:
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
class TrainingPage:
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
        self._weapondisttable = WeaponTroopDistTable(
            att_dist=WeaponDistTableEntry(self.attacksoldiers,
                                          self.attweps),
            def_dist=WeaponDistTableEntry(self.defensesoldiers, self.defweps),
            spy_dist=WeaponDistTableEntry(self.spyweps, self.spyweps),
            sent_dist=WeaponDistTableEntry(self.sentriesamt, self.sentrycost)
        )

    @property
    def weapon_distribution_table(self) -> WeaponTroopDistTable:
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


class TrainingSettings():
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


class UserSettings:
    def __init__(
            self,
            usenightmode: bool = False,
            regular_waitrange: typing.Tuple[int, int] = None,
            nightmode_activerange: typing.Tuple[dt.time, dt.time] = None,
            nightmode_waitrange: typing.Tuple[float, float] = None
            ) -> None:
        self.use_nightmode = usenightmode
        self.nightmode_activetime_range = nightmode_activerange
        self.nightmode_waittime_range = nightmode_waitrange
        self.regular_waittimes_seconds = regular_waitrange


class RocWebHandler:
    def __init__(self, current_gold=None,) -> None:
        self._currentgold = current_gold

    def current_gold(self) -> int:
        if self._currentgold is None:
            raise ValueError('Gold value was not set')

        return self._currentgold


class BuyerSettings:
    def __init__(
            self,
            min_gold_to_buy=None,
            buying_enabled=True,
            dagger=0, maul=0, blade=0, excalibur=0,
            cloak=0, hook=0, pickaxe=0, sai=0,
            shield=0, mithril=0, dragonskin=0,
            horn=0, guard_dog=0, torch=0
            ) -> None:
        self._minbuygold = min_gold_to_buy
        self._buyingenabled = buying_enabled
        self._weaponbuydict = {
            'dagger': dagger, "maul": maul,
            "blade": blade, "excalibur": excalibur,
            "cloak": cloak, "hook": hook, "pickaxe": pickaxe,
            "sai": sai, "shield": shield, "mithril": mithril,
            "dragonskin": dragonskin, "horn": horn, "guard_dog": guard_dog,
            "torch": torch
        }

    def min_gold_to_buy(self) -> int:
        if self._minbuygold is None:
            raise ValueError("Min gold not set")
        return self._minbuygold

    def get_weapons_to_buy(self) -> dict[str, int]:
        d = {}
        for settingid, setting in self._weaponbuydict.items():
            if settingid != 'buy_weapons' and settingid != 'min_gold' \
                    and setting > 0:
                d[settingid] = setting
        return d

    def buying_enabled(self) -> bool:
        return self._buyingenabled