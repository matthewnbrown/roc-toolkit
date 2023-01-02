import typing
import datetime as dt
import dataclasses

from rocalert.models.pages.training import RocTrainingTableEntry as RTTE
from rocalert.models.pages.genericpages import WeaponDistTableEntry
import rocalert.models.pages as rocpages

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


class TrainingPageCreator:
    @staticmethod
    def create(
            gold: int = 0,
            attacksoldiers: int = 0,
            defensesoldiers: int = 0,
            spiesamt: int = 0,
            sentriesamt: int = 0,
            untrained: int = 0,
            attacksoldcost: int = 0,
            defensesoldcost: int = 0,
            spycost: int = 0,
            sentrycost: int = 0,
            attweps: int = 0,
            defweps: int = 0,
            spyweps: int = 0,
            sentryweps: int = 0,
            attmercs: int = 0,
            defmercs: int = 0,
            untrainedmercs: int = 0
            ) -> rocpages.TrainingPage:
        
        details = rocpages.TrainingDetails(
            attack_soldiers=RTTE(attacksoldiers, attacksoldiers*20),
            defense_soldiers=RTTE(defensesoldiers, defensesoldiers*25),
            spies=RTTE(spiesamt, spiesamt*10),
            sentries=RTTE(sentriesamt, sentriesamt*10),
            untrained_soldiers=RTTE(untrained, untrained*20),
            attack_sold_cost=attacksoldcost,
            defense_sold_cost=defensesoldcost,
            spy_sold_cost=spycost,
            sentry_sold_cost=sentrycost,
            total_soldiers=RTTE(attacksoldiers+defensesoldiers+untrained,
                                attacksoldiers*20+defensesoldiers*25+untrained*20),
            total_mercenaries=RTTE(attmercs+defmercs+untrainedmercs,
                                   (attacksoldiers+defensesoldiers+untrained)*-5),
            total_covert_force=RTTE(spiesamt+sentriesamt,(spiesamt+sentriesamt)*10),
            )
        clockbar = rocpages.ClockBar(name='username', rank=-1,gold=gold,turns=-1,
                                     next_turn=None)
        wt_table = WeaponTroopDistTable(
            att_dist=WeaponDistTableEntry(attacksoldiers,
                                          attweps),
            def_dist=WeaponDistTableEntry(defensesoldiers, defweps),
            spy_dist=WeaponDistTableEntry(spyweps, spyweps),
            sent_dist=WeaponDistTableEntry(sentriesamt, sentryweps)
        )
        
        return rocpages.TrainingPage(
            training=details,
            clock_bar=clockbar,
            weapon_dist_table=wt_table)


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
