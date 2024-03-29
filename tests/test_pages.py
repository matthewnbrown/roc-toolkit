import os
import unittest

from bs4 import BeautifulSoup

import rocalert.pages as pages
import rocalert.pages.genericpages as gp


def _get_dir():
    lastslash = max(__file__.rfind("\\"), __file__.rfind("/"))
    return __file__[: lastslash + 1]


def _check_tfile_exists(path):
    if not os.path.exists(path):
        raise Exception(f"File does not exist at {path}")


def _getsoup(path):
    filepath = _get_dir() + path
    _check_tfile_exists(filepath)

    with open(filepath) as f:
        text = f.read()
        soup = BeautifulSoup(text, "lxml")
    return soup


class PageLoggedInTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_logged_in(self):
        path = "testpages/simplepages/loginstatus/true.html"
        soup = _getsoup(path)

        page = gp.RocPage(soup)
        self.assertTrue(page.logged_in, "Page is not logged in.")

    def test_notlogged_in(self):
        path = "testpages/simplepages/loginstatus/false.html"
        soup = _getsoup(path)

        page = gp.RocPage(soup)
        self.assertFalse(page.logged_in, "Page is logged in.")


class StatsTableTest(unittest.TestCase):
    # TODO Add seperate tests for bonus tables
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _getnobonustable(self) -> gp.StatTable:
        filepath = "testpages/simplepages/statstable/statstable_nobonus.html"
        soup = _getsoup(filepath)
        return gp.StatTable(soup)

    def _getbonustable(self) -> gp.StatTable:
        filepath = "testpages/simplepages/statstable/statstable_allbonus.html"
        soup = _getsoup(filepath)
        return gp.StatTable(soup)

    def test_simple_table_strike_val(self):
        table = self._getnobonustable()
        entry = table.strike
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 10000000, 109),
            "Invalid strike tuple",
        )

    def test_simple_table_defense(self):
        table = self._getnobonustable()
        entry = table.defense
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 420690, 1),
            "Invalid defense tuple",
        )

    def test_simple_table_spy(self):
        table = self._getnobonustable()
        entry = table.spy
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 100001, 63),
            "Invalid strike tuple",
        )

    def test_simple_table_sentry(self):
        table = self._getnobonustable()
        entry = table.sentry
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 24232122, 11),
            "Invalid sentry tuple",
        )

    def test_simple_table_kills(self):
        table = self._getnobonustable()
        self.assertEqual(table.kills, 322432, "Invalid kill count")

    def test_simple_table_killratio(self):
        table = self._getnobonustable()
        self.assertEqual(table.kill_ratio, 1.23, "Invalid kill ratio")

    def test_bonus_strike(self):
        table = self._getbonustable()
        entry = table.strike
        self.assertEqual(entry.bonus, 3.0, "Invalid strike bonus")

    def test_bonus_defense(self):
        table = self._getbonustable()
        entry = table.defense
        self.assertEqual(entry.bonus, 55.5, "Invalid defense bonus")

    def test_bonus_spy(self):
        table = self._getbonustable()
        entry = table.spy
        self.assertEqual(entry.bonus, 17.0, "Invalid spy bonus")

    def test_bonus_sentry(self):
        table = self._getbonustable()
        entry = table.sentry
        self.assertEqual(entry.bonus, 1.0, "Invalid sentry bonus")


class WeaponTroopDistTableTest(unittest.TestCase):
    # TODO Add seperate tests for with untrained table
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_page_path(self):
        return "/testpages/simplepages/weapontrooptable/"

    def _get_untrained_table(self) -> gp.WeaponTroopDistTable:
        path = self._get_page_path() + "weapontrooptable_hasuntrained.html"
        soup = _getsoup(path)
        return gp.WeaponTroopDistTable(soup)

    def _get_no_untrained_table(self) -> gp.WeaponTroopDistTable:
        path = (
            "/testpages/simplepages/weapontrooptable/"
            + "weapontrooptable_nountrained.html"
        )
        soup = _getsoup(path)
        return gp.WeaponTroopDistTable(soup)

    def _get_training_unt_table(self) -> gp.WeaponTroopDistTable:
        path = self._get_page_path() + "weapontrooptable_training_unt.html"
        soup = _getsoup(path)
        return gp.WeaponTroopDistTable(soup)

    def test_load_training_table(self):
        self._get_training_unt_table()

    def test_nountrained_attack(self):
        table = self._get_no_untrained_table()
        entry = table.attack_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (2322121, 1234),
            "Invalid attack weapon troop distribution",
        )

    def test_nountrained_defense(self):
        table = self._get_no_untrained_table()
        entry = table.defense_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (360885, 36333),
            "Invalid defense weapon troop distribution",
        )

    def test_nountrained_spy(self):
        table = self._get_no_untrained_table()
        entry = table.spy_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (3221, 20),
            "Invalid spy weapon troop distribution",
        )

    def test_nountrained_sentry(self):
        table = self._get_no_untrained_table()
        entry = table.sentry_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (311483, 304814),
            "Invalid sentry weapon troop distribution",
        )

    def test_nountrained_untrained(self):
        table = self._get_no_untrained_table()
        entry = table.untrained_soldiers

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (0, None),
            "Invalid untrained weapon troop distribution",
        )

    def test_nountrained_tff(self):
        table = self._get_no_untrained_table()
        entry = table.total_fighting_force

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (1684268, None),
            "Invalid tff weapon troop distribution",
        )

    def test_nountrained_tcf(self):
        table = self._get_no_untrained_table()
        entry = table.total_covert_force

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (311503, None),
            "Invalid tcf weapon troop distribution",
        )

    def test_untrained_untrained(self):
        table = self._get_untrained_table()
        entry = table.untrained_soldiers

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (1120, None),
            "Invalid untrained soldier count (untrained)",
        )


class RocUserPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_userpage(self) -> gp.RocUserPage:
        path = "/testpages/simplepages/userpage.html"
        soup = _getsoup(path)
        return gp.RocUserPage(soup)

    def test_userpage_loggedin(self):
        page = self._get_userpage()
        entry = page.logged_in

        self.assertTrue(entry, "Invalid login status on user page")

    def test_userpage_gold(self):
        page = self._get_userpage()
        entry = page.gold

        self.assertEqual(entry, 123456789, "Invalid gold amount on user page")

    def test_userpage_name(self):
        page = self._get_userpage()
        entry = page.name

        self.assertEqual(entry, "usersname", "Invalid user name on user page")

    def test_userpage_rank(self):
        page = self._get_userpage()
        entry = page.rank

        self.assertEqual(entry, 32, "Invalid user rank on user page")

    def test_userpage_turns(self):
        page = self._get_userpage()
        entry = page.turns

        self.assertEqual(entry, 4333, "Invalid user turns on user page")


class RocCooldownPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests


class RocImageCaptchaPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests


class ArmoryPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_page_path(self):
        return "/testpages/armory/"

    def _get_basic_armory(self) -> pages.RocArmoryPage:
        path = self._get_page_path() + "armorybasic.html"
        soup = _getsoup(path)
        return pages.RocArmoryPage(soup)

    # TODO add tests


class RecruitPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_no_captcha_page(self) -> pages.RocRecruitPage:
        path = "/testpages/recruit/recruit_no_captcha.html"
        soup = _getsoup(path)
        return pages.RocRecruitPage(soup)

    def _get_captcha_page(self) -> pages.RocRecruitPage:
        path = "/testpages/recruit/recruit_captcha.html"
        soup = _getsoup(path)
        return pages.RocRecruitPage(soup)

    def test_nocaptcha_captcha_status(self):
        page = self._get_no_captcha_page()

        self.assertEqual(
            page.captcha_hash, None, "Captcha hash on cooldown should be None"
        )

    def test_nocaptcha_spm(self):
        page = self._get_no_captcha_page()
        spm = page.soldiers_per_minute
        self.assertEqual(spm, 70, "Soldiers per minute is not correct value")

    def test_captcha_captcha_status(self):
        page = self._get_captcha_page()

        self.assertEqual(
            page.captcha_hash,
            "05537ef36072099afa7011808bdf40e3",
            "Captcha hash was not expected value",
        )

    def test_captcha_spm(self):
        page = self._get_captcha_page()
        spm = page.soldiers_per_minute

        self.assertEqual(spm, 60, "Soldiers per minute is not correct value")


class KeepPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = "/testpages/keep/"

    def _get_6k_0b_rep_page(self) -> pages.RocKeepPage:
        path = self._pagepath + "6k0brep.html"
        soup = _getsoup(path)
        return pages.RocKeepPage(soup)

    def test_keycount(self):
        page = self._get_6k_0b_rep_page()

        self.assertEqual(
            page.key_count, 6, "Unbroken key count does not match expected value"
        )

    def test_6k_0b_rep(self):
        page = self._get_6k_0b_rep_page()

        self.assertEqual(
            page.broken_key_count,
            0,
            "Broken key count does not match expect value of zero",
        )

    # TODO: Get test pages and implement test cases

    def test_6k_0b_norep(self):
        pass

    def test_0k_1b_norep(self):
        pass

    def test_0k_1b_rep(self):
        pass

    def test_0k_0b_norep(self):
        pass

    def test_0k_0b_rep(self):
        pass

    def test_1k_1b_rep(self):
        pass

    def test_1k_1b_norep(self):
        pass


class TrainingPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = "/testpages/training/"

    def _get_allmercs_page(self) -> pages.RocTrainingPage:
        path = self._pagepath + "trainingallmercs.html"
        soup = _getsoup(path)
        return pages.RocTrainingPage(soup)

    def _get_0am_page(self) -> pages.RocTrainingPage:
        path = self._pagepath + "training0am.html"
        soup = _getsoup(path)
        return pages.RocTrainingPage(soup)

    def _get_none_avail_mercs(self) -> pages.RocTrainingPage:
        path = self._pagepath + "training_none_avail.html"
        soup = _getsoup(path)
        return pages.RocTrainingPage(soup)

    def test_stats_table(self):
        page = self._get_allmercs_page()

        self.assertIsNotNone(
            page.stats_table, "Training page stat table should not be none"
        )

        self.assertEqual(
            page.stats_table.kills,
            16921,
        )

    def test_weapondist_table(self):
        page = self._get_0am_page()

        self.assertIsNotNone(
            page.weapon_distribution_table,
            "Training page weapon dist table should not be none",
        )

        self.assertEqual(
            page.weapon_distribution_table.untrained_soldiers.soldiers, 71771
        )

    def test_allmercs_values(self):
        page = self._get_allmercs_page()

        self.assertTupleEqual(
            (page.attack_mercenaries.count, page.attack_mercenaries.income),
            (2, -20),
            "Incorrect attack mercs pair",
        )

        self.assertTupleEqual(
            (page.defense_mercenaries.count, page.defense_mercenaries.income),
            (107630, -1076300),
            "Incorrect defense merc pair",
        )

        self.assertTupleEqual(
            (page.untrained_mercenaries.count, page.untrained_mercenaries.income),
            (69555, -347775),
            "Inccorect defense merc pair",
        )

    def test_0am_values(self):
        page = self._get_0am_page()

        self.assertTupleEqual(
            (page.attack_mercenaries.count, page.attack_mercenaries.income),
            (0, 0),
            "Incorrect attack mercs pair",
        )

        self.assertTupleEqual(
            (page.defense_mercenaries.count, page.defense_mercenaries.income),
            (107630, -1076300),
            "Incorrect defense merc pair",
        )

        self.assertTupleEqual(
            (page.untrained_mercenaries.count, page.untrained_mercenaries.income),
            (69555, -347775),
            "Incorrect defense merc pair",
        )

    def test_allmercs_availmercs(self):
        page = self._get_allmercs_page()

        self.assertTupleEqual(
            (page.avail_attack_mercs.count, page.avail_attack_mercs.income),
            (104653, 2500),
            "Incorrect number/cost of attack mercenaries",
        )

        self.assertTupleEqual(
            (page.avail_defense_mercs.count, page.avail_defense_mercs.income),
            (114653, 2500),
            "Incorrect number/cost of defense mercenaries",
        )

        self.assertTupleEqual(
            (page.avail_untrained_mercs.count, page.avail_untrained_mercs.income),
            (114653, 2000),
            "Incorrect number/cost of untrained mercenaries",
        )

    def test_none_avail_merccount(self):
        page = self._get_none_avail_mercs()

        self.assertTupleEqual(
            (
                page.avail_attack_mercs.count,
                page.avail_defense_mercs.count,
                page.avail_untrained_mercs.count,
            ),
            (50664, 0, 0),
            "Incorrect amount of mercenaries",
        )

    def test_event_merc_cost(self):
        page = self._get_none_avail_mercs()

        self.assertTupleEqual(
            (
                page.avail_untrained_mercs.income,
                page.avail_defense_mercs.income,
                page.avail_untrained_mercs.income,
            ),
            (577, 577, 577),
            "Incorrect cost of mercenaries during event",
        )

    def test_attack_soldier_costs(self):
        page = self._get_allmercs_page()

        self.assertEqual(page.attack_sold_cost, 1000)

    def test_defense_soldier_costs(self):
        page = self._get_allmercs_page()

        self.assertEqual(page.defense_sold_cost, 1500)

    def test_spy_costs(self):
        page = self._get_allmercs_page()

        self.assertEqual(page.spy_sold_cost, 2500)

    def test_sentry_cost(self):
        page = self._get_allmercs_page()

        self.assertEqual(page.sentry_sold_cost, 3000)


class BasePageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = "/testpages/base/"

    def _get_dubtrub_page(self) -> pages.RocBasePage:
        path = self._pagepath + "dubtrub.html"
        soup = _getsoup(path)
        return pages.RocBasePage(soup)

    def _get_stoleturn_page(self) -> pages.RocBasePage:
        path = self._pagepath + "stoleturn.html"
        soup = _getsoup(path)
        return pages.RocBasePage(soup)

    def _get_basewithofficers_page(self) -> pages.RocBasePage:
        path = self._pagepath + "basewithofficers.html"
        soup = _getsoup(path)
        return pages.RocBasePage(soup)

    def _get_basefoundbrokenkey_page(self) -> pages.RocBasePage:
        path = self._pagepath + "basefoundbrokenkey.html"
        soup = _getsoup(path)
        return pages.RocBasePage(soup)

    def _get_noactive_events_page(self) -> pages.RocBasePage:
        path = self._pagepath + "base_noactive_events.html"
        soup = _getsoup(path)
        return pages.RocBasePage(soup)

    def test_dubtrub(self):
        page = self._get_dubtrub_page()

        self.assertEqual(
            len(page.current_events),
            1,
            "Incorrect number of current events on dubtrub page",
        )

        self.assertEqual(
            len(page.upcoming_events),
            2,
            "Incorrect number of upcoming events on dubtrub page",
        )

        self.assertEqual(
            page.current_events[0].name,
            "Double Trouble",
            "Incorrect current event name on dubtrub page",
        )

    def test_stoleturns(self):
        page = self._get_stoleturn_page()

        self.assertIsNotNone(
            page.recenty_activity, "Recent activity should not be none"
        )
        self.assertEqual(
            len(page.recenty_activity),
            10,
            "Recenty activity list is not correct length",
        )
        self.assertEqual(
            "stole" in page.recenty_activity[7].activity_text,
            True,
            "7th activity text should be user stealing turns.",
        )

    def test_dist_table(self):
        page = self._get_basewithofficers_page()

        self.assertIsNotNone(page.weapon_distribution_table)

        self.assertEqual(
            page.weapon_distribution_table.untrained_soldiers.soldiers, 2818
        )

        self.assertEqual(
            page.weapon_distribution_table.total_fighting_force.soldiers, 6918
        )

    def test_stats_table(self):
        page = self._get_dubtrub_page()

        self.assertIsNotNone(page.stats_table)

        self.assertEqual(page.stats_table.strike.action, 12630025)

        self.assertEqual(page.stats_table.sentry.bonus, 15)

        self.assertEqual(page.stats_table.spy.rank, 10)

    def test_totals_table(self):
        pass

    def test_alliance(self):
        pass

    def test_officers(self):
        pass

    def test_commandchain(self):
        pass

    def test_serverdate(self):
        pass

    def test_soldier_source(self):
        pass


class AttackPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = "/testpages/attack/attack/"

    def _get_offline_page(self) -> pages.RocAttackPage:
        path = self._pagepath + "attack_offline.html"
        soup = _getsoup(path)
        return pages.RocAttackPage(soup)

    def _get_online_page(self) -> pages.RocAttackPage:
        path = self._pagepath + "attack_online.html"
        soup = _getsoup(path)
        return pages.RocAttackPage(soup)

    def test_name_correct(self):
        page = self._get_offline_page()

        self.assertEqual(page.target_name, "offlineuser")

    def test_online_correct(self):
        page = self._get_online_page()

        self.assertEqual(page.is_online, True)

    def test_offline_correct(self):
        page = self._get_offline_page()

        self.assertEqual(page.is_online, False)

    def test_turns_correct(self):
        page = self._get_online_page()

        self.assertEqual(page.max_attack_turns, 12)

    def test_id_correct(self):
        page = self._get_online_page()

        self.assertEqual(page.target_id, "31143")

    def test_unusualnumber_turns_correct(self):
        page = self._get_offline_page()

        self.assertEqual(page.max_attack_turns, 3)
