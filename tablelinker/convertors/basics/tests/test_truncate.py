import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..truncate import TruncateFilter, truncate


class TestTruncateFn(unittest.TestCase):
    def test_truncate(self):
        self.assertEqual(truncate("1234567890", length=5, omission="..."), "12345...")


class TestTruncateFilter(unittest.TestCase):
    def test_concat_filter(self):
        job = LocalJob(
            filter=TruncateFilter,
            filter_params={"attr": 2, "length": 5, "omission": "...",},
            input=ArrayInputCollection(
                [
                    ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                    [1, "aaa1", "xxx,yyy,zzz", "ccc1", "ddd1", "eee1"],
                    [1, "aaa2", "xxx,yyy,zzz", "ccc2", "ddd2", "eee2"],
                    [1, "aaa3", "xxx,yyy,zzz", "ccc3", "ddd3", "eee3"],
                ]
            ),
            output=ArrayOutputCollection([]),
        )
        job.run()

        self.assertEqual(
            job.get_result().get_data(),
            [
                ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                [1, "aaa1", "xxx,y...", "ccc1", "ddd1", "eee1"],
                [1, "aaa2", "xxx,y...", "ccc2", "ddd2", "eee2"],
                [1, "aaa3", "xxx,y...", "ccc3", "ddd3", "eee3"],
            ],
        )
