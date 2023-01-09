import unittest

from convertors.core import ArrayInputCollection, ArrayOutputCollection, LocalJob

from ..delete_row import StringContainDeleteRowFilter


class TestStringContainSelectRowFilter(unittest.TestCase):
    def test_concat_filter(self):
        job = LocalJob(
            filter=StringContainDeleteRowFilter,
            filter_params={"attr": 3, "query": "test",},
            input=ArrayInputCollection(
                [
                    ["num", "col-a", "col-b", "col-c", "col-d", "col-e"],
                    [1, "aaa1", "bbb1", "ccc_test_ccc", "ddd1", "eee1"],
                    [1, "aaa2", "bbb2", "ccc_test", "ddd2", "eee2"],
                    [1, "aaa3", "bbb3", "test_ccc3", "ddd3", "eee3"],
                    [1, "aaa4", "bbb4", "ccc4", "ddd4", "eee4"],
                ]
            ),
            output=ArrayOutputCollection([]),
        )
        job.run()

        self.assertEqual(
            job.get_result().get_data(),
            [["num", "col-a", "col-b", "col-c", "col-d", "col-e"], [1, "aaa4", "bbb4", "ccc4", "ddd4", "eee4"],],
        )
