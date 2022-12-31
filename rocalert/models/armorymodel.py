import dataclasses

from rocalert.models import ItemCostPair
from rocalert.enums import Weapon


@dataclasses.dataclass
class ArmoryModel:
    dagger: ItemCostPair = None
    maul: ItemCostPair = None
    blade: ItemCostPair = None
    excalibur: ItemCostPair = None
    sai: ItemCostPair = None
    shield: ItemCostPair = None
    mithril: ItemCostPair = None
    dragonskin: ItemCostPair = None
    cloak: ItemCostPair = None
    hook: ItemCostPair = None
    pickaxe: ItemCostPair = None
    horn: ItemCostPair = None
    guard_dog: ItemCostPair = None
    torch: ItemCostPair = None

    @property
    def total_attack_weapons(self) -> int:
        total = self.dagger + self.maul + self.blade + self.excalibur
        return total.count

    @property
    def total_defense_weapons(self) -> int:
        total = self.sai + self.shield + self.mithril + self.dragonskin
        return total.count

    @property
    def total_spy_weapons(self) -> int:
        total = self.cloak + self.hook + self.pickaxe
        return total.count

    @property
    def total_sentry_weapons(self) -> int:
        total = self.horn + self.guard_dog + self.torch
        return total.count

    def get_weapon(self, rocweapon: Weapon) -> ItemCostPair:
        match rocweapon:
            case Weapon.DAGGER:
                return self.dagger
            case Weapon.MAUL:
                return self.maul
            case Weapon.BLADE:
                return self.blade
            case Weapon.EXCALIBUR:
                return self.excalibur
            case Weapon.SAI:
                return self.sai
            case Weapon.SHIELD:
                return self.shield
            case Weapon.MITHRIL:
                return self.mithril
            case Weapon.DRAGONSKIN:
                return self.dragonskin
            case Weapon.CLOAK:
                return self.cloak
            case Weapon.HOOK:
                return self.hook
            case Weapon.PICKAXE:
                return self.pickaxe
            case Weapon.HORN:
                return self.horn
            case Weapon.GUARD_DOG:
                return self.guard_dog
            case Weapon.TORCH:
                return self.torch
