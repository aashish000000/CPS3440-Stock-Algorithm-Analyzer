"""Build the CPS 3440 slide deck from results/results.json."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "CPS3440-Stock-Algorithm-Analyzer.pptx"
QR = ROOT / "docs" / "assets" / "site-qr.png"
TIME_FIG = ROOT / "docs" / "assets" / "max-subarray-time.png"
HEAP_FIG = ROOT / "docs" / "assets" / "heap-cases.png"
SITE = "https://aashish000000.github.io/CPS3440-Stock-Algorithm-Analyzer/"

GREEN = RGBColor(0x14, 0x34, 0x2B)
CREAM = RGBColor(0xF6, 0xF4, 0xEF)
INK = RGBColor(0x1C, 0x24, 0x30)
MUTED = RGBColor(0x3D, 0x4A, 0x44)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD = RGBColor(0xFF, 0xFC, 0xF7)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def load_site():
    spec = importlib.util.spec_from_file_location("site_render", ROOT / "docs" / "render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.load()


def set_run(paragraph, text, size, bold=False, color=INK, font="Calibri", align=None):
    paragraph.alignment = align or PP_ALIGN.LEFT
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return run


def add_text(slide, left, top, width, height, text, size=20, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri", anchor=MSO_ANCHOR.TOP):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = shape.text_frame
    frame.word_wrap = True
    frame.auto_size = None
    frame.anchor = anchor
    set_run(frame.paragraphs[0], text, size, bold, color, font, align)
    return shape


def add_bullets(slide, left, top, width, height, items, size=20, color=INK, space=10):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = shape.text_frame
    frame.word_wrap = True
    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.space_after = Pt(space)
        set_run(paragraph, item, size, False, color)
    return shape


def fill_background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def top_bar(slide):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(0), Emu(0), SLIDE_W, Inches(0.12))
    shape.fill.solid()
    shape.fill.fore_color.rgb = GREEN
    shape.line.fill.background()


def footer(slide, speaker, page, total):
    add_text(slide, 0.48, 7.05, 9.2, 0.32, f"{speaker}   ·   CPS 3440", 13, False, MUTED)
    add_text(slide, 10.2, 7.05, 2.6, 0.32, f"{page}  /  {total}", 13, False, MUTED, PP_ALIGN.RIGHT)


def blank(prs, speaker, page, total, title):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill_background(slide, CREAM)
    top_bar(slide)
    add_text(slide, 0.48, 0.28, 12.3, 0.72, title, 30, True, GREEN, font="Georgia")
    footer(slide, speaker, page, total)
    notes = slide.notes_slide.notes_text_frame
    notes.text = f"{speaker}. See presentation/SPEAKER_SCRIPT.md for the timed lines on this slide."
    return slide


def build() -> Path:
    site, results = load_site()
    window = site.window_row
    top = site.top_row
    brute_10k = site.fmt_ms(window(results, "brute_force", 10_000)["median_ms"])
    brute_1k = site.fmt_ms(window(results, "brute_force", 1_000)["median_ms"])
    brute_100k = site.clock(window(results, "brute_force", 100_000))
    brute_1m = site.clock(window(results, "brute_force", 1_000_000))
    kadane_10k = site.fmt_ms(window(results, "kadane", 10_000)["median_ms"])
    kadane_1m = site.fmt_ms(window(results, "kadane", 1_000_000)["median_ms"])
    divide_10k = site.fmt_ms(window(results, "divide_and_conquer", 10_000)["median_ms"])
    divide_1m = site.fmt_ms(window(results, "divide_and_conquer", 1_000_000)["median_ms"])
    slope = site.slope(results, "brute_force", 1_000, 10_000)
    divide_slope = site.slope(results, "divide_and_conquer", 10_000, 1_000_000)
    reads = site.fmt_ops(window(results, "divide_and_conquer", 1_000_000)["operations"])
    ratio = window(results, "brute_force", 10_000)["median_ms"] / window(results, "kadane", 10_000)["median_ms"]
    heap = top(results, "binary_heap", "random", 1_000_000)
    sort = top(results, "full_sort", "random", 1_000_000)
    heap_best = top(results, "binary_heap", "best_for_heap", 1_000_000)
    heap_worst = top(results, "binary_heap", "worst_for_heap", 1_000_000)
    moves = f"{results['source_moves']:,}"

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    prs.core_properties.title = "Historical Stock Market Algorithm Analyzer"
    prs.core_properties.subject = "CPS 3440 Analysis of Algorithms"
    prs.core_properties.author = "Aashish Joshi, Aron Dardouri, Bhartendra Kumar Mandal, Brian Lucero"
    total = 13

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill_background(slide, GREEN)
    add_text(slide, 0.7, 1.45, 12, 1.5, "Historical Stock Market\nAlgorithm Analyzer", 40, True, WHITE, font="Georgia")
    add_text(slide, 0.7, 3.7, 11, 0.8, "Maximum subarray and Top-K on the Kaggle S&P 500 history", 22, False, RGBColor(0xD5, 0xE6, 0xDC))
    add_text(slide, 0.7, 5.15, 11, 1.1, "Aashish Joshi    Aron Dardouri\nBhartendra Kumar Mandal    Brian Lucero", 20, False, WHITE)
    add_text(slide, 0.7, 6.5, 11, 0.4, "CPS 3440 Analysis of Algorithms  ·  Kean University", 16, False, RGBColor(0xD5, 0xE6, 0xDC))
    slide.notes_slide.notes_text_frame.text = "Aashish Joshi opens. See SPEAKER_SCRIPT.md, slide 1."

    slide = blank(prs, "Aashish Joshi", 2, total, "Two questions, one price file")
    add_bullets(
        slide,
        0.55,
        1.35,
        12.2,
        5.3,
        [
            "Best single buy and a later sell: the maximum subarray of daily adjusted-close changes.",
            "That sum is the profit per share. Ties keep the earliest window. A fully negative series means do not trade.",
            "Largest movers: Top-K under the order (higher return, then earlier ticker).",
            "On Apple in this file, every window algorithm returns the same trade: buy 8 October 2002 at $0.20, sell 2 December 2025 at $285.92, profit $285.72 per share.",
            "Among 472 stocks, NVDA leads buy-and-hold return at 210,811.11 percent.",
        ],
        size=22,
        space=12,
    )

    slide = blank(prs, "Aashish Joshi", 3, total, "The downloaded Kaggle file")
    add_bullets(
        slide,
        0.55,
        1.3,
        12.2,
        5.4,
        [
            "Source: jacksaleeby/s-and-p500-historical-data, file SP500_Historical_Data.csv.",
            "Columns: Ticker, Date, Open, High, Low, Close, Adj Close, Volume.",
            "2,703,531 rows, 472 tickers, 3 January 2000 through 20 February 2026.",
            f"{moves} daily changes, stored as integer micro-dollars so the three window algorithms compare the same integers.",
            "Scaling inputs are prefixes of 1,000, 10,000, 100,000, and 1,000,000 records from that file.",
            "python3 -m analyzer reads this CSV by default. The download steps are in data/README.md.",
        ],
        size=20,
        space=8,
    )

    slide = blank(prs, "Aashish Joshi", 4, total, "What the tool checks")
    add_bullets(
        slide,
        0.55,
        1.35,
        12.2,
        5.2,
        [
            "prices.py loads adjusted closes and turns them into daily changes.",
            "max_subarray.py runs brute force, divide and conquer, and Kadane on one ticker.",
            "top_k.py ranks the universe with a full sort, a size-K heap, and quickselect.",
            "The command line prints both groups and says whether they agree.",
            "On the Kaggle file they do agree: one Apple window, and the same top 10 movers.",
            "Unit tests cover the CLRS example, all-negative arrays, ties, and the offline sample.",
        ],
        size=22,
        space=10,
    )

    slide = blank(prs, "Aron Dardouri", 5, total, "Brute force examines every window")
    add_bullets(
        slide,
        0.55,
        1.3,
        12.2,
        5.4,
        [
            "Build a prefix array, then score every start and end with one subtraction.",
            "Every nonempty window is considered once, so the best pair is the best window.",
            "Best, average, and worst time are all Θ(n²). The loops do not stop early.",
            "Extra space is the prefix, Θ(n).",
            f"Measured medians, 5 trials: {brute_1k} at 1,000 records and {brute_10k} at 10,000.",
            f"The log-log slope on that decade is {slope}. The model value is 2. The pair count is exactly n(n+1)/2.",
        ],
        size=20,
        space=8,
    )

    slide = blank(prs, "Aron Dardouri", 6, total, "What was timed, and what was projected")
    add_bullets(
        slide,
        0.55,
        1.3,
        12.2,
        5.4,
        [
            "Sizes through 10,000 records are the median of 5 trials. Brute force at 100,000 records is one trial.",
            "The second metric is an operation count: pairs, element reads, or comparisons.",
            f"The measured 100,000-record brute-force time is {brute_100k}.",
            f"1,000,000 records projects to {brute_1m}.",
            "Only that million-record time is a projection. The dashed line is that projection. The pair count is still exact.",
        ],
        size=20,
        space=8,
    )

    slide = blank(prs, "Aron Dardouri", 7, total, "The window algorithms, on the clock")
    add_bullets(
        slide,
        0.48,
        1.2,
        6.3,
        5.5,
        [
            f"At 10,000 changes:",
            f"Brute force  {brute_10k}",
            f"Divide and conquer  {divide_10k}",
            f"Kadane  {kadane_10k}",
            f"Brute force is about {ratio:,.0f}× Kadane at that size.",
            f"At 1,000,000 changes Kadane takes {kadane_1m}.",
            f"The brute-force cell there is {brute_1m}, and it was not run. The 100,000-record cell, {brute_100k}, was.",
        ],
        size=18,
        space=6,
    )
    slide.shapes.add_picture(str(TIME_FIG), Inches(6.85), Inches(1.35), Inches(6.0), Inches(3.7))
    add_text(slide, 6.85, 5.15, 6.0, 1.5, "Solid marks were timed, including one brute-force trial at 100,000 records. The dashed segment is the projection to 1,000,000.", 14, False, MUTED)

    slide = blank(prs, "Bhartendra Kumar Mandal", 8, total, "Divide and conquer")
    add_bullets(
        slide,
        0.55,
        1.25,
        12.2,
        5.5,
        [
            "An optimal window is entirely on the left, entirely on the right, or it crosses the midpoint.",
            "The crossing window is a maximum suffix of the left half plus a maximum prefix of the right half.",
            "That case is what makes the induction work. Ties keep the earlier index.",
            "Recurrence: T(n) = 2T(n/2) + Θ(n). The Master Theorem gives Θ(n log n) on every input.",
            "Extra space is the Θ(log n) recursion stack.",
            f"At 1,000,000 records the dry run counts {reads} element reads. The measured median is {divide_1m}.",
        ],
        size=20,
        space=7,
    )

    slide = blank(prs, "Bhartendra Kumar Mandal", 9, total, "The clock and the recurrence")
    add_bullets(
        slide,
        0.55,
        1.3,
        12.2,
        5.4,
        [
            "Kadane keeps a running sum and drops it when it goes negative. One pass, Θ(n) in every case, Θ(1) extra words.",
            f"Its wall-clock slope from 1,000 to 1,000,000 records is 1.00. The median at one million records is {kadane_1m}.",
            f"Divide and conquer's read count grows like n log n. Its wall-clock slope from 10,000 to 1,000,000 is {divide_slope}, because each Python call allocates a result.",
            "The reads follow the Master Theorem. The clock says which algorithm to ship.",
            f"At one million records that choice is Kadane at {kadane_1m}, against divide and conquer at {divide_1m}.",
            "All three algorithms agree on every prefix where brute force was executed, and Kadane agrees with divide and conquer at the two larger sizes.",
        ],
        size=18,
        space=7,
    )

    slide = blank(prs, "Brian Lucero", 10, total, "Sort versus a size-10 heap")
    add_bullets(
        slide,
        0.55,
        1.25,
        12.2,
        5.5,
        [
            "Both algorithms use one total order: higher score, then earlier name. The tests require the same K names, including ties.",
            "The full sort is merge sort: Θ(n log n) in every case, with Θ(n) extra space. It does not become linear on a sorted run.",
            "The heap holds the K weakest-at-the-root survivors. Worst-case time is Θ(n log k). Best-case time is Θ(n + k log k). Extra space is Θ(k).",
            f"Market order, one million daily moves, k = 10:",
            f"Full sort  {site.fmt_ms(sort['median_ms'])}    and    {site.fmt_ops(sort['operations'])} comparisons.",
            f"Binary heap  {site.fmt_ms(heap['median_ms'])}    and    {site.fmt_ops(heap['operations'])} comparisons.",
        ],
        size=20,
        space=7,
    )

    slide = blank(prs, "Brian Lucero", 11, total, "Best case, worst case, and the clock")
    add_bullets(
        slide,
        0.45,
        1.2,
        6.5,
        5.5,
        [
            "Comparison counts at one million records:",
            f"Heap, top K first:  {heap_best['operations']:,}",
            f"Heap, market order:  {heap['operations']:,}",
            f"Heap, every insert:  {heap_worst['operations']:,}",
            f"Clocks: market {site.fmt_ms(heap['median_ms'])}, prepared best case {site.fmt_ms(heap_best['median_ms'])}, worst case {site.fmt_ms(heap_worst['median_ms'])}.",
            "The prepared arrays are permutations, so the best-case clock is slower than market order. The comparison count is the case split.",
            "Merge sort stays Θ(n log n) on a sorted run. The heap's comparison count, not the sort, is the case split.",
        ],
        size=16,
        space=5,
    )
    slide.shapes.add_picture(str(HEAP_FIG), Inches(7.05), Inches(1.4), Inches(5.8), Inches(3.55))
    add_text(slide, 7.05, 5.1, 5.8, 1.5, "Log scale. Worst case stays above best case at every size. Market order, not shown here, is faster in wall-clock time at the large sizes.", 14, False, MUTED)

    slide = blank(prs, "Bhartendra Kumar Mandal", 12, total, "Algorithmic Efficiency versus Computational Hardness")
    add_bullets(
        slide,
        0.55,
        1.3,
        12.2,
        5.4,
        [
            "Efficiency is a property of an algorithm. Hardness is a property of a problem.",
            "Brute force for this window is a correct polynomial. It is the wrong polynomial. Kadane puts maximum subarray in P.",
            f"The dashed line is an efficiency statement: this Python brute force projects to {brute_1m} at one million records. That trial was not run. Kadane finishes the same input in {kadane_1m}.",
            "Cardinality-constrained mean-variance portfolio selection is NP-hard. The chosen names interact through a covariance matrix.",
            "Top-K does not solve that problem. A heap of size K is optimal only when the score of a set is the sum of the scores of its members.",
            "A faster language multiplies the constant on the double loop. It does not put the portfolio problem in P.",
        ],
        size=18,
        space=7,
    )

    slide = blank(prs, "Aashish Joshi", 13, total, "The site, the paper, and the repository")
    add_bullets(
        slide,
        0.5,
        1.25,
        8.3,
        5.4,
        [
            "GitHub Pages serves docs/: the tables, the four figures, and the paper.",
            "Brute force at 1,000,000 records is labeled projected. The 100,000-record brute-force cell was measured once.",
            "The paper is 10 pages. It includes the efficiency-versus-hardness section and CLO reflections A through D.",
            "Slides and this script live in presentation/. Resume lines are in CONTRIBUTIONS.md.",
            SITE,
        ],
        size=18,
        space=8,
    )
    if QR.exists():
        slide.shapes.add_picture(str(QR), Inches(9.35), Inches(1.55), Inches(3.15), Inches(3.15))
        add_text(slide, 9.2, 4.8, 3.5, 0.8, "Scan for the project site", 14, False, MUTED, PP_ALIGN.CENTER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
