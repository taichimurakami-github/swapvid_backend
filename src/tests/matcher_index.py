import unittest
from Matcher.index import compare_lbbfmt


class TestCompareAsLbbFmt(unittest.TestCase):
    def test_success_1(self):
        lbbfmt_testdata1 = {
            "offset": [[0, 0], [0, 0]],
            "linePosition": [[743, 752], [777, 955]],
            "content": "jclune@ gmail.com",
        }

        lbbfmt_testdata2 = {
            "offset": [[0, 0], [0, 0]],
            "linePosition": [[807, 0], [31, 1066]],
            "content": "Jclune @ gmail.com",
        }

        match_result = compare_lbbfmt(lbbfmt_testdata1, lbbfmt_testdata2)

        self.assertEqual(len(match_result), 2)

    def test_failure_1(self):
        lbbfmt_testdata1 = {
            "offset": [[10200, 0], [0, 0]],
            "linePosition": [[10501, 617], [642, 1402]],
            "content": "Despite the foundation model\u2019s zero-shot rollout performance plateauing 1/3 into training (Fig. 4,",
        }

        lbbfmt_testdata2 = {
            "offset": [[0, 0], [0, 0]],
            "linePosition": [[807, 0], [31, 1066]],
            "content": "Jclune @ gmail.com",
        }

        match_result = compare_lbbfmt(lbbfmt_testdata1, lbbfmt_testdata2)

        self.assertEqual(len(match_result), 0)
