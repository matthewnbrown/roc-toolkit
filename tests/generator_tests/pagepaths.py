
class Armory:
    _base = '/testpages/armory/'
    BASIC = _base + 'armorybasic.html'


class Base:
    _base = '/testpages/base/'
    DUB_TRUB = _base + 'dubtrub.html'
    STOLE_TURN = _base + 'stoleturn.html'
    BASE_WITH_OFFICERS = _base + 'basewithofficers.html'
    FOUND_BROKE_KEY = _base + 'basefoundbrokenkey.html'
    NO_ACTIVE_EVENTS = _base + 'base_noactive_events.html'


class BattlefieldActions:
    pass


class CustomPages:
    pass


class SimplePages:
    _base = '/testpages/simplepages/'
    LOGGED_IN_PAGE = 'loginstatus/true.html'
    NOT_LOGGED_IN = 'loginstatus/false.html'


class Keep:
    _base = '/testpages/keep/'
    SIXKEYSNOBROKEN_REPAIRING = _base + '6k0brep.html'


class Recruit:
    _base = '/testpages/recruit/'
    NOCAPTCHA = _base + 'recruit_no_captcha.html'
    HAS_CAPTCHA = _base + 'recruit_captcha.html'


class Components:
    class StatTable:
        _base = '/testpages/simplepages/statstable/'
        NOBONUS = _base + 'statstable_nobonus.html'
        BONUS = _base + 'statstable_allbonus.html'


class Training:
    _base = '/testpages/training/'
    ALL_MERCS = _base + 'trainingallmercs.html'
    NO_ATTACK_MERCS = _base + 'training0am.html'
    NO_AVAILABLE_MERCS = _base + 'training_none_avail.html'
