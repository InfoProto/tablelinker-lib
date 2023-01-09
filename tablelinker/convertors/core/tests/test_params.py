import unittest

from ..params import IntParam
from ..validators import Errors, IntValidator, RangeValidator


class TestParamSet(unittest.TestCase):
    def setUp(self):
        pass

    def test(self):
        pass


class TestIntParams(unittest.TestCase):
    def setUp(self):
        pass

    def test_validator_ok(self):
        param = IntParam("value", validators=[IntValidator(), RangeValidator(max=10, min=5)])
        self.assertEqual(None, param.get_value(None, None))
        self.assertTrue(param.validate("5", Errors()))
        self.assertTrue(param.validate("8", Errors()))
        self.assertTrue(param.validate("10", Errors()))

    def test_validator_ng(self):
        param = IntParam("value", validators=[IntValidator(), RangeValidator(max=10, min=5)])
        self.assertEqual(None, param.get_value(None, None))
        self.assertFalse(param.validate("4", Errors()))
        self.assertFalse(param.validate("11", Errors()))
        self.assertFalse(param.validate("a", Errors()))

    def test_get_value_without_default_value(self):
        param = IntParam("value")
        self.assertEqual(None, param.get_value(None, None))
        self.assertEqual(1, param.get_value("1", None))

    def test_get_value_with_default_value(self):
        param = IntParam("value", default_value=10)
        self.assertEqual(10, param.get_value(None, None))
        self.assertEqual(1, param.get_value("1", None))
