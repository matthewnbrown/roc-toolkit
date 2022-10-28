from ._settings import Settings, Setting, SettingsValidator


class BuyerSettings(Settings):
    def __positive__(x): return x >= 0

    DEFAULT_SETTINGS = {
        'buy_weapons': Setting('Toggle Buying', 'buy_weapons', False, bool,
                               'Enable weapon buying'),
        'min_gold': Setting('Minimum Gold', 'min_gold', 500000000, int,
                            'Minimum gold to purchase with',
                            None, __positive__),
        'dagger': Setting('Dagger', 'dagger', 0, int,
                          'Amount of daggers to buy',
                          None, __positive__),
        'maul': Setting('Maul', 'maul', 0, int, 'Amount of Mauls to buy',
                        None, __positive__),
        'blade': Setting('Blade', 'blade', 0, int, 'Amount of blades to buy',
                         None, __positive__),
        'excalibur': Setting('Excalibur', 'excalibur', 0, int,
                             'Amount of excalibur to buy',
                             None, __positive__),
        'cloak': Setting('Cloak', 'cloak', 0, int, 'Amount of cloaks to buy',
                         None, __positive__),
        'hook': Setting('Hook', 'hook', 0, int, 'Amount of hooks to buy',
                        None, __positive__),
        'pickaxe': Setting('Pickaxe', 'pickaxe', 0, int,
                           'Amount of pickaxes to buy',
                           None, __positive__),
        'sai': Setting('Sai', 'sai', 0, int, 'Amount of sai to buy',
                       None, __positive__),
        'shield': Setting('Shield', 'shield', 0, int,
                          'Amount of shields to buy',
                          None, __positive__),
        'mithril': Setting('Mithril', 'mithril', 0, int,
                           'Amount of mithril to buy',
                           None, __positive__),
        'dragonskin': Setting('Dragonskin', 'dragonskin', 0, int,
                              'Amount of dragonskins to buy',
                              None, __positive__),
        'horn': Setting('Horn', 'horn', 0, int, 'Amount of horns to buy',
                        None, __positive__),
        'guard_dog': Setting('Guard Dog', 'guard_dog', 0, int,
                             'Amount of guard dogs to buy',
                             None, __positive__),
        'torch': Setting('Torch', 'torch', 0, int, 'Amount of torches to buy',
                         None, __positive__)
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = "Buyer Settings"

        super().__init__(name, filepath)

        self.mandatory = {'buy_weapons'}

        if(filepath is not None):
            self.__check_valid_settings()

    def load_settings_from_path(self, filepath) -> None:
        super().load_settings_from_path(filepath)
        self.__check_valid_settings()

    def buying_enabled(self) -> bool:
        return self.settings is not None and self.settings['buy_weapons'].value

    def min_gold_to_buy(self) -> int:
        return self.settings['min_gold'].value

    def get_weapons_to_buy(self) -> dict:
        d = {}
        for settingid, setting in self.settings.items():
            if settingid != 'buy_weapons' and settingid != 'min_gold' \
                    and setting.value > 0:
                d[settingid] = setting.value
        return d

    def __check_valid_settings(self):
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        SettingsValidator.check_settings_in_range(self.settings, True)
