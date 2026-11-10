import contextlib
import io
import unittest
from datetime import date
from pathlib import Path

from analyzer.__main__ import DEFAULT_DATA, _build_parser, main
from analyzer.fetch import parse_constituent_symbols
from analyzer.max_subarray import kadane
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
        fetch_help = next(action.help for action in parser._actions if action.dest == "fetch")
        self.assertIn("Optional fallback", fetch_help)
        self.assertIn("Yahoo", fetch_help)

    def test_cli_on_sample(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = main([str(FIXTURE), "--ticker", "AAPL", "--k", "3", "--html", "/tmp/sample-results.html"])
        self.assertEqual(code, 0)
        self.assertIn("MSFT", buffer.getvalue())
        page = Path("/tmp/sample-results.html").read_text(encoding="utf-8")
        self.assertIn("Best buy/sell window for AAPL", page)
        self.assertIn("quickselect", page)

    def test_symbol_parser_stops_at_the_constituents_table(self) -> None:
        html = """
        <table id="constituents">
        <tr><td>BRK.B</td><td>Berkshire</td></tr>
        <tr><td>AAPL</td><td>Apple</td></tr>
        <tr><td>not a ticker</td></tr>
        </table>
        <table><tr><td>Alphabet Inc.
        Amazon</td></tr></table>
        """
        self.assertEqual(parse_constituent_symbols(html), ["BRK-B", "AAPL"])


if __name__ == "__main__":
    unittest.main()
