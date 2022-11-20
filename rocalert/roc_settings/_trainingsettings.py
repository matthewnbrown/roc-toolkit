from ._settings import Setting, Settings, SettingsValidator


class TrainerSettings(Settings):
    VALID_SOLDIER_TYPES = {'attack', 'defense', 'spies', 'sentries', 'none'}
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
            'none',
            lambda x: x in TrainerSettings.VALID_SOLDIER_TYPES
        ),
        'soldier_round_amount': Setting(
            'Soldier round amount', 'soldier_round_amount',
            1000, int, 'Round matching purchase to this amount',
            1000, lambda x: x >= 0
        ),
        'min_train_purchase_size': Setting(
            'Minimum amount of untrained soldiers to train.',
            'min_train_purchase_size',
            1200, int, 'Round matching purchase to this amount',
            1200, lambda x: x >= 0
        ),
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

        if filepath is not None:
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
    def training_enabled(self) -> bool:
        return self.get_setting('train_soldiers').value

    @property
    def match_soldiers_to_weapons(self) -> bool:
        return self.get_setting('soldier_weapon_match').value

    @property
    def soldier_dump_type(self) -> str:
        return self.get_setting('soldier_dump_type').value

    @property
    def soldier_round_amount(self) -> int:
        return self.get_setting('soldier_round_amount').value

    @property
    def min_training_size(self):
        return self.get_setting('min_train_purchase_size').value
