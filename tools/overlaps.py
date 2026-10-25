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
    "wma-sma-distance": lambda h, l, c, v: (c - ind.wma(c, 20), c - ind.sma(c, 20)),
    "wma-ema-distance": lambda h, l, c, v: (c - ind.wma(c, 20), c - ind.ema(c, 20)),
    "dema-ema-distance": lambda h, l, c, v: (c - ind.dema(c, 20), c - ind.ema(c, 20)),
    "tema-dema-distance": lambda h, l, c, v: (c - ind.tema(c, 20), c - ind.dema(c, 20)),
    "kama-ema-distance": lambda h, l, c, v: (c - ind.kama(c), c - ind.ema(c, 20)),
    "mcginley-ema-distance": lambda h, l, c, v: (c - ind.mcginley(c), c - ind.ema(c, 14)),
    "envelope-pctb": lambda h, l, c, v: (
        (lambda m, u, lo: (c - lo) / (u - lo))(*ind.envelope(c, 20, 2.5)),
        _bb_pctb(c),
    ),
    "vortex-di": lambda h, l, c, v: (
        (lambda a, b: a - b)(*ind.vortex(h, l, c, 14)),
        (lambda adx, p, m: (p - m) / 100)(*ind.adx(h, l, c, 14)),
    ),
    "supertrend-psar-distance": lambda h, l, c, v: (c - ind.supertrend(h, l, c, 10, 3), c - ind.psar(h, l)),
    "linreg-sma-distance": lambda h, l, c, v: (c - ind.linreg(c, 20)[0], c - ind.sma(c, 20)),
    "srsi-stoch": lambda h, l, c, v: (ind.stoch_rsi(c)[0], ind.stochastic(h, l, c)[0]),
    "srsi-rsi": lambda h, l, c, v: (ind.stoch_rsi(c)[0], ind.rsi(c, 14)),
    "smi-stoch": lambda h, l, c, v: (ind.smi(h, l, c)[0], ind.stochastic(h, l, c)[0]),
    "tsi-macd": lambda h, l, c, v: (ind.tsi(c)[0], ind.macd(c)[0]),
    "tsi-rsi": lambda h, l, c, v: (ind.tsi(c)[0], ind.rsi(c, 14)),
    "kst-macd": lambda h, l, c, v: (ind.kst(c)[0], ind.macd(c)[0]),
    "kst-tsi": lambda h, l, c, v: (ind.kst(c)[0], ind.tsi(c)[0]),
    "dpo-sma-distance": lambda h, l, c, v: (ind.dpo(c, 20), c - ind.sma(c, 20)),
    "coppock-roc": lambda h, l, c, v: (ind.coppock(c), ind.roc(c, 12)),
    "fisher-stoch": lambda h, l, c, v: (ind.fisher(h, l)[0], ind.stochastic(h, l, c)[0]),
    "rmi-rsi": lambda h, l, c, v: (ind.rmi(c, 14, 5), ind.rsi(c, 14)),
    "elder-ema-distance": lambda h, l, c, v: ((lambda b, e: (b + e) / 2)(*ind.elder_ray(h, l, c, 13)), c - ind.ema(c, 13)),
    "crsi-rsi14": lambda h, l, c, v: (ind.connors_rsi(c), ind.rsi(c, 14)),
    "crsi-rsi3": lambda h, l, c, v: (ind.connors_rsi(c), ind.rsi(c, 3)),
    "hv-atr": lambda h, l, c, v: (ind.historical_volatility(c), ind.atr(h, l, c)),
    "hv-sd-pct": lambda h, l, c, v: (ind.historical_volatility(c), ind.std_dev(c) / c),
    "sd-atr": lambda h, l, c, v: (ind.std_dev(c), ind.atr(h, l, c)),
    "cv-atr-level": lambda h, l, c, v: (ind.chaikin_volatility(h, l), ind.atr(h, l, c)),
    "chop-adx": lambda h, l, c, v: (ind.choppiness(h, l, c), ind.adx(h, l, c)[0]),
    "ulcer-hv": lambda h, l, c, v: (ind.ulcer(c), ind.historical_volatility(c)),
    "adl-obv": lambda h, l, c, v: (ind.accumulation_distribution(h, l, c, v).diff(20), ind.obv(c, v).diff(20)),
    "co-cmf": lambda h, l, c, v: (ind.chaikin_oscillator(h, l, c, v), ind.cmf(h, l, c, v, 20)),
    "mfi-rsi": lambda h, l, c, v: (ind.mfi(h, l, c, v), ind.rsi(c, 14)),
    "force-obv": lambda h, l, c, v: (ind.force_index(c, v), ind.obv(c, v).diff(13)),
    "force-roc": lambda h, l, c, v: (ind.force_index(c, v), ind.roc(c, 12)),
    "emv-roc": lambda h, l, c, v: (ind.ease_of_movement(h, l, v), ind.roc(c, 12)),
    "pvt-obv": lambda h, l, c, v: (ind.price_volume_trend(c, v).diff(20), ind.obv(c, v).diff(20)),
    "pvt-close": lambda h, l, c, v: (ind.price_volume_trend(c, v), c),
    "pvt-roc": lambda h, l, c, v: (ind.price_volume_trend(c, v).diff(20), ind.roc(c, 20)),
    "bmp-cmf": lambda h, l, c, v: (ind.balance_of_market_power(_sample_open(), h, l, c), ind.cmf(h, l, c, v, 20)),
    "klinger-co": lambda h, l, c, v: (ind.klinger(h, l, c, v)[0], ind.chaikin_oscillator(h, l, c, v)),
    "mom-roc": lambda h, l, c, v: (ind.momentum(c, 10), ind.roc(c, 10)),
    "di-ema-distance": lambda h, l, c, v: (ind.disparity_index(c, 14), c - ind.ema(c, 14)),
    "stc-stoch": lambda h, l, c, v: (ind.schaff_trend_cycle(c), ind.stochastic(h, l, c)[1]),
    "stc-macd": lambda h, l, c, v: (ind.schaff_trend_cycle(c), ind.macd(c)[0]),
    "dss-stoch": lambda h, l, c, v: (ind.double_smoothed_stochastic(h, l, c), ind.stochastic(h, l, c)[1]),
    "pzo-rsi": lambda h, l, c, v: (ind.price_zone_oscillator(c), ind.rsi(c, 14)),
    "woodie-6-14": lambda h, l, c, v: ind.woodies_cci(h, l, c),
    "tma-sma-distance": lambda h, l, c, v: (c - ind.triangular_ma(c, 20), c - ind.sma(c, 20)),
    "vidya-ema-distance": lambda h, l, c, v: (c - ind.variable_ma(c), c - ind.ema(c, 21)),
    "displaced-ema-distance": lambda h, l, c, v: (c - ind.displaced_ema(c), c - ind.ema(c, 20)),
    "starc-keltner-width": lambda h, l, c, v: (
        (lambda m, u, lo: (u - lo) / m)(*ind.starc_bands(h, l, c)),
        (lambda m, u, lo: (u - lo) / m)(*ind.keltner(h, l, c)),
    ),
    "cv-atr-roc": lambda h, l, c, v: (ind.chaikin_volatility(h, l), 100 * (ind.atr(h, l, c) / ind.atr(h, l, c).shift(10) - 1)),
    "rvi-rsi": lambda h, l, c, v: (ind.relative_volatility(c), ind.rsi(c, 14)),
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


def _id_rmi_rsi(h, l, c, v):
    return (ind.rmi(c, 14, 1) - ind.rsi(c, 14)).abs().max()


def _id_stddev_bollinger(h, l, c, v):
    _, up, lo = ind.bollinger(c, 20, 2)
    return ((up - lo) - 4 * ind.std_dev(c, 20)).abs().max()


def _id_avwap_vwap(h, l, c, v):
    return (ind.anchored_vwap(h, l, c, v, 0) - ind.vwap(h, l, c, v, pd.Series(0, index=c.index))).abs().max()


def _id_adl_cmf(h, l, c, v):
    return (ind.accumulation_distribution(h, l, c, v).diff(20) / v.rolling(20).sum() - ind.cmf(h, l, c, v, 20)).abs().max()


def _id_co_macd(h, l, c, v):
    return (ind.chaikin_oscillator(h, l, c, v) - ind.macd(ind.accumulation_distribution(h, l, c, v), 3, 10)[0]).abs().max()


def _id_vo_ppo(h, l, c, v):
    return (ind.volume_oscillator(v, 5, 10) - ind.ppo(v, 5, 10, 9)[0]).abs().max()


def _id_woodie_cci(h, l, c, v):
    return (ind.woodies_cci(h, l, c, 14, 6)[0] - ind.cci(h, l, c, 14)).abs().max()


def _id_ribbon_ema(h, l, c, v):
    ribbon, _ = ind.ema_ribbon(c)
    return (ribbon[20] - ind.ema(c, 20)).abs().max()


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
    "ribbon-ema": _id_ribbon_ema,
    "woodie-cci-14": _id_woodie_cci,
    "volume-oscillator-ppo": _id_vo_ppo,
    "adl-cmf": _id_adl_cmf,
    "chaikin-osc-macd-of-adl": _id_co_macd,
    "avwap-vwap": _id_avwap_vwap,
    "stddev-bollinger": _id_stddev_bollinger,
    "rmi-rsi-momentum-1": _id_rmi_rsi,
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
    ("weighted-moving-average", "simple-moving-average"): dict(strength="near", identity=None, corr="wma-sma-distance"),
    ("weighted-moving-average", "exponential-moving-average"): dict(strength="near", identity=None, corr="wma-ema-distance"),
    ("double-exponential-moving-average", "exponential-moving-average"): dict(strength="partial", identity=None, corr="dema-ema-distance"),
    ("triple-exponential-moving-average", "double-exponential-moving-average"): dict(strength="partial", identity=None, corr="tema-dema-distance"),
    ("kaufman-adaptive-moving-average", "exponential-moving-average"): dict(strength="partial", identity=None, corr="kama-ema-distance"),
    ("mcginley-dynamic", "exponential-moving-average"): dict(strength="near", identity=None, corr="mcginley-ema-distance"),
    ("moving-average-envelope", "bollinger-bands"): dict(strength="partial", identity=None, corr="envelope-pctb"),
    ("vortex-indicator", "average-directional-index"): dict(strength="partial", identity=None, corr="vortex-di"),
    ("supertrend", "parabolic-sar"): dict(strength="partial", identity=None, corr="supertrend-psar-distance"),
    ("stochastic-rsi", "stochastic-oscillator"): dict(strength="partial", identity=None, corr="srsi-stoch"),
    ("stochastic-momentum-index", "stochastic-oscillator"): dict(strength="partial", identity=None, corr="smi-stoch"),
    ("true-strength-index", "macd"): dict(strength="near", identity=None, corr="tsi-macd"),
    ("know-sure-thing", "macd"): dict(strength="near", identity=None, corr="kst-macd"),
    ("know-sure-thing", "true-strength-index"): dict(strength="partial", identity=None, corr="kst-tsi"),
    ("coppock-curve", "rate-of-change"): dict(strength="partial", identity=None, corr="coppock-roc"),
    ("fisher-transform", "stochastic-oscillator"): dict(strength="partial", identity=None, corr="fisher-stoch"),
    ("relative-momentum-index", "relative-strength-index"): dict(strength="partial", identity="rmi-rsi-momentum-1", corr="rmi-rsi"),
    ("elder-ray", "exponential-moving-average"): dict(strength="near", identity=None, corr="elder-ema-distance"),
    ("connors-rsi", "relative-strength-index"): dict(strength="partial", identity=None, corr="crsi-rsi3"),
    ("standard-deviation", "bollinger-bands"): dict(strength="identical", identity="stddev-bollinger", corr=None),
    ("historical-volatility", "average-true-range"): dict(strength="partial", identity=None, corr="hv-atr"),
    ("historical-volatility", "standard-deviation"): dict(strength="partial", identity=None, corr="hv-sd-pct"),
    ("chaikin-volatility", "average-true-range"): dict(strength="partial", identity=None, corr="cv-atr-roc"),
    ("relative-volatility-index", "relative-strength-index"): dict(strength="partial", identity=None, corr="rvi-rsi"),
    ("anchored-vwap", "volume-weighted-average-price"): dict(strength="identical", identity="avwap-vwap", corr=None),
    ("ulcer-index", "historical-volatility"): dict(strength="partial", identity=None, corr="ulcer-hv"),
    ("accumulation-distribution", "on-balance-volume"): dict(strength="partial", identity=None, corr="adl-obv"),
    ("accumulation-distribution", "chaikin-money-flow"): dict(strength="identical", identity="adl-cmf", corr=None),
    ("chaikin-oscillator", "macd"): dict(strength="identical", identity="chaikin-osc-macd-of-adl", corr=None),
    ("chaikin-oscillator", "chaikin-money-flow"): dict(strength="partial", identity=None, corr="co-cmf"),
    ("money-flow-index", "relative-strength-index"): dict(strength="partial", identity=None, corr="mfi-rsi"),
    ("force-index", "on-balance-volume"): dict(strength="partial", identity=None, corr="force-obv"),
    ("force-index", "rate-of-change"): dict(strength="partial", identity=None, corr="force-roc"),
    ("ease-of-movement", "rate-of-change"): dict(strength="partial", identity=None, corr="emv-roc"),
    ("price-volume-trend", "on-balance-volume"): dict(strength="partial", identity=None, corr="pvt-obv"),
    ("price-volume-trend", "rate-of-change"): dict(strength="near", identity=None, corr="pvt-roc"),
    ("balance-of-market-power", "chaikin-money-flow"): dict(strength="partial", identity=None, corr="bmp-cmf"),
    ("klinger-oscillator", "chaikin-oscillator"): dict(strength="partial", identity=None, corr="klinger-co"),
    ("volume-oscillator", "percentage-price-oscillator"): dict(strength="identical", identity="volume-oscillator-ppo", corr=None),
    ("momentum", "rate-of-change"): dict(strength="near", identity=None, corr="mom-roc"),
    ("disparity-index", "exponential-moving-average"): dict(strength="near", identity=None, corr="di-ema-distance"),
    ("schaff-trend-cycle", "stochastic-oscillator"): dict(strength="partial", identity=None, corr="stc-stoch"),
    ("double-smoothed-stochastic", "stochastic-oscillator"): dict(strength="partial", identity=None, corr="dss-stoch"),
    ("price-zone-oscillator", "relative-strength-index"): dict(strength="partial", identity=None, corr="pzo-rsi"),
    ("woodies-cci", "commodity-channel-index"): dict(strength="identical", identity="woodie-cci-14", corr=None),
    ("triangular-moving-average", "simple-moving-average"): dict(strength="near", identity=None, corr="tma-sma-distance"),
    ("variable-moving-average", "exponential-moving-average"): dict(strength="partial", identity=None, corr="vidya-ema-distance"),
    ("displaced-ema", "exponential-moving-average"): dict(strength="near", identity=None, corr="displaced-ema-distance"),
    ("starc-bands", "keltner-channels"): dict(strength="partial", identity=None, corr="starc-keltner-width"),
    ("moving-average-ribbon", "exponential-moving-average"): dict(strength="identical", identity="ribbon-ema", corr=None),
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
    ("weighted-moving-average", 2, "wma-sma-distance"),
    ("weighted-moving-average", 2, "wma-ema-distance"),
    ("double-exponential-moving-average", 2, "dema-ema-distance"),
    ("triple-exponential-moving-average", 2, "tema-dema-distance"),
    ("kaufman-adaptive-moving-average", 2, "kama-ema-distance"),
    ("mcginley-dynamic", 2, "mcginley-ema-distance"),
    ("moving-average-envelope", 2, "envelope-pctb"),
    ("vortex-indicator", 2, "vortex-di"),
    ("supertrend", 2, "supertrend-psar-distance"),
    ("linear-regression", 2, "linreg-sma-distance"),
    ("stochastic-rsi", 2, "srsi-stoch"),
    ("stochastic-rsi", 2, "srsi-rsi"),
    ("stochastic-momentum-index", 2, "smi-stoch"),
    ("true-strength-index", 2, "tsi-macd"),
    ("true-strength-index", 2, "tsi-rsi"),
    ("know-sure-thing", 2, "kst-macd"),
    ("know-sure-thing", 2, "kst-tsi"),
    ("detrended-price-oscillator", 2, "dpo-sma-distance"),
    ("coppock-curve", 2, "coppock-roc"),
    ("fisher-transform", 2, "fisher-stoch"),
    ("relative-momentum-index", 2, "rmi-rsi"),
    ("elder-ray", 2, "elder-ema-distance"),
    ("connors-rsi", 2, "crsi-rsi3"),
    ("connors-rsi", 2, "crsi-rsi14"),
    ("historical-volatility", 2, "hv-atr"),
    ("historical-volatility", 2, "hv-sd-pct"),
    ("standard-deviation", 2, "sd-atr"),
    ("chaikin-volatility", 2, "cv-atr-roc"),
    ("chaikin-volatility", 2, "cv-atr-level"),
    ("relative-volatility-index", 2, "rvi-rsi"),
    ("choppiness-index", 2, "chop-adx"),
    ("ulcer-index", 2, "ulcer-hv"),
    ("accumulation-distribution", 2, "adl-obv"),
    ("chaikin-oscillator", 2, "co-cmf"),
    ("money-flow-index", 2, "mfi-rsi"),
    ("force-index", 2, "force-obv"),
    ("force-index", 2, "force-roc"),
    ("ease-of-movement", 2, "emv-roc"),
    ("price-volume-trend", 2, "pvt-obv"),
    ("price-volume-trend", 2, "pvt-roc"),
    ("price-volume-trend", 3, "pvt-close"),
    ("balance-of-market-power", 2, "bmp-cmf"),
    ("klinger-oscillator", 2, "klinger-co"),
    ("momentum", 3, "mom-roc"),
    ("disparity-index", 3, "di-ema-distance"),
    ("woodies-cci", 2, "woodie-6-14"),
    ("schaff-trend-cycle", 2, "stc-stoch"),
    ("schaff-trend-cycle", 2, "stc-macd"),
    ("double-smoothed-stochastic", 2, "dss-stoch"),
    ("price-zone-oscillator", 2, "pzo-rsi"),
    ("triangular-moving-average", 3, "tma-sma-distance"),
    ("variable-moving-average", 2, "vidya-ema-distance"),
    ("displaced-ema", 3, "displaced-ema-distance"),
    ("starc-bands", 2, "starc-keltner-width"),
    ("guides/overlaps", 2, "adx-aroon"),
    ("guides/overlaps", 3, "tma-sma-distance"),
    ("guides/overlaps", 3, "displaced-ema-distance"),
    ("guides/overlaps", 2, "vidya-ema-distance"),
    ("guides/overlaps", 2, "starc-keltner-width"),
    ("guides/overlaps", 3, "mom-roc"),
    ("guides/overlaps", 3, "di-ema-distance"),
    ("guides/overlaps", 2, "stc-stoch"),
    ("guides/overlaps", 2, "stc-macd"),
    ("guides/overlaps", 2, "dss-stoch"),
    ("guides/overlaps", 2, "pzo-rsi"),
    ("guides/overlaps", 2, "mcginley-ema-distance"),
    ("guides/overlaps", 2, "wma-sma-distance"),
    ("guides/overlaps", 2, "wma-ema-distance"),
    ("guides/overlaps", 2, "dema-ema-distance"),
    ("guides/overlaps", 2, "kama-ema-distance"),
    ("guides/overlaps", 2, "linreg-sma-distance"),
    ("guides/overlaps", 2, "envelope-pctb"),
    ("guides/overlaps", 2, "tsi-macd"),
    ("guides/overlaps", 2, "kst-macd"),
    ("guides/overlaps", 2, "kst-tsi"),
    ("guides/overlaps", 2, "coppock-roc"),
    ("guides/overlaps", 2, "srsi-stoch"),
    ("guides/overlaps", 2, "srsi-rsi"),
    ("guides/overlaps", 2, "smi-stoch"),
    ("guides/overlaps", 2, "fisher-stoch"),
    ("guides/overlaps", 2, "rmi-rsi"),
    ("guides/overlaps", 2, "crsi-rsi3"),
    ("guides/overlaps", 2, "mfi-rsi"),
    ("guides/overlaps", 2, "rvi-rsi"),
    ("guides/overlaps", 2, "hv-atr"),
    ("guides/overlaps", 2, "sd-atr"),
    ("guides/overlaps", 2, "cv-atr-roc"),
    ("guides/overlaps", 2, "ulcer-hv"),
    ("guides/overlaps", 2, "chop-adx"),
    ("guides/overlaps", 2, "adl-obv"),
    ("guides/overlaps", 2, "co-cmf"),
    ("guides/overlaps", 2, "pvt-roc"),
    ("guides/overlaps", 2, "emv-roc"),
    ("guides/overlaps", 2, "force-roc"),
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


def _sample_open():
    return pd.read_csv(pathlib_path(), index_col=0)["open"]


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
