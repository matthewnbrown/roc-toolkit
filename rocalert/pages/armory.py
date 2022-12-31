import rocalert.pages.genericpages as gp
import rocalert.models as models


class ArmoryPage(gp.RocPage, gp.TurnBoxPage, gp.CaptchaPage):
    armory:  models.ArmoryModel
    stats: gp.StatTable
    weapon_distribution: gp.WeaponTroopDistTable


'''
@dataclasses.dataclass
class ArmoryDetails:
    weapons: dict[str, models.ItemCostPair]

    @property
    def dagger(self) -> models.ItemCostPair:
        return self.weapons['dagger']

    @property
    def maul(self) -> models.ItemCostPair:
        return self.weapons['maul']

    @property
    def blade(self) -> models.ItemCostPair:
        return self.weapons['blade']

    @property
    def excalibur(self) -> models.ItemCostPair:
        return self.weapons['excalibur']

    @property
    def sai(self) -> models.ItemCostPair:
        return self.weapons['sai']

    @property
    def shield(self) -> models.ItemCostPair:
        return self.weapons['shield']

    @property
    def mithril(self) -> models.ItemCostPair:
        return self.weapons['mithril']

    @property
    def dragonskin(self) -> models.ItemCostPair:
        return self.weapons['dragonskin']

    @property
    def horn(self) -> models.ItemCostPair:
        return self.weapons['horn']

    @property
    def guard_dog(self) -> models.ItemCostPair:
        return self.weapons['guard_dog']

    @property
    def torch(self) -> models.ItemCostPair:
        return self.weapons['torch']

    @property
    def cloak(self) -> models.ItemCostPair:
        return self.weapons['cloak']

    @property
    def hook(self) -> models.ItemCostPair:
        return self.weapons['hook']

    @property
    def pickaxe(self) -> models.ItemCostPair:
        return self.weapons['pickaxe']


class ArmoryPage(gp.RocPage, gp.TurnBox, gp.CaptchaStatus):
    armory: ArmoryDetails
    stats: gp.StatTable
    weapon_distribution: gp.WeaponTroopDistTable
'''
