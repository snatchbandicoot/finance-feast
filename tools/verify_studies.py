"""Checks the pandas snippets on each study page against independent loop implementations.

Run: python3 tools/verify_studies.py
The functions under test live in tools/indicators.py, and their code is shown on the study pages.
"""
import numpy as np
import pandas as pd

from indicators import (aroon, adx, atr, bollinger, cci, cmf, donchian, ema, ichimoku, keltner, macd, obv, psar,
                        roc, rsi, sma, stochastic, vwap, williams_r)

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
# ROC, Williams %R, CCI, ADX, Parabolic SAR
# =====================================================================================
def roc_ref(p, n):
    out = [np.nan] * len(p)
    for i in range(n, len(p)):
        out[i] = 100 * (p[i] - p[i - n]) / p[i - n]
    return np.array(out)


def williams_ref(h, l, c, n):
    out = [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        hh, ll = max(h[i - n + 1 : i + 1]), min(l[i - n + 1 : i + 1])
        out[i] = -100 * (hh - c[i]) / (hh - ll)
    return np.array(out)


def cci_ref(h, l, c, n):
    tp = [(h[i] + l[i] + c[i]) / 3 for i in range(len(c))]
    out = [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        w = tp[i - n + 1 : i + 1]
        m = sum(w) / n
        md = sum(abs(x - m) for x in w) / n
        out[i] = (tp[i] - m) / (0.015 * md)
    return np.array(out)


def _true_range_and_dm(h, l, c):
    tr, pdm, mdm = [h[0] - l[0]], [0.0], [0.0]
    for i in range(1, len(c)):
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
        up, down = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm.append(up if (up > down and up > 0) else 0.0)
        mdm.append(down if (down > up and down > 0) else 0.0)
    return tr, pdm, mdm


def adx_ref_same_seed(h, l, c, n):
    tr, pdm, mdm = _true_range_and_dm(h, l, c)
    a = 1 / n
    s_tr, s_p, s_m, s_dx = tr[0], pdm[0], mdm[0], None
    adx_out, pdi_out, mdi_out = [], [], []
    for i in range(len(c)):
        if i:
            s_tr, s_p, s_m = s_tr * (1 - a) + tr[i] * a, s_p * (1 - a) + pdm[i] * a, s_m * (1 - a) + mdm[i] * a
        pdi, mdi = 100 * s_p / s_tr, 100 * s_m / s_tr
        dx = 100 * abs(pdi - mdi) / (pdi + mdi) if (pdi + mdi) else np.nan
        if not np.isnan(dx):
            s_dx = dx if s_dx is None else s_dx * (1 - a) + dx * a
        adx_out.append(np.nan if s_dx is None else s_dx)
        pdi_out.append(pdi)
        mdi_out.append(mdi)
    return np.array(adx_out), np.array(pdi_out), np.array(mdi_out)


def adx_ref_wilder(h, l, c, n):
    """Textbook Wilder: first values are sums over the first n changes, then S = S - S/n + x."""
    tr, pdm, mdm = _true_range_and_dm(h, l, c)
    N = len(c)
    s_tr, s_p, s_m = sum(tr[1 : n + 1]), sum(pdm[1 : n + 1]), sum(mdm[1 : n + 1])
    dxs = {}
    pdi_out, mdi_out = [np.nan] * N, [np.nan] * N
    for i in range(n, N):
        if i > n:
            s_tr, s_p, s_m = s_tr - s_tr / n + tr[i], s_p - s_p / n + pdm[i], s_m - s_m / n + mdm[i]
        pdi, mdi = 100 * s_p / s_tr, 100 * s_m / s_tr
        pdi_out[i], mdi_out[i] = pdi, mdi
        dxs[i] = 100 * abs(pdi - mdi) / (pdi + mdi)
    out = [np.nan] * N
    first = 2 * n - 1
    a = sum(dxs[i] for i in range(n, first + 1)) / n
    out[first] = a
    for i in range(first + 1, N):
        a = (a * (n - 1) + dxs[i]) / n
        out[i] = a
    return np.array(out), np.array(pdi_out), np.array(mdi_out)


def psar_ref(h, l, step=0.02, step_max=0.2):
    """Same rules, written sign-symmetrically (t = +1 uptrend, -1 downtrend) instead of two mirrored branches."""
    n = len(h)
    t = 1 if h[1] >= h[0] else -1

    def best(i):  # the extreme this trend is chasing
        return h[i] if t > 0 else l[i]

    def worst(i):  # the side the SAR must not cross
        return l[i] if t > 0 else h[i]

    sar, ep, af = [l[0] if t > 0 else h[0]], best(0), step
    for i in range(1, n):
        s = sar[-1] + af * (ep - sar[-1])
        s = t * min(t * s, t * worst(i - 1), t * worst(i - 2 if i > 1 else i - 1))
        if t * (worst(i) - s) < 0:  # price pushed through the SAR: reverse
            t = -t
            s, ep, af = ep, best(i), step  # best() now reads the new trend
        elif t * (best(i) - ep) > 0:
            ep, af = best(i), min(af + step, step_max)
        sar.append(s)
    return np.array(sar)


roc_s = roc(close, 12)
check("ROC(12) vs loop", roc_s, roc_ref(p, 12), 1e-9)
wr = williams_r(hi, lo, close, 14)
check("Williams %R(14) vs loop", wr, williams_ref(H, L, p, 14), 1e-9)
# Williams %R is the raw stochastic %K shifted down by 100, exactly
raw_k14 = stochastic(hi, lo, close, 14)[0]
check("Williams %R == raw stochastic %K - 100", wr, raw_k14 - 100, 1e-9)
cci_s = cci(hi, lo, close, 20)
check("CCI(20) vs loop", cci_s, cci_ref(H, L, p, 20), 1e-8)

adx_s, pdi_s, mdi_s = adx(hi, lo, close, 14)
a_r, p_r, m_r = adx_ref_same_seed(H, L, p, 14)
check("ADX(14) vs loop, same seed", adx_s, a_r, 1e-9)
check("+DI(14) vs loop, same seed", pdi_s, p_r, 1e-9)
check("-DI(14) vs loop, same seed", mdi_s, m_r, 1e-9)
aw, pw, mw = adx_ref_wilder(H, L, p, 14)
check("ADX(14) vs Wilder-seeded, bars 250+", adx_s[250:], aw[250:], 1e-3)
check("+DI(14) vs Wilder-seeded, bars 250+", pdi_s[250:], pw[250:], 1e-3)
assert adx_s.dropna().between(0, 100).all() and pdi_s.between(0, 100).all() and mdi_s.between(0, 100).all()
print("ok  ADX, +DI and -DI stay within 0 to 100")

sar_s = psar(hi, lo)
check("Parabolic SAR vs sign-symmetric re-implementation", sar_s, psar_ref(H, L), 1e-9)
# invariants: on non-reversal bars the SAR sits on the far side of the bar from the trend
above = sar_s.to_numpy() > H
below = sar_s.to_numpy() < L
inside = ~(above | below)
assert inside.sum() <= 0.02 * len(sar_s), f"{inside.sum()} bars have SAR inside the bar's range"
print(f"ok  Parabolic SAR lies outside the bar on {100 * (1 - inside.mean()):.1f}% of bars (inside only on rare reversal bars)")

# ---- worked examples quoted on the pages --------------------------------------------
# ROC: 11.5 against 10.0 twelve bars earlier is +15%
assert abs(100 * (11.5 / 10.0 - 1) - 15.0) < 1e-12
# Williams %R: highest high 20, lowest low 10, close 16 -> -40 (the stochastic page's example gives %K = 60)
assert abs(-100 * (20 - 16) / (20 - 10) - (-40.0)) < 1e-12 and abs(100 * (16 - 10) / (20 - 10) - 100 - (-40.0)) < 1e-12
# CCI: five typical prices 10, 11, 12, 13, 14 with n = 5: mean 12, mean deviation 1.2, CCI = (14 - 12) / (0.015 * 1.2)
tp = np.array([10.0, 11, 12, 13, 14])
md = np.abs(tp - tp.mean()).mean()
assert abs(md - 1.2) < 1e-12 and abs((tp[-1] - tp.mean()) / (0.015 * md) - 111.1111111) < 1e-6
# ADX: +DI 30 and -DI 10 -> DX = 100 * 20 / 40 = 50
assert abs(100 * abs(30 - 10) / (30 + 10) - 50.0) < 1e-12
# True range / directional movement of one bar: high 12 vs 11, low 10 vs 9.5 -> +DM 1, -DM 0 (up move 1 beats down move -0.5)
up, down = 12 - 11, 9.5 - 10
assert (up if up > down and up > 0 else 0) == 1 and (down if down > up and down > 0 else 0) == 0
# Parabolic SAR by hand on six bars (see the page): SAR = 8, 8, 8, 8.24, 8.6208, 14 (reversal on the last bar)
ex_h = pd.Series([10.0, 11, 12, 13, 14, 13])
ex_l = pd.Series([8.0, 9, 10, 11, 12, 7])
expected = [8.0, 8.0, 8.0, 8.24, 8.6208, 14.0]
assert np.allclose(psar(ex_h, ex_l).to_numpy(), expected, atol=1e-9), psar(ex_h, ex_l).tolist()
print("ok  worked examples (ROC, Williams %R, CCI, ADX, Parabolic SAR)")


# =====================================================================================
# Aroon, Donchian, Keltner, Chaikin Money Flow, Ichimoku
# =====================================================================================
def aroon_ref(h, l, n):
    up, dn = [np.nan] * len(h), [np.nan] * len(h)
    for i in range(n, len(h)):
        wh, wl = h[i - n : i + 1], l[i - n : i + 1]
        # bars since the most recent high (or low) inside the n + 1 bar window
        since_high = min(k for k in range(n + 1) if wh[n - k] == max(wh))
        since_low = min(k for k in range(n + 1) if wl[n - k] == min(wl))
        up[i], dn[i] = 100 * (n - since_high) / n, 100 * (n - since_low) / n
    return np.array(up), np.array(dn)


def donchian_ref(h, l, n):
    up, mid, lo = [np.nan] * len(h), [np.nan] * len(h), [np.nan] * len(h)
    for i in range(n - 1, len(h)):
        up[i], lo[i] = max(h[i - n + 1 : i + 1]), min(l[i - n + 1 : i + 1])
        mid[i] = (up[i] + lo[i]) / 2
    return np.array(up), np.array(mid), np.array(lo)


def cmf_ref(h, l, c, v, n):
    out = [np.nan] * len(c)
    mfv = []
    for i in range(len(c)):
        rng = h[i] - l[i]
        mult = 0.0 if rng == 0 else ((c[i] - l[i]) - (h[i] - c[i])) / rng
        mfv.append(mult * v[i])
    for i in range(n - 1, len(c)):
        out[i] = sum(mfv[i - n + 1 : i + 1]) / sum(v[i - n + 1 : i + 1])
    return np.array(out)


def ichimoku_ref(h, l, conversion, base, span_b):
    def mid(n):
        out = [np.nan] * len(h)
        for i in range(n - 1, len(h)):
            out[i] = (max(h[i - n + 1 : i + 1]) + min(l[i - n + 1 : i + 1])) / 2
        return np.array(out)

    return mid(conversion), mid(base), mid(span_b)


up_a, dn_a, osc_a = aroon(hi, lo, 25)
ar_u, ar_d = aroon_ref(H, L, 25)
check("Aroon Up(25) vs loop", up_a, ar_u, 1e-9)
check("Aroon Down(25) vs loop", dn_a, ar_d, 1e-9)
check("Aroon Oscillator vs loop", osc_a, ar_u - ar_d, 1e-9)
assert up_a.dropna().between(0, 100).all() and dn_a.dropna().between(0, 100).all()
print("ok  Aroon stays within 0 to 100")
# Aroon Up is 100 exactly when the bar's high ties or exceeds the highest high of the previous 25 bars (a new 25-bar high);
# Aroon Down is 100 exactly when its low ties or undercuts the previous 25 lows.
prior_high = hi.rolling(25).max().shift(1)
prior_low = lo.rolling(25).min().shift(1)
valid = up_a.notna()
assert ((up_a[valid] == 100) == (hi[valid] >= prior_high[valid])).all()
assert ((dn_a[valid] == 100) == (lo[valid] <= prior_low[valid])).all()
print("ok  Aroon = 100 exactly when a new 25-bar high (or low) is set, the same event as a Donchian breakout")

du, dm, dl = donchian(hi, lo, 20)
dur, dmr, dlr = donchian_ref(H, L, 20)
check("Donchian upper vs loop", du, dur, 1e-9)
check("Donchian middle vs loop", dm, dmr, 1e-9)
check("Donchian lower vs loop", dl, dlr, 1e-9)
valid = du.notna()  # comparisons with NaN are False, so skip the warm-up bars explicitly
assert (hi[valid] <= du[valid]).all() and (lo[valid] >= dl[valid]).all()
print("ok  Donchian channel always contains the current bar's high and low")

km, ku, kl = keltner(hi, lo, close, 20, 10, 2)
k_mid = ema_ref(p, 20)
k_atr = atr_ref_same_seed(H, L, p, 10)
check("Keltner middle vs EMA loop", km, k_mid, 1e-9)
check("Keltner upper vs EMA + 2 x ATR loops", ku, k_mid + 2 * k_atr, 1e-9)
check("Keltner lower vs EMA - 2 x ATR loops", kl, k_mid - 2 * k_atr, 1e-9)

cm = cmf(hi, lo, close, vol, 20)
check("CMF(20) vs loop", cm, cmf_ref(H, L, p, V, 20), 1e-9)
assert cm.dropna().between(-1, 1).all()
print("ok  CMF stays within -1 to +1")
# a bar with no range counts as zero instead of dividing by zero
flat = cmf(pd.Series([10.0, 10.0, 12.0]), pd.Series([10.0, 10.0, 10.0]), pd.Series([10.0, 10.0, 11.0]), pd.Series([5.0, 5.0, 10.0]), 3)
assert np.isfinite(flat.iloc[-1]) and abs(flat.iloc[-1] - 0.0) < 1e-12
print("ok  CMF handles a bar with no range")

tk, kj, sa, sb, ch = ichimoku(hi, lo, close)
tr_, kr_, sbr_ = ichimoku_ref(H, L, 9, 26, 52)
check("Ichimoku Tenkan(9) vs loop", tk, tr_, 1e-9)
check("Ichimoku Kijun(26) vs loop", kj, kr_, 1e-9)
sa_ref = (tr_ + kr_) / 2
# Senkou A and B are labelled 26 bars ahead, the Chikou span 26 bars behind
check("Ichimoku Senkou A (drawn 26 bars ahead)", sa.to_numpy(), sa_ref, 1e-9)
check("Ichimoku Senkou B (drawn 26 bars ahead)", sb.to_numpy(), sbr_, 1e-9)
assert sa.index[0] == 26 and sa.index[-1] == len(close) - 1 + 26 and ch.index[0] == -26 and ch.index[-1] == len(close) - 1 - 26
assert np.array_equal(ch.to_numpy(), close.to_numpy())
print("ok  Ichimoku shifts: cloud 26 bars ahead, lagging span 26 bars behind")

# ---- worked examples quoted on the pages --------------------------------------------
# Aroon: n = 4, highs 10, 12, 11, 11.5, 11.2 -> highest high 3 bars ago -> Up 25; lows 9, 10, 9.5, 9.8, 9.4 -> lowest low 4 bars ago -> Down 0
au, ad, ao = aroon(pd.Series([10.0, 12, 11, 11.5, 11.2]), pd.Series([9.0, 10, 9.5, 9.8, 9.4]), 4)
assert au.iloc[-1] == 25.0 and ad.iloc[-1] == 0.0 and ao.iloc[-1] == 25.0
# Donchian: highest high 14, lowest low 8 -> middle 11; a close of 14.5 breaks the prior upper channel of 14
assert (14 + 8) / 2 == 11 and 14.5 > 14
# Keltner: middle 100, ATR 2, multiplier 2 -> bands 104 and 96
assert 100 + 2 * 2 == 104 and 100 - 2 * 2 == 96
# CMF: bar 1 high 12 low 10 close 11.5 volume 100 -> multiplier 0.5; bar 2 close 10.5 volume 300 -> -0.5; CMF = (50 - 150) / 400 = -0.25
c2 = cmf(pd.Series([12.0, 12.0]), pd.Series([10.0, 10.0]), pd.Series([11.5, 10.5]), pd.Series([100.0, 300.0]), 2)
assert abs(c2.iloc[-1] - (-0.25)) < 1e-12
# Ichimoku on six bars with short settings (2, 3, 4, shift 2): at bar 3 Tenkan 11, Kijun 11, Senkou A 11, Senkou B 10.5, drawn at bar 5
ex_h, ex_l, ex_c = pd.Series([10.0, 12, 11, 13, 12, 14]), pd.Series([8.0, 9, 9, 10, 10, 11]), pd.Series([9.0, 11, 10, 12, 11, 13])
t_, k_, a_, b_, c_ = ichimoku(ex_h, ex_l, ex_c, 2, 3, 4, 2)
assert t_.iloc[3] == 11 and k_.iloc[3] == 11 and a_.loc[5] == 11 and b_.loc[5] == 10.5
print("ok  worked examples (Aroon, Donchian, Keltner, CMF, Ichimoku)")


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
    "average-directional-index": "adx",
    "parabolic-sar": "psar",
    "commodity-channel-index": "cci",
    "williams-percent-r": "williams_r",
    "rate-of-change": "roc",
    "aroon": "aroon",
    "donchian-channels": "donchian",
    "keltner-channels": "keltner",
    "chaikin-money-flow": "cmf",
    "ichimoku-cloud": "ichimoku",
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


# the site's CSS color tokens must match tools/palette.py (charts and site share one palette)
import palette

css = (pathlib.Path(__file__).resolve().parent.parent / "src" / "layouts" / "Base.astro").read_text()
light_block = re.search(r":root \{(.*?)\}", css, re.S).group(1)
dark_block = re.search(r"prefers-color-scheme: dark\) \{\s*:root \{(.*?)\}", css, re.S).group(1)
for name, block, colors in (("light", light_block, palette.LIGHT), ("dark", dark_block, palette.DARK)):
    for key, hex_value in colors.items():
        found = re.search(rf"--{key.replace('_', '-')}:\s*(#[0-9a-fA-F]{{6}})", block)
        assert found and found.group(1).lower() == hex_value.lower(), f"{name} {key}: Base.astro has {found and found.group(1)}, palette.py has {hex_value}"
print("ok  site color tokens match tools/palette.py (light and dark)")
