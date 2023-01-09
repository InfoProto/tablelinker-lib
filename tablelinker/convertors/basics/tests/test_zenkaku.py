import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..zenkaku import ToHarfNumberFilter, to_harf_number


class TestWarekiFn(unittest.TestCase):
    def test_to_harf_number(self):
        self.assertEqual(to_harf_number("１２３４５６７８９０"), "1234567890")
        self.assertEqual(to_harf_number("１２３全角文字"), "123全角文字")


class TestToSeirekiFilter(unittest.TestCase):
    def test_filter(self):
        job = LocalJob(
            filter=ToHarfNumberFilter,
            filter_params={"attr": 2,},
            input=ArrayInputCollection(
                [
                    ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                    [1, "aaa1", "１２３４５６７８９０", "ccc1", "ddd1", "eee1"],
                    [1, "aaa2", "１２３全角文字", "ccc2", "ddd2", "eee2"],
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
                [1, "aaa1", "1234567890", "ccc1", "ddd1", "eee1"],
                [1, "aaa2", "123全角文字", "ccc2", "ddd2", "eee2"],
                [1, "aaa3", "xxx,yyy,zzz", "ccc3", "ddd3", "eee3"],
            ],
        )
