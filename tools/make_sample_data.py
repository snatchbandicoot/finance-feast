"""Generates the synthetic sample data behind the example charts.

Run: python3 tools/make_sample_data.py   (writes data/sample_daily.csv, data/sample_intraday.csv)

The data is SYNTHETIC. It is built from four regimes (an uptrend, a sideways range, a sharp
selloff, a recovery) so each study can be shown behaving well in some conditions and badly in
others. It is committed as CSV, so charts do not depend on any library's random generator.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)

# (name, bars, drift per bar, volatility per bar, mean reversion strength)
REGIMES = [
    ("uptrend", 100, 0.0016, 0.0085, 0.0),
    ("range", 100, 0.0, 0.0095, 0.10),
    ("selloff", 50, -0.0035, 0.0145, 0.0),
    ("recovery", 70, 0.0030, 0.0100, 0.0),
]


def make_daily():
    rows, price, anchor, regime_col = [], 100.0, 100.0, []
    for name, n, drift, vol, revert in REGIMES:
        if revert:
            anchor = price
        for _ in range(n):
            gap = rng.normal(0, 0.012) if rng.random() < 0.03 else rng.normal(0, 0.001)
            o = price * (1 + gap)
            pull = -revert * np.log(price / anchor) if revert else 0.0
            ret = drift + pull + rng.normal(0, vol)
            c = o * (1 + ret)
            hi = max(o, c) * (1 + abs(rng.normal(0, vol * 0.5)))
            lo = min(o, c) * (1 - abs(rng.normal(0, vol * 0.5)))
            v = 1_000_000 * np.exp(rng.normal(0, 0.25)) * (1 + 14 * abs(ret))
            rows.append((o, hi, lo, c, v))
            regime_col.append(name)
            price = c
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"]).round(4)
    df["volume"] = df["volume"].round(0).astype(int)
    df["regime"] = regime_col
    df.index.name = "bar"
    return df


def make_intraday(sessions=3, bars=78):
    rows, price, sess = [], 50.0, []
    x = np.linspace(0, 1, bars)
    u_shape = 1 + 2.2 * (np.exp(-x * 12) + np.exp(-(1 - x) * 12))  # busy open and close
    for s in range(sessions):
        price *= 1 + rng.normal(0, 0.004)
        drift = [0.00004, -0.00003, 0.00005][s % 3]
        for i in range(bars):
            o = price
            ret = drift + rng.normal(0, 0.0011)
            c = o * (1 + ret)
            hi = max(o, c) * (1 + abs(rng.normal(0, 0.0004)))
            lo = min(o, c) * (1 - abs(rng.normal(0, 0.0004)))
            v = 20_000 * u_shape[i] * np.exp(rng.normal(0, 0.3))
            rows.append((o, hi, lo, c, v))
            sess.append(s)
            price = c
    df = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"]).round(4)
    df["volume"] = df["volume"].round(0).astype(int)
    df["session"] = sess
    df.index.name = "bar"
    return df


if __name__ == "__main__":
    make_daily().to_csv("data/sample_daily.csv")
    make_intraday().to_csv("data/sample_intraday.csv")
    print("wrote data/sample_daily.csv and data/sample_intraday.csv")
