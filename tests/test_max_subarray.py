import random
import unittest

from analyzer.max_subarray import ALGORITHMS, brute_force, divide_and_conquer, kadane


CLRS = [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7]


class MaxSubarrayTests(unittest.TestCase):
    def test_clrs_example(self) -> None:
        for name, function in ALGORITHMS.items():
            with self.subTest(name=name):
                found = function(CLRS)
                self.assertEqual(found.total, 43)
                self.assertEqual((found.start, found.end), (7, 10))

    def test_all_negative_skips_the_trade(self) -> None:
        for function in ALGORITHMS.values():
            found = function([-5, -1, -3])
            self.assertTrue(found.empty)
            self.assertEqual(found.total, 0)

    def test_equal_windows_keep_the_earliest(self) -> None:
        values = [5, -1, 3, -10, 5, -1, 3]
        for function in ALGORITHMS.values():
            found = function(values)
            self.assertEqual((found.total, found.start, found.end), (7, 0, 2))

    def test_leading_zero_keeps_the_earlier_start(self) -> None:
        for function in ALGORITHMS.values():
            found = function([0, 5])
            self.assertEqual((found.total, found.start, found.end), (5, 0, 1))

    def test_empty_and_single(self) -> None:
        for function in ALGORITHMS.values():
            self.assertTrue(function([]).empty)
            self.assertEqual((function([4]).total, function([4]).start), (4, 0))
            self.assertTrue(function([-4]).empty)

    def test_algorithms_agree_on_random_input(self) -> None:
        rng = random.Random(3440)
        for length in range(0, 40):
            values = [rng.randint(-15, 15) for _ in range(length)]
            expected = brute_force(values)
            self.assertEqual(divide_and_conquer(values), expected)
            self.assertEqual(kadane(values), expected)


if __name__ == "__main__":
    unittest.main()
