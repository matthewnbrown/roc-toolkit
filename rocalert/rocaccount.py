class RocAccount:
    def __init__(self) -> None:
        pass


class RocSoldiers:
    def __init__(self) -> None:
        pass


class RocArmoury:
    def __init__(self) -> None:
        pass


class BattlefieldTarget:
    def __init__(self, id: str, rank: int, name: str, alliance: str,
                 tff: int, tfftype: str, gold: int) -> None:
        self.id = id
        self.rank = rank
        self.name = name
        self.alliance = alliance
        self.tff = tff
        self.tfftype = tfftype
        self.gold = gold
