import unittest

from ..validators import Errors, FloatValidator, IntValidator, RangeValidator


class TestIntValidator(unittest.TestCase):
    def setUp(self):
        self.validator = IntValidator()

    def test_ok(self):
        actual = Errors()
        self.validator.valid("6", actual)
        self.validator.valid("9", actual)
        self.validator.valid("10", actual)
        self.assertFalse(actual.has_error())

    def test_ng(self):
        actual = Errors()
        self.validator.valid("qqq", actual)
        self.validator.valid("1.1", actual)
        self.assertTrue(actual.has_error())


class TestFloatValidator(unittest.TestCase):
    def setUp(self):
        self.validator = FloatValidator()

    def test_ok(self):
        actual = Errors()
        self.validator.valid("5.5", actual)
        self.validator.valid("9", actual)
        self.validator.valid("9.6", actual)
        self.validator.valid("10.1", actual)
        self.assertFalse(actual.has_error())

    def test_ng(self):
        actual = Errors()
        self.validator.valid("qqq", actual)
        self.validator.valid("eee", actual)
        self.assertTrue(actual.has_error())


class TestRangeValidatorByInt(unittest.TestCase):
    def setUp(self):
        self.validator = RangeValidator(max=10, min=5)

    def test_ok(self):
        actual = Errors()
        self.validator.valid(6, actual)
        self.validator.valid(9, actual)
        self.validator.valid(10, actual)
        self.assertFalse(actual.has_error())

    def test_ng(self):
        actual = Errors()
        self.validator.valid(4, actual)
        self.validator.valid(11, actual)
        self.assertTrue(actual.has_error())


class TestRangeValidatorByFloat(unittest.TestCase):
    def setUp(self):
        self.validator = RangeValidator(max=10.5, min=5.5)

    def test_ok(self):
        actual = Errors()
        self.validator.valid("5.5", actual)
        self.validator.valid("9", actual)
        self.validator.valid("9.9", actual)
        self.validator.valid("10.5", actual)
        self.assertFalse(actual.has_error())

    def test_ng(self):
        actual = Errors()
        self.validator.valid("5.4", actual)
        self.validator.valid("10.6", actual)
        self.assertTrue(actual.has_error())
