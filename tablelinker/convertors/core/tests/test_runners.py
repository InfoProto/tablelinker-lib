import os
import unittest

from ..core import Job, LocalRunner
from ..filters import NoopFilter
from ..input import ArrayInputCollection, CsvInputCollection
from ..output import ArrayOutputCollection


class TestLocalRunner(unittest.TestCase):
    """LocalRunner with array."""

    def test_convertor_with_array(self):
        """test method for tashizan"""
        filter = NoopFilter
        filter_params = {}
        runner = LocalRunner()
        input = ArrayInputCollection([[1, 2, 3]])
        output = ArrayOutputCollection()

        job = Job(runner, filter, filter_params, input, output)
        job.run()

        actual = output.get_data()
        self.assertEqual([[1, 2, 3]], actual)

    def test_convertor_with_csv(self):
        """test method for tashizan"""
        filter = NoopFilter
        filter_params = {}
        runner = LocalRunner()
        input = CsvInputCollection(os.path.dirname(__file__) + "/fixtures/test.csv")
        output = ArrayOutputCollection()

        job = Job(runner, filter, filter_params, input, output)
        job.run()

        actual = output.get_data()
        expected = [
            ["A", "B", "C"],
            ["1", "aa", "AA"],
            ["2", "bb", "BB"],
            ["3", "cc", "DD"],
            ["4", "dd", "CC"],
        ]
        self.assertEqual(expected, actual)


# python -m unittest convertors.core.tests
