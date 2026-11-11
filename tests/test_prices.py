import contextlib
import io
import random
import tempfile
import unittest
from datetime import date
from pathlib import Path

from analyzer.__main__ import DEFAULT_DATA, _build_parser, main
from analyzer.max_subarray import brute_force, divide_and_conquer, kadane
from analyzer.prices import daily_changes, holding_return_bps, load_csv, window_bounds
from analyzer.report import analyze, render_text

FIXTURE = Path(__file__).parent / "fixtures" / "sample.csv"


class PriceTests(unittest.TestCase):
    def test_sample_window_and_returns(self) -> None:
        book = load_csv(FIXTURE)
        apple = book["AAPL"]
        changes = daily_changes(apple)
        self.assertEqual([change // 1_000_000 for change in changes], [-2, 4, 3, -6, 5])
        found = kadane(changes)
        self.assertEqual((found.total, found.start, found.end), (7_000_000, 1, 2))
        buy_day, sell_day, buy_px, sell_px = window_bounds(apple, found)
        self.assertEqual(buy_day, date(2020, 1, 3))
        self.assertEqual(sell_day, date(2020, 1, 7))
        self.assertEqual(sell_px - buy_px, found.total)
        self.assertEqual(holding_return_bps(apple), 4000)
        self.assertEqual(holding_return_bps(book["MSFT"]), 5000)
        self.assertEqual(holding_return_bps(book["XOM"]), 2500)
        self.assertEqual(holding_return_bps(book["NVDA"]), -7000)

    def test_analyze_agrees_across_algorithms(self) -> None:
        report = analyze(FIXTURE, "AAPL", 3, None, None)
        self.assertTrue(all(item.window == report.windows[0].window for item in report.windows))
        self.assertTrue(all(item.picked == report.movers[0].picked for item in report.movers))
        self.assertEqual([item.ticker for item in report.movers[0].picked], ["MSFT", "AAPL", "XOM"])
        text = render_text(report)
        self.assertIn("buy 2020-01-03", text)
        self.assertIn("sell 2020-01-07", text)
        self.assertIn("2020-01-02 through 2020-01-09", text)
        self.assertIn("Maximum-subarray algorithms agree.", text)
        self.assertIn("Top-K algorithms agree.", text)
        self.assertIn("40.00%", text)
        self.assertIn("50.00%", text)

    def test_cli_defaults_to_the_kaggle_csv(self) -> None:
        parser = _build_parser()
        args = parser.parse_args([])
        self.assertEqual(args.data, DEFAULT_DATA)
        self.assertEqual(args.data, Path("data/SP500_Historical_Data.csv"))
        destinations = {action.dest for action in parser._actions}
        self.assertNotIn("fetch", destinations)

    def test_cli_on_sample(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main([str(FIXTURE), "--ticker", "AAPL", "--k", "3", "--html", "/tmp/sample-results.html"])
        self.assertEqual(code, 0)
        self.assertIn("MSFT", buffer.getvalue())
        page = Path("/tmp/sample-results.html").read_text(encoding="utf-8")
        self.assertIn("Best buy/sell window for AAPL", page)
        self.assertIn("quickselect", page)

    def test_loader_rejects_a_missing_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            path.write_text("Ticker,Date,Close\nAAPL,2020-01-02,10\n", encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                load_csv(path)
        self.assertIn("Adj Close", str(caught.exception))

    def test_loader_skips_blank_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blank.csv"
            path.write_text(
                "Ticker,Date,Adj Close\n"
                "AAPL,2020-01-02,10\n"
                ",,\n"
                "AAPL,,\n"
                "AAPL,2020-01-03,12\n",
                encoding="utf-8",
            )
            book = load_csv(path)
        self.assertEqual(book["AAPL"].dates, (date(2020, 1, 2), date(2020, 1, 3)))
        self.assertEqual([price // 1_000_000 for price in book["AAPL"].ticks], [10, 12])

    def test_loader_keeps_the_last_price_on_a_duplicate_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.csv"
            path.write_text(
                "Ticker,Date,Adj Close\n"
                "AAPL,2020-01-02,10\n"
                "AAPL,2020-01-02,15\n"
                "AAPL,2020-01-03,12\n",
                encoding="utf-8",
            )
            book = load_csv(path)
        self.assertEqual(book["AAPL"].dates, (date(2020, 1, 2), date(2020, 1, 3)))
        self.assertEqual([price // 1_000_000 for price in book["AAPL"].ticks], [15, 12])

    def test_long_random_windows_agree(self) -> None:
        rng = random.Random(3440)
        samples = [
            [0] * 2_000,
            [rng.choice([-(10**12), 0, 10**12]) for _ in range(2_000)],
            [rng.randint(-(10**6), 10**6) for _ in range(2_000)],
            [0],
            [],
        ]
        for values in samples:
            expected = kadane(values)
            self.assertEqual(brute_force(values), expected)
            self.assertEqual(divide_and_conquer(values), expected)


if __name__ == "__main__":
    unittest.main()
