import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..wareki import ToSeirekiFilter, wareki2seireki


class TestWarekiFn(unittest.TestCase):
    def test_wareki2seireki(self):
        self.assertEqual(wareki2seireki("昭和55年1月22日"), "1980年1月22日")


class TestToSeirekiFilter(unittest.TestCase):
    def test_filter(self):
        job = LocalJob(
            filter=ToSeirekiFilter,
            filter_params={"attr": 2,},
            input=ArrayInputCollection(
                [
                    ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                    [1, "aaa1", "昭和55年1月22日", "ccc1", "ddd1", "eee1"],
                    [1, "aaa2", "昭和55年1月22日", "ccc2", "ddd2", "eee2"],
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
                [1, "aaa1", "1980年1月22日", "ccc1", "ddd1", "eee1"],
                [1, "aaa2", "1980年1月22日", "ccc2", "ddd2", "eee2"],
                [1, "aaa3", "xxx,yyy,zzz", "ccc3", "ddd3", "eee3"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
