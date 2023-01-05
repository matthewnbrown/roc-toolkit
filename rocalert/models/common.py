import dataclasses

import rocalert.enums as rocenums


@dataclasses.dataclass
class NameIdPair:
    name: str
    id: str
    
@dataclasses.dataclass
class Army:
    soldier_count: int
    soldier_type: rocenums.RocRace


@dataclasses.dataclass
class Officer(NameIdPair):
    rank: int = -1
    alliance: NameIdPair = None
    army: Army = None
    