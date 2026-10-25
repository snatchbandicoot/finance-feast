"""How studies overlap, measured on the site's sample data.

Each pair a study page declares in its `overlaps` frontmatter must appear here, and tools/verify_studies.py
checks the declared strength and correlation against these definitions. There are two kinds of evidence:

  identity  an exact mathematical relationship that holds on any data (checked to 1e-9)
  corr      a correlation on the synthetic sample, over bars 60 onward so recursive averages have settled

Strengths: identical (an exact relationship), near (correlation of at least 0.95), partial (0.6 up to 0.95,
or a shared exact event). The correlations are measured on synthetic data, so they show direction, not
the exact overlap you would see in a real market. Exact identities do not depend on the data.
"""
import numpy as np
import pandas as pd

import indicators as ind

WARM = 60


def corr(a, b):
    both = pd.concat([a, b], axis=1).iloc[WARM:].dropna()
    return both.iloc[:, 0].corr(both.iloc[:, 1])


# ---- correlation measures: name -> (series a, series b) from the sample's high, low, close, volume ----------
def _bb_pctb(c):
    _, up, lo = ind.bollinger(c, 20, 2)
    return (c - lo) / (up - lo)


MEASURES = {
    "ao-macd": lambda h, l, c, v: (ind.awesome(h, l, 5, 34), ind.macd(c)[0]),
    "ao-sma-diff": lambda h, l, c, v: (ind.awesome(h, l, 5, 34), ind.sma(c, 5) - ind.sma(c, 34)),
    "cci-pctb": lambda h, l, c, v: (ind.cci(h, l, c, 20), _bb_pctb(c)),
    "cci-rsi": lambda h, l, c, v: (ind.cci(h, l, c, 20), ind.rsi(c, 14)),
    "uo-rsi": lambda h, l, c, v: (ind.ultimate(h, l, c), ind.rsi(c, 14)),
    "cmo-rsi": lambda h, l, c, v: (ind.cmo(c, 14), ind.rsi(c, 14)),
    "stoch-rsi": lambda h, l, c, v: (ind.stochastic(h, l, c)[1], ind.rsi(c, 14)),
    "roc-macd": lambda h, l, c, v: (ind.roc(c, 12), ind.macd(c)[0]),
    "roc-rsi": lambda h, l, c, v: (ind.roc(c, 12), ind.rsi(c, 14)),
    "trix-macd": lambda h, l, c, v: (ind.trix(c, 15), ind.macd(c)[0]),
    "ppo-macd": lambda h, l, c, v: (ind.ppo(c)[0], ind.macd(c)[0]),
    "ema-sma-distance": lambda h, l, c, v: (c - ind.ema(c, 20), c - ind.sma(c, 20)),
    "keltner-bb-width": lambda h, l, c, v: (
        (lambda m, u, lo: (u - lo) / m)(*ind.keltner(h, l, c, 20, 10, 2)),
        (lambda m, u, lo: (u - lo) / m)(*ind.bollinger(c, 20, 2)),
    ),
    "cmf-obv": lambda h, l, c, v: (ind.cmf(h, l, c, v, 20), ind.obv(c, v).diff(20)),
    "adx-aroon": lambda h, l, c, v: (ind.adx(h, l, c)[0], ind.aroon(h, l, 25)[2].abs()),
}


# ---- exact identities: name -> largest absolute error (or True/False for an event identity) -------------------
def _id_williams_stochastic(h, l, c, v):
    return (ind.williams_r(h, l, c, 14) - (ind.stochastic(h, l, c, 14)[0] - 100)).abs().max()


def _id_cmo_cutler(h, l, c, v):
    change = c.diff()
    up = change.clip(lower=0).rolling(14).sum()
    down = (-change).clip(lower=0).rolling(14).sum()
    cutler = 100 * up / (up + down)
    return (ind.cmo(c, 14) - (2 * cutler - 100)).abs().max()


def _id_ppo_macd(h, l, c, v):
    slow = c.ewm(span=26, adjust=False).mean()
    return (ind.ppo(c)[0] * slow / 100 - ind.macd(c)[0]).abs().max()


def _id_aroon_donchian(h, l, c, v):
    up, down, _ = ind.aroon(h, l, 25)
    valid = up.notna()
    new_high = h >= h.rolling(25).max().shift(1)
    new_low = l <= l.rolling(25).min().shift(1)
    return 0.0 if (((up[valid] == 100) == new_high[valid]).all() and ((down[valid] == 100) == new_low[valid]).all()) else 1.0


def _id_ichimoku_donchian(h, l, c, v):
    tenkan, kijun, senkou_a, senkou_b, _ = ind.ichimoku(h, l, c)
    errs = [(tenkan - ind.donchian(h, l, 9)[1]).abs().max(), (kijun - ind.donchian(h, l, 26)[1]).abs().max()]
    # Senkou B is the 52-bar Donchian middle line, labelled 26 bars ahead
    errs.append((senkou_b - ind.donchian(h, l, 52)[1].set_axis(senkou_b.index)).abs().max())
    return max(errs)


IDENTITIES = {
    "ichimoku-donchian": _id_ichimoku_donchian,
    "williams-stochastic": _id_williams_stochastic,
    "cmo-cutler": _id_cmo_cutler,
    "ppo-macd": _id_ppo_macd,
    "aroon-donchian": _id_aroon_donchian,
}

# ---- the pairs: (declaring study, other study) -> strength, identity check, correlation measure ----------------
PAIRS = {
    ("williams-percent-r", "stochastic-oscillator"): dict(strength="identical", identity="williams-stochastic", corr=None),
    ("chande-momentum-oscillator", "relative-strength-index"): dict(strength="identical", identity="cmo-cutler", corr="cmo-rsi"),
    ("percentage-price-oscillator", "macd"): dict(strength="identical", identity="ppo-macd", corr=None),
    ("awesome-oscillator", "macd"): dict(strength="near", identity=None, corr="ao-macd"),
    ("commodity-channel-index", "bollinger-bands"): dict(strength="near", identity=None, corr="cci-pctb"),
    ("exponential-moving-average", "simple-moving-average"): dict(strength="near", identity=None, corr="ema-sma-distance"),
    ("commodity-channel-index", "relative-strength-index"): dict(strength="partial", identity=None, corr="cci-rsi"),
    ("ultimate-oscillator", "relative-strength-index"): dict(strength="partial", identity=None, corr="uo-rsi"),
    ("stochastic-oscillator", "relative-strength-index"): dict(strength="partial", identity=None, corr="stoch-rsi"),
    ("rate-of-change", "macd"): dict(strength="partial", identity=None, corr="roc-macd"),
    ("trix", "macd"): dict(strength="partial", identity=None, corr="trix-macd"),
    ("keltner-channels", "bollinger-bands"): dict(strength="partial", identity=None, corr="keltner-bb-width"),
    ("chaikin-money-flow", "on-balance-volume"): dict(strength="partial", identity=None, corr="cmf-obv"),
    ("aroon", "donchian-channels"): dict(strength="partial", identity="aroon-donchian", corr=None),
    ("ichimoku-cloud", "donchian-channels"): dict(strength="partial", identity="ichimoku-donchian", corr=None),
}

# Correlations quoted in page text must match these measures. (page, decimals, measure name)
# A page under guides/ is the overlap guide.
QUOTES = [
    ("awesome-oscillator", 2, "ao-macd"),
    ("awesome-oscillator", 3, "ao-sma-diff"),
    ("commodity-channel-index", 2, "cci-pctb"),
    ("commodity-channel-index", 2, "cci-rsi"),
    ("bollinger-bands", 2, "cci-pctb"),
    ("ultimate-oscillator", 2, "uo-rsi"),
    ("chande-momentum-oscillator", 2, "cmo-rsi"),
    ("percentage-price-oscillator", 3, "ppo-macd"),
    ("rate-of-change", 2, "roc-macd"),
    ("rate-of-change", 2, "roc-rsi"),
    ("keltner-channels", 2, "keltner-bb-width"),
    ("chaikin-money-flow", 2, "cmf-obv"),
    ("guides/overlaps", 2, "adx-aroon"),
    ("guides/overlaps", 2, "ao-macd"),
    ("guides/overlaps", 2, "trix-macd"),
    ("guides/overlaps", 2, "roc-macd"),
    ("guides/overlaps", 2, "cci-pctb"),
    ("guides/overlaps", 2, "cci-rsi"),
    ("guides/overlaps", 2, "uo-rsi"),
    ("guides/overlaps", 2, "cmo-rsi"),
    ("guides/overlaps", 2, "stoch-rsi"),
    ("guides/overlaps", 2, "keltner-bb-width"),
    ("guides/overlaps", 2, "cmf-obv"),
    ("guides/overlaps", 2, "ema-sma-distance"),
]


def sample():
    d = pd.read_csv(pathlib_path(), index_col=0)
    return d["high"], d["low"], d["close"], d["volume"]


def pathlib_path():
    import pathlib
    return pathlib.Path(__file__).resolve().parent.parent / "data" / "sample_daily.csv"


def measure(name):
    h, l, c, v = sample()
    a, b = MEASURES[name](h, l, c, v)
    return corr(a, b)


def identity_error(name):
    h, l, c, v = sample()
    return float(IDENTITIES[name](h, l, c, v))


if __name__ == "__main__":
    for key in MEASURES:
        print(f"{key:20s} {measure(key):.4f}")
    for key in IDENTITIES:
        print(f"{key:20s} identity error {identity_error(key):.2e}")
