import enum


class RocPageType(enum.Enum):
    UNKNOWN = 1
    HOME = 2  # Not implemented
    BASE = 3
    TRAINING = 4
    ARMORY = 5
    RECRUIT = 6
    KEEP = 7
    BATTLEFIELD = 8  # Not Implemented
    BUILDINGS_AND_SKILLS = 9  # Not Implemented
    MAIL = 10  # Not Implemented
    BATTLE_LOG = 11  # Not Implemented
    ACTIVITY_LOG = 12  # Not Implemented
    TARGET_STATS = 13  # Not Implemented
    TARGET_ATTACK = 14  # Not Implemented
    TARGET_PROBE = 15  # Not Implemented
    TARGET_SPY = 16  # Not Implemented
    TARGET_SENTRY = 17  # Not Implemented
    TARGET_SPITE = 18  # Not Implemented
    INTEL_FILE = 19  # Overall recent intel  # Not Implemented
    INTEL_DETAIL = 20  # Specific spy report  # Not Implemented
    ALL_SAB_LOG = 21  # Not Implemented
    ERROR = 22
    ATTACK_LOG = 23  # Not Implemented
    ATTACK_DETAIL = 24  # Not Implemented
    ALLIANCE = 25  # Not Implemented
    SEND_CREDITS = 26  # Not Implemented
    SEND_MESSAGE = 27  # Not Implemented
    SEND_DOGE = 28  # Not Implemented
