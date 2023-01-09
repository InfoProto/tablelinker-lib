import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..concat_col import ConcatColFilter, concat


class TestConcatFn(unittest.TestCase):
    def test_concat(self):
        self.assertEqual(concat(["AAA", "BBB"]), "AAABBB")
        self.assertEqual(concat(["AAA", "BBB"], separator="-"), "AAA-BBB")


class TestConcatColFilter(unittest.TestCase):
    def test_run_filter(self):
        job = LocalJob(
            filter=ConcatColFilter,
            filter_params={"attr1": 1, "attr2": 2, "separator": "-", "output_attr_name": "output_attr_name",},
            input=ArrayInputCollection(
                [
                    ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                    [1, "aaa1", "bbb1", "ccc1", "ddd1", "eee1"],
                    [1, "aaa2", "bbb2", "ccc2", "ddd2", "eee2"],
                    [1, "aaa3", "bbb3", "ccc3", "ddd3", "eee3"],
                ]
            ),
            output=ArrayOutputCollection([]),
        )
        job.run()

        self.assertEqual(
            job.get_result().get_data(),
            [
                ["num", "col-a", "col-b", "col-c", "col-d", "col-e", "output_attr_name"],
                [1, "aaa1", "bbb1", "ccc1", "ddd1", "eee1", "aaa1-bbb1"],
                [1, "aaa2", "bbb2", "ccc2", "ddd2", "eee2", "aaa2-bbb2"],
                [1, "aaa3", "bbb3", "ccc3", "ddd3", "eee3", "aaa3-bbb3"],
            ],
        )

    def test_validation_error(self):
        job = LocalJob(
            filter=ConcatColFilter, filter_params={}, input=ArrayInputCollection([]), output=ArrayOutputCollection([])
        )

        job.run()

        self.assertEqual(
            job.errors().error_messages,
            {"attr1": ["対象列1は、必須入力です。", "対象列1は、数字を入力してください。"], "attr2": ["対象列2は、必須入力です。", "対象列2は、数字を入力してください。"],},
        )
