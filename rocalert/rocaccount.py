
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
