import random
import unittest

from analyzer.top_k import ALGORITHMS, Scored, top_k_heap, top_k_quickselect, top_k_sort


class TopKTests(unittest.TestCase):
    def test_ties_break_on_ticker(self) -> None:
        items = [Scored("ZZ", 5), Scored("AA", 5), Scored("MM", 5), Scored("BB", 9)]
        expected = [Scored("BB", 9), Scored("AA", 5), Scored("MM", 5)]
        for function in ALGORITHMS.values():
            self.assertEqual(function(items, 3), expected)

    def test_edges(self) -> None:
        items = [Scored("A", 1), Scored("B", 2)]
        for function in ALGORITHMS.values():
            self.assertEqual(function(items, 0), [])
            self.assertEqual(function(items, 5), [Scored("B", 2), Scored("A", 1)])

    def test_algorithms_agree(self) -> None:
        rng = random.Random(3440)
        for _ in range(40):
            items = [Scored(f"T{index:03d}", rng.randint(-20, 20)) for index in range(30)]
            k = rng.randint(0, 35)
            expected = top_k_sort(items, k)
            self.assertEqual(top_k_heap(items, k), expected)
            self.assertEqual(top_k_quickselect(items, k), expected)


if __name__ == "__main__":
    unittest.main()
