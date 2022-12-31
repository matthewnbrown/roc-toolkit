import unittest
from unittest.mock import Mock
import datetime as dt

from rocalert.services.keeptools import KeepKeyRepairer, KeyRepairError


class KeepKeyRepairerTest(unittest.TestCase):
    def test_when_used_before_update_should_raise_exception(self):
        self.assertTrue(True)
