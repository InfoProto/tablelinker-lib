import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..split_col import PivotColFilter, SplitColFilter, split


class TestSplitFn(unittest.TestCase):
    def test_split(self):
        self.assertEqual(split("AAA,BBB", separator=","), ["AAA", "BBB"])


class TestSplitColFilter(unittest.TestCase):
    def test_concat_filter(self):
        job = LocalJob(
            filter=SplitColFilter,
            filter_params={"attr": 2, "separator": ",", "output_attr_name": "output_attr_name",},
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
                [
                    "num",
                    "col-a",
                    "col-b",
                    "col-c",
                    "col-d",
                    "col-e",
                    "output_attr_name_1",
                    "output_attr_name_2",
                    "output_attr_name_3",
                ],
                [1, "aaa1", "xxx,yyy,zzz", "ccc1", "ddd1", "eee1", "xxx", "yyy", "zzz"],
                [1, "aaa2", "xxx,yyy,zzz", "ccc2", "ddd2", "eee2", "xxx", "yyy", "zzz"],
                [1, "aaa3", "xxx,yyy,zzz", "ccc3", "ddd3", "eee3", "xxx", "yyy", "zzz"],
            ],
        )


class TestPivotColFilter(unittest.TestCase):
    def test_concat_filter(self):
        job = LocalJob(
            filter=PivotColFilter,
            filter_params={"attr": 2, "separator": ",", "output_attr_name": "output_attr_name",},
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
                [1, "aaa1", "xxx", "ccc1", "ddd1", "eee1"],
                [1, "aaa1", "yyy", "ccc1", "ddd1", "eee1"],
                [1, "aaa1", "zzz", "ccc1", "ddd1", "eee1"],
                [1, "aaa2", "xxx", "ccc2", "ddd2", "eee2"],
                [1, "aaa2", "yyy", "ccc2", "ddd2", "eee2"],
                [1, "aaa2", "zzz", "ccc2", "ddd2", "eee2"],
                [1, "aaa3", "xxx", "ccc3", "ddd3", "eee3"],
                [1, "aaa3", "yyy", "ccc3", "ddd3", "eee3"],
                [1, "aaa3", "zzz", "ccc3", "ddd3", "eee3"],
            ],
        )


# class TestPivotFilter(unittest.TestCase):

#     def test_pivot_filter(self):
#         pass
