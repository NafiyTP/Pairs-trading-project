## Company Comparison & Pairs Trading Tool

This tool compares two companies from the same industry to help identify potential pairs trading opportunities.

Users input two company names (or tickers), and the tool analyzes their historical price data from **2021 to 2024**. It computes the relative price spread and produces a graph highlighting periods where one asset appears overvalued or undervalued, indicating potential **long / short** or **no-trade** signals.

For meaningful results, the selected companies must operate in the **same sector**. A typical example is comparing **Visa (V)** and **Mastercard (MA)**, which share similar business models and market dynamics.

This project is intended for **educational and research purposes only**
---

## Requirements

The following Python modules are required:

- `yfinance`
- `numpy`
- `pandas`
- `matplotlib`

You can install them with:

```bash
pip install yfinance numpy pandas matplotlib
