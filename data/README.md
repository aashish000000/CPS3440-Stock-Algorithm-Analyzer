# Data

The measurements use the Kaggle dataset [S&P 500 OHLC stock data](https://www.kaggle.com/datasets/jacksaleeby/s-and-p500-historical-data) by Jack Saleeby. The file name on that page is `SP500_Historical_Data.csv`.

1. Sign in to Kaggle.
2. Open the dataset and choose Download.
3. Unzip the archive.
4. Put the CSV in this folder as `data/SP500_Historical_Data.csv`.

The columns are `Ticker`, `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, and `Volume`. The copy used for the published timings has 2,703,531 rows, 472 tickers, and dates from 2000-01-03 through 2026-02-20.

`data/*.csv` is gitignored because the file is about 143 MB. This README stays in the repository.
