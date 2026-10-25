"""Checks the pandas snippets on each study page against independent loop implementations.

Run: python3 tools/verify_studies.py
The snippets below are copied verbatim into the study pages. If you change one, change both.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
close = pd.Series(100 + rng.normal(0, 1, 600).cumsum())


# ---- snippets as shown on the pages -------------------------------------------------
def sma(close, n):
    return close.rolling(n).mean()


def ema(close, n):
    return close.ewm(span=n, adjust=False).mean()


def rsi(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)


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
# ---- snippets as shown on the pages -------------------------------------------------
def macd(close, fast=12, slow=26, signal=9):
    line = close.ewm(span=fast, adjust=False).mean() - close.ewm(span=slow, adjust=False).mean()
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig


def bollinger(close, n=20, k=2):
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std(ddof=0)
    return mid, mid + k * sd, mid - k * sd


def atr(high, low, close, n=14):
    prev_close = close.shift()
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


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
