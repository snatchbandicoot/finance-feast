"""Checks the pandas snippets on each study page against independent loop implementations.

Run: python3 tools/verify_studies.py
The functions under test live in tools/indicators.py, and their code is shown on the study pages.
"""
import numpy as np
import pandas as pd

from indicators import atr, bollinger, ema, macd, obv, rsi, sma, stochastic, vwap

rng = np.random.default_rng(7)
close = pd.Series(100 + rng.normal(0, 1, 600).cumsum())


# ---- independent references: plain loops, no pandas smoothing ------------------------
def sma_ref(p, n):
    out = [np.nan] * len(p)
    for i in range(n - 1, len(p)):
        out[i] = sum(p[i - n + 1 : i + 1]) / n
    return np.array(out)


def ema_ref(p, n):
    a = 2 / (n + 1)
    out = [p[0]]
    for x in p[1:]:
        out.append(a * x + (1 - a) * out[-1])
    return np.array(out)


def rsi_ref_same_seed(p, n):
    """Same recursion as the snippet (average starts at the first change)."""
    out = [np.nan]
    ag = al = 0.0
    for i in range(1, len(p)):
        ch = p[i] - p[i - 1]
        g, l = max(ch, 0.0), max(-ch, 0.0)
        if i == 1:
            ag, al = g, l
        else:
            ag = ag * (1 - 1 / n) + g / n
            al = al * (1 - 1 / n) + l / n
        out.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    return np.array(out)


def rsi_ref_wilder(p, n):
    """Textbook Wilder: first averages are simple means of the first n changes."""
    out = [np.nan] * len(p)
    ch = [p[i] - p[i - 1] for i in range(1, len(p))]
    ag = sum(max(c, 0) for c in ch[:n]) / n
    al = sum(max(-c, 0) for c in ch[:n]) / n
    out[n] = 100 - 100 / (1 + ag / al)
    for i in range(n, len(ch)):
        ag = (ag * (n - 1) + max(ch[i], 0)) / n
        al = (al * (n - 1) + max(-ch[i], 0)) / n
        out[i + 1] = 100 - 100 / (1 + ag / al)
    return np.array(out)


def check(name, a, b, tol):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    err = np.max(np.abs(a[ok] - b[ok]))
    assert ok.sum() > 100 and err < tol, f"{name}: max error {err}"
    print(f"ok  {name}: max error {err:.2e} over {ok.sum()} bars")


p = close.to_numpy()
check("SMA(20) vs loop", sma(close, 20), sma_ref(p, 20), 1e-9)
check("EMA(20) vs loop", ema(close, 20), ema_ref(p, 20), 1e-9)
check("RSI(14) vs loop, same seed", rsi(close, 14), rsi_ref_same_seed(p, 14), 1e-9)
# The textbook seed differs at the start and the gap decays; compare after warm-up.
check("RSI(14) vs Wilder-seeded, bars 200+", rsi(close, 14)[200:], rsi_ref_wilder(p, 14)[200:], 1e-3)

# ---- worked examples quoted on the pages --------------------------------------------
ex = pd.Series([10, 11, 12, 11, 13], dtype=float)
assert sma(ex, 3).iloc[-1] == 12.0
assert np.allclose(ema(ex, 3).to_numpy(), [10, 10.5, 11.25, 11.125, 12.0625])
avg_gain, avg_loss = 0.6, 0.4
assert abs((100 - 100 / (1 + avg_gain / avg_loss)) - 60.0) < 1e-12
print("ok  worked examples")


# =====================================================================================
# MACD, Bollinger Bands, ATR
# =====================================================================================
# ---- independent references ---------------------------------------------------------
def bollinger_ref(p, n, k):
    mid, up, lo = [np.nan] * len(p), [np.nan] * len(p), [np.nan] * len(p)
    for i in range(n - 1, len(p)):
        w = p[i - n + 1 : i + 1]
        m = sum(w) / n
        sd = (sum((x - m) ** 2 for x in w) / n) ** 0.5
        mid[i], up[i], lo[i] = m, m + k * sd, m - k * sd
    return np.array(mid), np.array(up), np.array(lo)


def atr_ref_same_seed(h, l, c, n):
    out = []
    a = None
    for i in range(len(c)):
        tr = h[i] - l[i] if i == 0 else max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        a = tr if a is None else a * (1 - 1 / n) + tr / n
        out.append(a)
    return np.array(out)


def atr_ref_wilder(h, l, c, n):
    """Textbook: first ATR is the plain mean of the first n true ranges, then Wilder smoothing."""
    trs = [h[0] - l[0]] + [
        max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))
    ]
    out = [np.nan] * len(c)
    a = sum(trs[:n]) / n
    out[n - 1] = a
    for i in range(n, len(c)):
        a = (a * (n - 1) + trs[i]) / n
        out[i] = a
    return np.array(out)


# synthetic OHLC around the same close series
hi = close + np.abs(rng.normal(0, 0.8, len(close)))
lo = close - np.abs(rng.normal(0, 0.8, len(close)))
H, L = hi.to_numpy(), lo.to_numpy()

# MACD: compare against EMA loops, built independently of pandas
e12, e26 = ema_ref(p, 12), ema_ref(p, 26)
line_ref = e12 - e26
sig_ref = ema_ref(line_ref, 9)
line, sig, hist = macd(close)
check("MACD line vs loop", line, line_ref, 1e-9)
check("MACD signal vs loop", sig, sig_ref, 1e-9)
check("MACD histogram vs loop", hist, line_ref - sig_ref, 1e-9)
# zero-line cross of MACD is exactly the cross of the 12 and 26 EMAs
assert np.array_equal(np.sign(line.to_numpy()), np.sign(e12 - e26))
print("ok  MACD zero cross == EMA12/EMA26 cross")

# Bollinger
mid, up, lw = bollinger(close, 20, 2)
mid_r, up_r, lw_r = bollinger_ref(p, 20, 2)
check("Bollinger middle vs loop", mid, mid_r, 1e-9)
check("Bollinger upper vs loop", up, up_r, 1e-9)
check("Bollinger lower vs loop", lw, lw_r, 1e-9)
# sample (ddof=1) standard deviation gives different, wider bands: the page warns about this
_, up_s, _ = (lambda m, s: (m, m + 2 * s, m - 2 * s))(close.rolling(20).mean(), close.rolling(20).std())
assert (up_s.dropna() > up.dropna()).all()
print("ok  Bollinger ddof=1 bands are strictly wider than ddof=0")

# ATR
check("ATR(14) vs loop, same seed", atr(hi, lo, close, 14), atr_ref_same_seed(H, L, p, 14), 1e-9)
check("ATR(14) vs Wilder-seeded, bars 200+", atr(hi, lo, close, 14)[200:], atr_ref_wilder(H, L, p, 14)[200:], 1e-3)

# ---- worked examples quoted on the pages --------------------------------------------
# MACD: values given directly
assert abs((105.2 - 104.5) - 0.7) < 1e-12 and abs((0.7 - 0.5) - 0.2) < 1e-12
# Bollinger: last three closes 12, 11, 13 (N = 3, k = 2)
w = [12.0, 11.0, 13.0]
m = sum(w) / 3
sd = (sum((x - m) ** 2 for x in w) / 3) ** 0.5
assert m == 12.0 and abs(sd - 0.816497) < 1e-6
assert abs((m + 2 * sd) - 13.632993) < 1e-6 and abs((m - 2 * sd) - 10.367007) < 1e-6
pct_b = (12.5 - (m - 2 * sd)) / ((m + 2 * sd) - (m - 2 * sd))
bw = ((m + 2 * sd) - (m - 2 * sd)) / m
assert abs(pct_b - 0.6531) < 1e-3 and abs(bw - 0.2722) < 1e-3
# ATR: true range on a gap down (high 12, low 10, previous close 13)
assert max(12 - 10, abs(12 - 13), abs(10 - 13)) == 3
# ATR position sizing: risk 100, ATR 2, stop at 2 ATR -> 100 / (2 * 2) = 25 shares
assert 100 / (2 * 2) == 25
print("ok  worked examples (MACD, Bollinger, ATR)")


# =====================================================================================
# Stochastic Oscillator, VWAP, On-Balance Volume
# =====================================================================================
# ---- independent references ---------------------------------------------------------
def stochastic_ref(h, l, c, n, sk, sd):
    N = len(c)
    raw = [np.nan] * N
    for i in range(n - 1, N):
        ll, hh = min(l[i - n + 1 : i + 1]), max(h[i - n + 1 : i + 1])
        raw[i] = 100 * (c[i] - ll) / (hh - ll)
    k = [np.nan] * N
    for i in range(n - 1 + sk - 1, N):
        k[i] = sum(raw[i - sk + 1 : i + 1]) / sk
    d = [np.nan] * N
    for i in range(n - 1 + sk - 1 + sd - 1, N):
        d[i] = sum(k[i - sd + 1 : i + 1]) / sd
    return np.array(raw), np.array(k), np.array(d)


def vwap_ref(h, l, c, v, session):
    out, pv, vv, cur = [], 0.0, 0.0, None
    for i in range(len(c)):
        if session[i] != cur:
            cur, pv, vv = session[i], 0.0, 0.0
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vv += v[i]
        out.append(pv / vv)
    return np.array(out)


def obv_ref(c, v):
    out, total = [0.0], 0.0
    for i in range(1, len(c)):
        if c[i] > c[i - 1]:
            total += v[i]
        elif c[i] < c[i - 1]:
            total -= v[i]
        out.append(total)
    return np.array(out)


vol = pd.Series(rng.integers(100, 1000, len(close)).astype(float))
V = vol.to_numpy()
session = pd.Series(np.arange(len(close)) // 78)  # 78 five-minute bars per 6.5 hour session
S = session.to_numpy()

raw_k, k, d = stochastic(hi, lo, close)
rr, kr, dr = stochastic_ref(H, L, p, 14, 3, 3)
check("Stochastic raw %K vs loop", raw_k, rr, 1e-9)
check("Stochastic slow %K vs loop", k, kr, 1e-9)
check("Stochastic %D vs loop", d, dr, 1e-9)
assert raw_k.dropna().between(0, 100).all()
print("ok  Stochastic stays within 0 to 100")

check("VWAP vs loop (resets each session)", vwap(hi, lo, close, vol, session), vwap_ref(H, L, p, V, S), 1e-9)
check("OBV vs loop", obv(close, vol), obv_ref(p, V), 1e-9)

# ---- worked examples quoted on the pages --------------------------------------------
# Stochastic: highest high 20, lowest low 10, close 16 -> 60
assert abs(100 * (16 - 10) / (20 - 10) - 60.0) < 1e-12
# Stochastic smoothing example: raw %K of 60, 70, 80 -> slow %K 70
assert abs((60 + 70 + 80) / 3 - 70.0) < 1e-12
# VWAP: typical price 10 on volume 100, then 11 on volume 300 -> 10.75 (the simple average would be 10.5)
assert abs((10 * 100 + 11 * 300) / (100 + 300) - 10.75) < 1e-12 and (10 + 11) / 2 == 10.5
# OBV
ex_c = pd.Series([10, 11, 10.5, 10.5, 12], dtype=float)
ex_v = pd.Series([100, 200, 150, 120, 300], dtype=float)
assert obv(ex_c, ex_v).tolist() == [0.0, 200.0, 50.0, 50.0, 350.0]
print("ok  worked examples (Stochastic, VWAP, OBV)")


# =====================================================================================
# Page snippets must be textually identical to the functions that were verified above
# =====================================================================================
import inspect
import pathlib
import re

import indicators

PAGES = {
    "simple-moving-average": "sma",
    "exponential-moving-average": "ema",
    "relative-strength-index": "rsi",
    "macd": "macd",
    "bollinger-bands": "bollinger",
    "average-true-range": "atr",
    "stochastic-oscillator": "stochastic",
    "volume-weighted-average-price": "vwap",
    "on-balance-volume": "obv",
}
studies = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "studies"
for slug, fn in PAGES.items():
    text = (studies / f"{slug}.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", text, re.S)
    shown = next((b.strip() for b in blocks if b.lstrip().startswith(f"def {fn}(")), None)
    assert shown is not None, f"{slug}: no python block defining {fn}()"
    assert shown == inspect.getsource(getattr(indicators, fn)).strip(), f"{slug}: snippet differs from indicators.{fn}"
print(f"ok  page snippets match indicators.py ({len(PAGES)} pages)")


# every chart a page references must exist, in both light and dark
charts = pathlib.Path(__file__).resolve().parent.parent / "public" / "charts"
for slug in PAGES:
    text = (studies / f"{slug}.md").read_text()
    assert f"charts/{slug}-light.svg" in text and f"charts/{slug}-dark.svg" in text, f"{slug}: chart not embedded"
    for mode in ("light", "dark"):
        assert (charts / f"{slug}-{mode}.svg").is_file(), f"missing chart {slug}-{mode}.svg"
print(f"ok  every page embeds its light and dark chart, and both files exist ({len(PAGES)} pages)")
