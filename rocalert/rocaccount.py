from rocalert.rocpurchases.rocpurchtools \
    import AttackSoldier, DefenseSoldier, RocItem, Spy, \
    Sentry, AttackMerc, DefenseMerc, UntrainedMerc, \
    ALL_ITEM_DETAILS


class ROCStats:
    STAT_IDS = {'keyfound', 'lastactive', 'rank', 'highestrank',
                'armysize', 'tbg', 'sa', 'da', 'spy', 'sentry'}

    def __init__(self, stats) -> None:
        self._stats = {id: None for id in ROCStats.STAT_IDS}
        if stats is not None:
            for id in ROCStats.STAT_IDS:
                if id in stats:
                    self._stats[id] = stats[id]

    def __nonnegative(num, name):
        if num < 0:
            raise Exception(f'Invalid {name}')

    @property
    def armysize(self) -> int:
        return self._stats['armysize']

    @armysize.setter
    def armysize(self, newarmysize: int) -> None:
        ROCStats.__nonnegative(newarmysize, 'army size')
        self._stats['armysize'] = newarmysize

    @property
    def turnbasedgold(self) -> int:
        return self._stats['tbg']

    @turnbasedgold.setter
    def turnbasedgold(self, newtbg: int) -> None:
        ROCStats.__nonnegative(newtbg, 'tbg')
        self._stats['tbg'] = newtbg

    @property
    def strike(self) -> int:
        return self._stats['sa']

    @strike.setter
    def strike(self, newsa: int) -> None:
        ROCStats.__nonnegative(newsa, 'strike action')
        self._stats['sa'] = newsa

    @property
    def defense(self) -> int:
        return self._stats['da']

    @defense.setter
    def defense(self, newda: int) -> None:
        ROCStats.__nonnegative(newda, 'defense action')
        self._stats['da'] = newda

    @property
    def spy(self) -> int:
        return self._stats['spy']

    @spy.setter
    def spy(self, newspy: int) -> None:
        ROCStats.__nonnegative(newspy, 'spy')
        self._stats['spy'] = newspy

    @property
    def sentry(self) -> int:
        return self._stats['sentry']

    @sentry.setter
    def sentry(self, newsentry: int) -> None:
        ROCStats.__nonnegative(newsentry, 'sentry')
        self._stats['sentry'] = newsentry


class ROCTraining:
    def __init__(self,
                 att: AttackSoldier = None,
                 ds: DefenseSoldier = None,
                 spy: Spy = None,
                 sent: Sentry = None,
                 am: AttackMerc = None,
                 dm: DefenseMerc = None,
                 um: UntrainedMerc = None) -> None:

        self._att = att
        self._def = ds
        self._spy = spy
        self._sentry = sent
        self._attmerc = am
        self._defmerc = dm
        self._untmerc = um


ITEM_BY_CODE = {item.code: item for _, item in ALL_ITEM_DETAILS}


class ROCArmory:
    def __init__(self, itemcount: dict[str, int] = None) -> None:
        self._counts = {name: 0 for name in ALL_ITEM_DETAILS}
        if itemcount:
            for name, count in itemcount.items():
                if name in ALL_ITEM_DETAILS:
                    self._counts[name] = count

    def _get_all_itemtype(self, itemtype: RocItem.ItemType) -> dict[str, int]:
        res = {}
        for name, item in ALL_ITEM_DETAILS.items():
            if item.stat_type == itemtype:
                res[name] = self._counts[name]
        return res

    def get_attack_items(self) -> dict[str, int]:
        return self._get_all_itemtype(RocItem.ItemType.ATTACK)

    def get_defense_items(self) -> dict[str, int]:
        return self._get_all_itemtype(RocItem.ItemType.DEFENSE)

    def get_spy_items(self) -> dict[str, int]:
        return self._get_all_itemtype(RocItem.ItemType.SPY)

    def get_sentry_items(self) -> dict[str, int]:
        return self._get_all_itemtype(RocItem.ItemType.SENTRY)


class ROCAccount:
    def __init__(self,
                 gold: int,
                 rocstats: ROCStats,
                 roctrain: ROCTraining,
                 rocarm: ROCArmory
                 ) -> None:
        self._gold = gold
        self._stats = rocstats
        self._roctrain = roctrain
        self._rocarm = rocarm

    @property
    def gold(self) -> int:
        return self._gold

    @gold.setter
    def gold(self, newgold: int) -> None:
        if type(newgold) != int or newgold < 0:
            raise Exception(f'Error: Invalid gold value: {newgold}')
        self._gold = newgold

    @property
    def stats(self) -> ROCStats:
        return self._stats

    @stats.setter
    def stats(self, newstats: ROCStats) -> None:
        if newstats is None:
            raise Exception('Invalid ROCStats value')

        self._stats = newstats

    @property
    def armory(self) -> ROCArmory:
        return self._rocarm

    @armory.setter
    def armory(self, newarmory: ROCArmory) -> None:
        if newarmory is None:
            raise Exception('Error: Invalid ROCArmory')

    @property
    def training(self) -> ROCTraining:
        return self._roctrain

    @training.setter
    def training(self, newtraining: ROCTraining) -> None:
        if newtraining is None:
            raise Exception('Error Invalid ROCTraining')
