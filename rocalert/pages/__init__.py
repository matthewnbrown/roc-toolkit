from .armory import ArmoryPage
from .base import BasePage
from .keep import KeepPage
from .recruit import RecruitPage
from .training import TrainingPage
import rocalert.pages.generators as generators


if __name__ == '__main__':
    print('dont run this')
    ArmoryPage()
    BasePage()
    KeepPage()
    RecruitPage()
    TrainingPage()
    generators.RocPageGenerator()
