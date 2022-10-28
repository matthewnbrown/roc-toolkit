from ._settings import Setting, Settings, SettingsValidator


class TrainerSettings(Settings):
    VALID_SOLDIER_TYPES = ['attack', 'defense', 'spy', 'sentry', 'none']
    DEFAULT_SETTINGS = {
        'train_soldiers': Setting(
            'Train Soldiers',
            'train_soldiers',
            False, bool,
            'Enable or disable all soldier training/buying'),
        'soldier_weapon_match': Setting(
            'Match weapons to soldiers',
            'soldier_weapon_match',
            False, bool,
            'Match amount of soldiers to amount of weapons '
            + 'in each weapons program'),
        'soldier_dump_type': Setting(
            'Soldier dump type',
            'soldier_dump_type',
            'none', str,
            'Dump all excess soldiers into this program.',
            None,
            lambda x: x in TrainerSettings.VALID_SOLDIER_TYPES
        )
    }

    class SoldierTypes:
        ATTACK = 'attack'
        DEFENSE = 'defense'
        SPY = 'spy'
        SENTRY = 'sentry'
        NONE = 'none'

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = "Trainer Settings"
        super().__init__(name, filepath)

        self.mandatory = {'train_soldiers'}

        if(filepath is not None):
            self.__check_valid_settings()

    def __check_valid_settings(self):
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        inrange = SettingsValidator.check_settings_in_range(
            self.settings, warnings=True)

        if not inrange:
            print("ERROR: Trainer settings are invalid!")
            quit()

    @property
    def training_enabled(self):
        return self.get_setting['train_soldiers'].value

    def match_soldiers_to_weapons(self):
        return self.get_setting['soldier_weapon_match'].value

    def soldier_dump_type(self):
        return self.get_setting['soldier_dump_type'].value