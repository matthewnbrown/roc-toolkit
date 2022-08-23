class ROCStats:
    STAT_IDS = {'keyfound', 'lastactive', 'rank', 'highestrank',
                'armysize', 'tbg', 'sa', 'da', 'spy', 'sentry'}

    def __init__(self, stats) -> None:
        self._stats = {id: None for id in ROCStats.STAT_IDS}
        if stats is not None:
            for id in ROCStats.STAT_IDS:
                if id in stats:
                    self._stats[id] = stats[id]

    @property
    def armysize(self) -> int:
        return self._stats['armysize']

    @armysize.setter
    def armysize(self, newarmysize: int) -> None:
        if newarmysize < 0:
            raise Exception('Invalid army size')

        self._stats['armysize'] = newarmysize


class ROCTraining:
    def __init__(self) -> None:
        pass


class ROCArmory:
    def __init__(self) -> None:
        pass


class ROCAccount:
    def __init__(self,
                 gold: int,
                 roctrain: ROCTraining,
                 rocarm: ROCArmory
                 ) -> None:
        self._gold = gold
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
