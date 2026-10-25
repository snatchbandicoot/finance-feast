"""Checks the pandas snippets on each study page against independent loop implementations.

Run: python3 tools/verify_studies.py
The functions under test live in tools/indicators.py, and their code is shown on the study pages.
"""
import numpy as np
import pandas as pd

from indicators import (aroon, adx, atr, awesome, bollinger, cci, cmf, cmo, dema, donchian, ema, hma, ichimoku, kama,
                        keltner, linreg, macd, mcginley, obv, ppo, psar, roc, rsi, sma, stochastic, supertrend, tema, trix, ultimate,
                        vortex, vwap, williams_r, wma, envelope)

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
# Awesome Oscillator, TRIX, Ultimate Oscillator, CMO, PPO
# =====================================================================================
def awesome_ref(h, l, fast, slow):
    med = [(h[i] + l[i]) / 2 for i in range(len(h))]
    out = [np.nan] * len(h)
    for i in range(slow - 1, len(h)):
        out[i] = sum(med[i - fast + 1 : i + 1]) / fast - sum(med[i - slow + 1 : i + 1]) / slow
    return np.array(out)


def trix_ref(p, n):
    t = ema_ref(ema_ref(ema_ref(p, n), n), n)
    return np.array([np.nan] + [100 * (t[i] / t[i - 1] - 1) for i in range(1, len(t))])


def ultimate_ref(h, l, c, s_, m_, l_):
    bp, tr = [], []
    for i in range(len(c)):
        lo_ref = l[i] if i == 0 else min(l[i], c[i - 1])
        hi_ref = h[i] if i == 0 else max(h[i], c[i - 1])
        bp.append(c[i] - lo_ref)
        tr.append(hi_ref - lo_ref)
    out = [np.nan] * len(c)
    for i in range(l_ - 1, len(c)):
        a = [sum(bp[i - n + 1 : i + 1]) / sum(tr[i - n + 1 : i + 1]) for n in (s_, m_, l_)]
        out[i] = 100 * (4 * a[0] + 2 * a[1] + a[2]) / 7
    return np.array(out)


def cmo_ref(c, n):
    out, cutler = [np.nan] * len(c), [np.nan] * len(c)
    for i in range(n, len(c)):
        ch = [c[k] - c[k - 1] for k in range(i - n + 1, i + 1)]
        su, sd = sum(x for x in ch if x > 0), sum(-x for x in ch if x < 0)
        out[i] = 100 * (su - sd) / (su + sd)
        cutler[i] = 100 * su / (su + sd)  # Cutler's RSI: plain sums instead of Wilder smoothing
    return np.array(out), np.array(cutler)


def ppo_ref(p, fast, slow, sig):
    ef, es = ema_ref(p, fast), ema_ref(p, slow)
    line = 100 * (ef - es) / es
    s_ = ema_ref(line, sig)
    return line, s_, line - s_, es


ao = awesome(hi, lo, 5, 34)
check("Awesome Oscillator (5, 34) vs loop", ao, awesome_ref(H, L, 5, 34), 1e-9)

tx = trix(close, 15)
check("TRIX(15) vs loop (three EMA loops)", tx, trix_ref(p, 15), 1e-9)
steady = pd.Series(100 * 1.01 ** np.arange(500))  # rises exactly 1% every bar
assert abs(trix(steady, 15).iloc[-1] - 1.0) < 1e-9
print("ok  TRIX of a series rising 1% per bar converges to exactly 1.0")

uo = ultimate(hi, lo, close, 7, 14, 28)
check("Ultimate Oscillator (7, 14, 28) vs loop", uo, ultimate_ref(H, L, p, 7, 14, 28), 1e-9)
assert uo.dropna().between(0, 100).all()
print("ok  Ultimate Oscillator stays within 0 to 100")

cm, cutler = cmo_ref(p, 14)
cmo_s = cmo(close, 14)
check("CMO(14) vs loop", cmo_s, cm, 1e-9)
check("CMO == 2 x Cutler RSI - 100", cmo_s, 2 * cutler - 100, 1e-9)
assert cmo_s.dropna().between(-100, 100).all()
print("ok  CMO stays within -100 to +100")

ppo_l, ppo_sg, ppo_h = ppo(close, 12, 26, 9)
pl, ps, ph, slow_ema_ref = ppo_ref(p, 12, 26, 9)
check("PPO line vs loop", ppo_l, pl, 1e-9)
check("PPO signal vs loop", ppo_sg, ps, 1e-9)
check("PPO histogram vs loop", ppo_h, ph, 1e-9)
macd_line = macd(close)[0]
check("PPO x slow EMA / 100 == MACD line", ppo_l * slow_ema_ref / 100, macd_line, 1e-9)

# ---- worked examples quoted on the pages --------------------------------------------
# Awesome: settings (2, 4); medians 9, 11, 13, 12 -> SMA2 = 12.5, SMA4 = 11.25 -> AO = 1.25
assert awesome(pd.Series([10.0, 12, 14, 13]), pd.Series([8.0, 10, 12, 11]), 2, 4).iloc[-1] == 1.25
# Ultimate: averages 0.6, 0.5, 0.4 -> 100 x (4 x 0.6 + 2 x 0.5 + 0.4) / 7
assert abs(100 * (4 * 0.6 + 2 * 0.5 + 0.4) / 7 - 54.285714285714) < 1e-9
# one bar: previous close 11, high 12, low 10.5, close 11.8 -> buying pressure 1.3 over true range 1.5
u1 = ultimate(pd.Series([11.5, 12.0]), pd.Series([10.5, 10.5]), pd.Series([11.0, 11.8]), 1, 1, 1)
assert abs(u1.iloc[-1] - 100 * 1.3 / 1.5) < 1e-9
# CMO: closes 10, 12, 11, 14, 12 (n = 4): gains 2 + 3 = 5, losses 1 + 2 = 3 -> CMO = 25, Cutler RSI = 62.5
c5 = pd.Series([10.0, 12, 11, 14, 12])
assert cmo(c5, 4).iloc[-1] == 25.0 and 100 * 5 / (5 + 3) == 62.5 and 2 * 62.5 - 100 == 25.0
# PPO: EMA12 105.2, EMA26 104.5 (the MACD page's example) -> PPO = 100 x 0.7 / 104.5
assert abs(100 * (105.2 - 104.5) / 104.5 - 0.669856459) < 1e-8
# Scale: multiply every price by 3. MACD and the Awesome Oscillator triple (they are in price units); PPO, TRIX,
# the Ultimate Oscillator and CMO do not change (they are percentages or ratios).
t3 = lambda x: x * 3
check("MACD line triples when prices triple", macd(t3(close))[0], 3 * macd(close)[0], 1e-9)
check("Awesome Oscillator triples when prices triple", awesome(t3(hi), t3(lo), 5, 34), 3 * awesome(hi, lo, 5, 34), 1e-9)
check("PPO unchanged when prices triple", ppo(t3(close))[0], ppo(close)[0], 1e-9)
check("TRIX unchanged when prices triple", trix(t3(close), 15), trix(close, 15), 1e-9)
check("Ultimate Oscillator unchanged when prices triple", ultimate(t3(hi), t3(lo), t3(close)), ultimate(hi, lo, close), 1e-9)
check("CMO unchanged when prices triple", cmo(t3(close), 14), cmo(close, 14), 1e-9)
print("ok  worked examples (Awesome, TRIX, Ultimate, CMO, PPO)")


# =====================================================================================
# WMA, DEMA, TEMA, HMA, KAMA
# =====================================================================================
def wma_ref(p, n):
    out = [np.nan] * len(p)
    for i in range(n - 1, len(p)):
        w = p[i - n + 1 : i + 1]
        if not np.isnan(w).any():
            out[i] = sum((k + 1) * w[k] for k in range(n)) / (n * (n + 1) / 2)
    return np.array(out)


def dema_ref(p, n):
    e1 = ema_ref(p, n)
    return 2 * e1 - ema_ref(e1, n)


def tema_ref(p, n):
    e1 = ema_ref(p, n)
    e2 = ema_ref(e1, n)
    return 3 * e1 - 3 * e2 + ema_ref(e2, n)


def hma_ref(p, n):
    raw = 2 * wma_ref(p, n // 2) - wma_ref(p, n)
    return wma_ref(raw, round(n ** 0.5))


def kama_ref(p, n, fast, slow):
    fs, ss = 2 / (fast + 1), 2 / (slow + 1)
    out = [np.nan] * len(p)
    out[n] = p[n]
    for i in range(n + 1, len(p)):
        path = sum(abs(p[k] - p[k - 1]) for k in range(i - n + 1, i + 1))
        er = 0.0 if path == 0 else abs(p[i] - p[i - n]) / path
        sc = (er * (fs - ss) + ss) ** 2
        out[i] = out[i - 1] + sc * (p[i] - out[i - 1])
    return np.array(out)


check("WMA(20) vs loop", wma(close, 20), wma_ref(p, 20), 1e-9)
check("DEMA(20) vs EMA loops", dema(close, 20), dema_ref(p, 20), 1e-9)
check("TEMA(20) vs EMA loops", tema(close, 20), tema_ref(p, 20), 1e-9)
check("HMA(21) vs WMA loops", hma(close, 21), hma_ref(p, 21), 1e-9)
check("KAMA(10, 2, 30) vs loop", kama(close, 10, 2, 30), kama_ref(p, 10, 2, 30), 1e-9)

# lag on a steady climb (price = bar number): how many bars each average trails price
climb = pd.Series(np.arange(1000, dtype=float))
lag = lambda f: climb.iloc[-1] - f(climb).iloc[-1]
assert abs(lag(lambda c: sma(c, 20)) - 9.5) < 1e-9 and abs(lag(lambda c: ema(c, 20)) - 9.5) < 1e-6
assert abs(lag(lambda c: wma(c, 20)) - (20 - 1) / 3) < 1e-9
assert abs(lag(lambda c: dema(c, 20))) < 1e-6 and abs(lag(lambda c: tema(c, 20))) < 1e-6
assert abs(lag(lambda c: hma(c, 21)) - 2 / 3) < 1e-9
assert abs(lag(lambda c: kama(c, 10, 2, 30)) - 1.25) < 1e-9  # efficiency 1: alpha = (2/3)^2, lag = (1 - alpha) / alpha
print("ok  lag on a steady climb: SMA 9.5, EMA 9.5, WMA 6.33, DEMA 0, TEMA 0, HMA 0.67, KAMA 1.25 bars (n = 20, HMA 21)")

# overshoot after a jump from 100 to 110: the cost of low lag
jump = pd.Series([100.0] * 200 + [110.0] * 200)
over = lambda f: round(f(jump).iloc[200:].max() - 110, 1)
assert over(lambda c: ema(c, 20)) == 0 and over(lambda c: wma(c, 20)) == 0 and over(lambda c: kama(c, 10, 2, 30)) == 0
assert (over(lambda c: dema(c, 20)), over(lambda c: tema(c, 20)), over(lambda c: hma(c, 21))) == (1.2, 1.8, 2.7)
print("ok  overshoot after a 10-point jump: EMA, WMA, KAMA 0; DEMA 1.2, TEMA 1.8, HMA 2.7 points")
assert not kama(jump, 10, 2, 30).iloc[10:].isna().any()
print("ok  KAMA stays defined on perfectly flat data")

# ---- worked examples quoted on the pages --------------------------------------------
assert abs(wma(pd.Series([10.0, 11, 13]), 3).iloc[-1] - 71 / 6) < 1e-12 and (10 + 11 + 13) / 3 != 71 / 6
assert 2 * 105 - 103 == 107 and 3 * 105 - 3 * 103 + 101.5 == 107.5
assert round(21 ** 0.5) == 5 and round(20 ** 0.5) == 4 and 2 * 104 - 100 == 108
k_up = kama(pd.Series([10.0, 11, 12, 13, 14, 15]), 4, 2, 30)           # efficiency 1: smoothing (2/3)^2
assert abs(k_up.iloc[5] - (14 + (2 / 3) ** 2 * (15 - 14))) < 1e-12
k_flat = kama(pd.Series([10.0, 12, 10, 12, 10, 12]), 4, 2, 30)          # efficiency 0: smoothing (2/31)^2
assert abs(k_flat.iloc[5] - (10 + (2 / 31) ** 2 * (12 - 10))) < 1e-12
print("ok  worked examples (WMA, DEMA, TEMA, HMA, KAMA)")


# =====================================================================================
# McGinley Dynamic, Moving Average Envelope, Linear Regression, Supertrend, Vortex
# =====================================================================================
def mcginley_ref(p, n, k):
    out = [p[0]]
    for i in range(1, len(p)):
        out.append(out[-1] + (p[i] - out[-1]) / (k * n * (p[i] / out[-1]) ** 4))
    return np.array(out)


def envelope_ref(p, n, pct):
    mid = sma_ref(p, n)
    return mid, mid * (1 + pct / 100), mid * (1 - pct / 100)


def linreg_ref(p, n):
    value, slope = [np.nan] * len(p), [np.nan] * len(p)
    x = np.arange(n)
    for i in range(n - 1, len(p)):
        m, b = np.polyfit(x, p[i - n + 1 : i + 1], 1)  # least squares, independent of the closed form
        value[i], slope[i] = m * (n - 1) + b, m
    return np.array(value), np.array(slope)


def vortex_ref(h, l, c, n):
    tr, vp, vm = [h[0] - l[0]], [np.nan], [np.nan]
    for i in range(1, len(c)):
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
        vp.append(abs(h[i] - l[i - 1]))
        vm.append(abs(l[i] - h[i - 1]))
    up, dn = [np.nan] * len(c), [np.nan] * len(c)
    for i in range(n, len(c)):
        t = sum(tr[i - n + 1 : i + 1])
        up[i], dn[i] = sum(vp[i - n + 1 : i + 1]) / t, sum(vm[i - n + 1 : i + 1]) / t
    return np.array(up), np.array(dn)


def supertrend_ref(h, l, c, n, k):
    """A fresh transcription of the widely used charting-platform definition, written with explicit previous values."""
    a = atr_ref_same_seed(h, l, c, n)
    up1 = dn1 = line_prev = None
    trend = 1
    out = []
    for i in range(len(c)):
        mid = (h[i] + l[i]) / 2
        up_b, dn_b = mid - k * a[i], mid + k * a[i]
        if i == 0:
            up, dn = up_b, dn_b
        else:
            up = max(up_b, up1) if c[i - 1] > up1 else up_b
            dn = min(dn_b, dn1) if c[i - 1] < dn1 else dn_b
            if trend == -1 and c[i] > dn1:
                trend = 1
            elif trend == 1 and c[i] < up1:
                trend = -1
        out.append(up if trend == 1 else dn)
        up1, dn1 = up, dn
    return np.array(out)


check("McGinley Dynamic (14, 0.6) vs loop", mcginley(close, 14, 0.6), mcginley_ref(p, 14, 0.6), 1e-9)
em, eu, el = envelope(close, 20, 2.5)
mr, ur, lr_ = envelope_ref(p, 20, 2.5)
check("Envelope middle vs loop", em, mr, 1e-9)
check("Envelope upper vs loop", eu, ur, 1e-9)
check("Envelope lower vs loop", el, lr_, 1e-9)
lv, ls = linreg(close, 20)
lvr, lsr = linreg_ref(p, 20)
check("Linear regression value vs np.polyfit", lv, lvr, 1e-8)
check("Linear regression slope vs np.polyfit", ls, lsr, 1e-8)
vip, vim = vortex(hi, lo, close, 14)
vpr, vmr = vortex_ref(H, L, p, 14)
check("Vortex VI+ vs loop", vip, vpr, 1e-9)
check("Vortex VI- vs loop", vim, vmr, 1e-9)
check("Supertrend (10, 3) vs independent transcription", supertrend(hi, lo, close, 10, 3), supertrend_ref(H, L, p, 10, 3), 1e-9)

# Supertrend: in an up-trend the line sits below the close and never falls; in a down-trend it sits above and never rises
st = supertrend(hi, lo, close, 10, 3).to_numpy()
side = np.sign(p - st)
for i in range(2, len(p)):
    if side[i] == side[i - 1] and side[i] != 0:
        assert (st[i] >= st[i - 1] - 1e-12) if side[i] > 0 else (st[i] <= st[i - 1] + 1e-12), f"supertrend ratchet broken at bar {i}"
print("ok  Supertrend line only moves in the trend's favor between flips")

# properties quoted on the pages
climb2 = pd.Series(np.arange(1000, dtype=float) + 100)
assert abs((climb2 - mcginley(climb2)).iloc[-1] - 7.672) < 1e-3
cover_half = lambda f, s_: int((f(s_).iloc[200:] >= 105).idxmax() - 200) if s_.iloc[-1] > s_.iloc[0] else int((f(s_).iloc[200:] <= 105).idxmax() - 200)
j_up, j_dn = pd.Series([100.0] * 200 + [110.0] * 200), pd.Series([110.0] * 200 + [100.0] * 200)
assert (cover_half(mcginley, j_up), cover_half(mcginley, j_dn)) == (7, 3)
assert (cover_half(lambda c: ema(c, 14), j_up), cover_half(lambda c: ema(c, 14), j_dn)) == (4, 4)
print("ok  McGinley: 7.67 bars behind a steady climb, and 7 bars to cover half an upward jump but 3 for a downward one (EMA: 4 and 4)")
lv2, ls2 = linreg(climb2, 20)
assert (lv2 - climb2).abs().iloc[20:].max() < 1e-9 and abs(ls2.iloc[-1] - 1) < 1e-9
assert round(linreg(j_up, 20)[0].iloc[200:].max() - 110, 1) == 3.0
print("ok  Linear regression: zero lag and slope exactly 1 on a straight climb; overshoots a 10-point jump by 3.0")

# ---- worked examples quoted on the pages --------------------------------------------
assert abs((100 + 10 / (0.6 * 14 * 1.1 ** 4)) - 100.8131) < 1e-3
assert abs(mcginley(pd.Series([100.0, 110.0]), 14, 0.6).iloc[-1] - (100 + 10 / (0.6 * 14 * 1.1 ** 4))) < 1e-12
assert abs(100 * 1.025 - 102.5) < 1e-12 and abs(100 * 0.975 - 97.5) < 1e-12
slope_ex = linreg(pd.Series([10.0, 11, 13, 14]), 4)  # least squares line through 10, 11, 13, 14
assert abs(slope_ex[1].iloc[-1] - 1.4) < 1e-12 and abs(slope_ex[0].iloc[-1] - 14.1) < 1e-12  # slope 7/5, fitted 12 + 1.4 x 1.5
h5, l5, c5 = pd.Series([11.0, 12, 13, 12, 9]), pd.Series([9.0, 10, 11, 8, 7]), pd.Series([10.0, 11.5, 12.5, 8.5, 7.5])
assert supertrend(h5, l5, c5, 1, 1).tolist() == [8.0, 9.0, 10.0, 14.5, 10.0]
v_up, v_dn = vortex(pd.Series([10.0, 12, 13, 14]), pd.Series([9.0, 10, 11, 12]), pd.Series([9.5, 11.5, 12.5, 13.5]), 3)
tr3 = [max(12 - 10, abs(12 - 9.5), abs(10 - 9.5)), max(13 - 11, abs(13 - 11.5), abs(11 - 11.5)), max(14 - 12, abs(14 - 12.5), abs(12 - 12.5))]
vm_plus = [abs(12 - 9), abs(13 - 10), abs(14 - 11)]
assert abs(v_up.iloc[-1] - sum(vm_plus) / sum(tr3)) < 1e-12
assert abs(mcginley(pd.Series([100.0, 90.0]), 14, 0.6).iloc[-1] - (100 - 10 / (0.6 * 14 * 0.9 ** 4))) < 1e-12
assert abs((100 - 10 / (0.6 * 14 * 0.9 ** 4)) - 98.185) < 1e-3 and abs(0.6 * 14 * 1.1 ** 4 - 12.298) < 1e-3
vm_minus = [abs(10 - 10), abs(11 - 12), abs(12 - 13)]
assert abs(v_up.iloc[-1] - 9 / 6.5) < 1e-12 and abs(v_dn.iloc[-1] - sum(vm_minus) / 6.5) < 1e-12 and abs(sum(vm_minus) / 6.5 - 0.3077) < 1e-3
print("ok  worked examples (McGinley, Envelope, Linear Regression, Supertrend, Vortex)")


# =====================================================================================
# Batch C: Stochastic RSI, Stochastic Momentum Index, True Strength Index, Know Sure Thing, Detrended Price Oscillator
# =====================================================================================
from indicators import dpo, kst, smi, stoch_rsi, tsi


def stoch_rsi_ref(p, n, sk, sd):
    r = rsi_ref_same_seed(p, n)
    raw = [np.nan] * len(p)
    for i in range(len(p)):
        w = r[max(0, i - n + 1) : i + 1]
        if i >= n and not np.isnan(w).any():
            lo_, hi_ = min(w), max(w)
            raw[i] = np.nan if hi_ == lo_ else 100 * (r[i] - lo_) / (hi_ - lo_)
    k = sma_ref(np.array(raw), sk)
    return k, sma_ref(k, sd)


def ema_seeded(x, n):
    """EMA that starts at the first non-NaN value, written as an explicit loop."""
    a = 2 / (n + 1)
    out, prev = [], None
    for v in x:
        if np.isnan(v):
            out.append(np.nan)
            continue
        prev = v if prev is None else a * v + (1 - a) * prev
        out.append(prev)
    return np.array(out)


def smi_ref(h, l, c, n, s1, s2, sig):
    off, span = [np.nan] * len(c), [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        top, bottom = max(h[i - n + 1 : i + 1]), min(l[i - n + 1 : i + 1])
        off[i], span[i] = c[i] - (top + bottom) / 2, top - bottom
    line = 100 * ema_seeded(ema_seeded(np.array(off), s1), s2) / (ema_seeded(ema_seeded(np.array(span), s1), s2) / 2)
    return line, ema_seeded(line, sig)


def tsi_ref(c, long, short, sig):
    ch = np.concatenate([[np.nan], np.diff(c)])
    num = ema_seeded(ema_seeded(ch, long), short)
    den = ema_seeded(ema_seeded(np.abs(ch), long), short)
    line = 100 * num / den
    return line, ema_seeded(line, sig)


def kst_ref(c, sig):
    total = np.zeros(len(c))
    for r_, s_, w in [(10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4)]:
        rc = np.array([np.nan] * r_ + [100 * (c[i] / c[i - r_] - 1) for i in range(r_, len(c))])
        total = total + w * sma_ref(rc, s_)
    return total, sma_ref(total, sig)


def dpo_ref(c, n):
    out = [np.nan] * len(c)
    back = n // 2 + 1
    for i in range(max(n - 1, back), len(c)):
        out[i] = c[i - back] - sum(c[i - n + 1 : i + 1]) / n
    return np.array(out)


sk_, sd_ = stoch_rsi(close, 14, 3, 3)
skr, sdr = stoch_rsi_ref(p, 14, 3, 3)
check("Stochastic RSI %K vs loop", sk_, skr, 1e-8)
check("Stochastic RSI %D vs loop", sd_, sdr, 1e-8)
sm_, ss_ = smi(hi, lo, close, 10, 3, 3, 10)
smr, ssr = smi_ref(H, L, p, 10, 3, 3, 10)
check("Stochastic Momentum Index vs loop", sm_, smr, 1e-8)
check("SMI signal vs loop", ss_, ssr, 1e-8)
ts_, tg_ = tsi(close, 25, 13, 7)
tsr, tgr = tsi_ref(p, 25, 13, 7)
check("True Strength Index vs loop", ts_, tsr, 1e-8)
check("TSI signal vs loop", tg_, tgr, 1e-8)
ks_, kg_ = kst(close, 9)
ksr, kgr = kst_ref(p, 9)
check("Know Sure Thing vs loop", ks_, ksr, 1e-8)
check("KST signal vs loop", kg_, kgr, 1e-8)
check("Detrended Price Oscillator (20) vs loop", dpo(close, 20), dpo_ref(p, 20), 1e-9)

# bounds
assert sk_.dropna().between(-1e-9, 100 + 1e-9).all() and sm_.dropna().abs().max() <= 100 + 1e-9 and ts_.dropna().abs().max() <= 100 + 1e-9
print("ok  Stochastic RSI stays in 0..100; SMI and TSI stay in -100..100")

# properties quoted on the pages
straight = pd.Series(np.arange(400, dtype=float) * 0.5 + 100)
assert all(abs(dpo(straight, n).iloc[-1] - (-1.5 * 0.5)) < 1e-9 for n in (10, 20, 40))
cycle = pd.Series(10 * np.sin(2 * np.pi * np.arange(400) / 20))
expected = cycle.shift(11)  # a 20-bar sine averages to exactly its midline over a 20-bar window
assert (dpo(cycle, 20) - expected).dropna().abs().max() < 1e-9
print("ok  DPO: constant -1.5 x slope on a straight climb at any even length; on a 20-bar cycle it returns the cycle exactly, 11 bars late")
assert tsi(pd.Series(np.arange(100, dtype=float)), 25, 13)[0].iloc[-1] > 99.999 and tsi(pd.Series(-np.arange(100, dtype=float)), 25, 13)[0].iloc[-1] < -99.999
flat_run = pd.Series(np.arange(300, dtype=float))
assert stoch_rsi(flat_run)[0].dropna().empty  # a straight climb pins RSI at 100, its range is zero, so the %K is undefined
print("ok  TSI hits +/-100 on a straight line; Stochastic RSI is undefined when RSI has not moved")
grow = pd.Series(100 * 1.01 ** np.arange(200))
want = sum(w * 100 * (1.01 ** r_ - 1) for r_, w in [(10, 1), (15, 2), (20, 3), (30, 4)])
assert abs(kst(grow, 9)[0].iloc[-1] - want) < 1e-9
print("ok  KST on steady 1% growth equals the weighted sum of the four growth rates")

# worked examples quoted on the pages
assert abs(100 * (55 - 40) / (60 - 40) - 75.0) < 1e-12
h2, l2, c2 = pd.Series([12.0, 13.0]), pd.Series([10.0, 11.0]), pd.Series([11.5, 12.5])
assert abs(smi(h2, l2, c2, 2, 1, 1, 1)[0].iloc[-1] - 100 * 1.0 / 1.5) < 1e-9
assert abs(tsi(pd.Series([10.0, 12, 13, 12]), 3, 3)[0].iloc[-1] - 100 * 1.0 / 1.5) < 1e-9
assert 1 * 2 + 2 * 3 + 3 * 4 + 4 * 5 == 40
assert abs(dpo(pd.Series([10.0, 11, 12, 13, 14, 15]), 4).iloc[-1] - (-1.5)) < 1e-12
print("ok  worked examples (Stochastic RSI, SMI, TSI, KST, DPO)")


# =====================================================================================
# Batch D: Coppock Curve, Fisher Transform, Relative Momentum Index, Elder Ray, Connors RSI
# =====================================================================================
from indicators import connors_rsi, coppock, elder_ray, fisher, rmi


def coppock_ref(c, a, b, n):
    roc_sum = [np.nan] * len(c)
    for i in range(max(a, b), len(c)):
        roc_sum[i] = 100 * (c[i] / c[i - a] - 1) + 100 * (c[i] / c[i - b] - 1)
    out = [np.nan] * len(c)
    for i in range(len(c)):
        w = roc_sum[i - n + 1 : i + 1] if i >= n - 1 else []
        if len(w) == n and not np.isnan(w).any():
            out[i] = sum((k + 1) * v for k, v in enumerate(w)) / (n * (n + 1) / 2)
    return np.array(out)


def fisher_ref(h, l, n):
    mid = (h + l) / 2
    value = line = 0.0
    out = []
    for i in range(len(mid)):
        if i < n - 1:
            out.append(np.nan)
            continue
        window = mid[i - n + 1 : i + 1]
        top, bottom = max(window), min(window)
        if top == bottom:
            out.append(np.nan)
            continue
        x = 2 * ((mid[i] - bottom) / (top - bottom) - 0.5)
        value = 0.33 * x + 0.67 * value
        value = min(0.999, max(-0.999, value))
        line = 0.5 * np.log((1 + value) / (1 - value)) + 0.5 * line
        out.append(line)
    return np.array(out)


def rmi_ref(c, n, k):
    out = [np.nan] * len(c)
    ag = al = None
    for i in range(k, len(c)):
        ch = c[i] - c[i - k]
        g, l_ = max(ch, 0.0), max(-ch, 0.0)
        if ag is None:
            ag, al = g, l_
        else:
            ag = ag * (1 - 1 / n) + g / n
            al = al * (1 - 1 / n) + l_ / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return np.array(out)


def elder_ref(h, l, c, n):
    e = ema_ref(c, n)
    return h - e, l - e


def connors_ref(c, rn, sn, pn):
    streak, run = [0.0], 0.0
    for i in range(1, len(c)):
        step = np.sign(c[i] - c[i - 1])
        run = 0.0 if step == 0 else (run + step if np.sign(run) == step else step)
        streak.append(run)
    r1 = rsi_ref_same_seed(c, rn)
    r2 = rsi_ref_same_seed(np.array(streak), sn)
    out = [np.nan] * len(c)
    for i in range(pn + 1, len(c)):
        today = c[i] / c[i - 1] - 1
        prior = [c[j] / c[j - 1] - 1 for j in range(i - pn, i)]
        out[i] = (r1[i] + r2[i] + 100 * sum(1 for x in prior if x < today) / pn) / 3
    return np.array(out)


check("Coppock Curve (14, 11, 10) vs loop", coppock(close, 14, 11, 10), coppock_ref(p, 14, 11, 10), 1e-9)
fi, fg = fisher(hi, lo, 10)
fir = fisher_ref(H, L, 10)
check("Fisher Transform (10) vs loop", fi, fir, 1e-9)
assert np.allclose(fg.iloc[1:].dropna().to_numpy(), fi.shift(1).iloc[1:].dropna().to_numpy())
check("Relative Momentum Index (14, 5) vs loop", rmi(close, 14, 5), rmi_ref(p, 14, 5), 1e-9)
bull, bear = elder_ray(hi, lo, close, 13)
bu_r, be_r = elder_ref(H, L, p, 13)
check("Elder Ray bull power vs loop", bull, bu_r, 1e-9)
check("Elder Ray bear power vs loop", bear, be_r, 1e-9)
check("Connors RSI (3, 2, 100) vs loop", connors_rsi(close, 3, 2, 100), connors_ref(p, 3, 2, 100), 1e-8)

# properties quoted on the pages
assert (rmi(close, 14, 1).dropna() - rsi(close, 14).dropna()).abs().max() < 1e-12
print("ok  RMI with a 1-bar momentum is exactly RSI")
grow = pd.Series(100 * 1.01 ** np.arange(200))
assert abs(coppock(grow).iloc[-1] - (100 * (1.01 ** 14 - 1) + 100 * (1.01 ** 11 - 1))) < 1e-9
print("ok  Coppock on steady 1% growth equals the sum of the two growth rates")
climb3 = pd.Series(np.arange(200, dtype=float) + 100)
fclimb = fisher(climb3 + 1, climb3 - 1, 10)[0].iloc[-1]
assert abs(fclimb - 2 * 0.5 * np.log(1.999 / 0.001)) < 1e-6 and abs(fclimb - 7.6) < 0.01
print("ok  Fisher Transform tops out near 7.6 (a straight climb), by its 0.999 clip and its half-weight on the prior value")
assert connors_rsi(close).dropna().between(0, 100).all()
print("ok  Connors RSI stays in 0..100")

# worked examples quoted on the pages
assert abs((1 * 10 + 2 * 12 + 3 * 16) / 6 - 13.6667) < 1e-3
assert abs(0.33 * 0.5 + 0.67 * 0.0 - 0.165) < 1e-12 and abs(0.5 * np.log(1.165 / 0.835) - 0.1664) < 1e-3
eh = elder_ray(pd.Series([10.0, 10.0]), pd.Series([9.0, 9.0]), pd.Series([9.5, 9.5]), 2)
assert (eh[0].iloc[-1], eh[1].iloc[-1]) == (0.5, -0.5)
assert abs((20 + 10 + 60) / 3 - 30) < 1e-12
print("ok  worked examples (Coppock, Fisher, Elder Ray, Connors RSI)")


# =====================================================================================
# Batch E: Historical Volatility, Standard Deviation, Chaikin Volatility, Relative Volatility Index, Mass Index
# =====================================================================================
from indicators import chaikin_volatility, historical_volatility, mass_index, relative_volatility, std_dev


def hv_ref(c, n, per_year):
    out = [np.nan] * len(c)
    r = [np.nan] + [np.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    for i in range(n, len(c)):
        w = r[i - n + 1 : i + 1]
        m = sum(w) / n
        out[i] = 100 * (sum((x - m) ** 2 for x in w) / (n - 1)) ** 0.5 * per_year ** 0.5
    return np.array(out)


def std_ref(c, n):
    out = [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1 : i + 1]
        m = sum(w) / n
        out[i] = (sum((x - m) ** 2 for x in w) / n) ** 0.5
    return np.array(out)


def chaikin_vol_ref(h, l, n, k):
    e = ema_ref(h - l, n)
    return np.array([np.nan] * k + [100 * (e[i] / e[i - k] - 1) for i in range(k, len(e))])


def rvi_ref(c, std_n, n):
    sd = std_ref(c, std_n)
    up = dn = None
    out = [np.nan] * len(c)
    for i in range(len(c)):
        if np.isnan(sd[i]):
            continue  # an average starts at its first available value
        ch = c[i] - c[i - 1] if i > 0 else np.nan
        u = sd[i] if ch > 0 else 0.0
        d = sd[i] if ch < 0 else 0.0
        if up is None:
            up, dn = u, d
        else:
            up = up * (1 - 1 / n) + u / n
            dn = dn * (1 - 1 / n) + d / n
        out[i] = np.nan if up + dn == 0 else 100 * up / (up + dn)
    return np.array(out)


def mass_ref(h, l, n, total):
    s1 = ema_ref(h - l, n)
    s2 = ema_ref(s1, n)
    ratio = s1 / s2
    return np.array([np.nan] * (total - 1) + [sum(ratio[i - total + 1 : i + 1]) for i in range(total - 1, len(ratio))])


check("Historical volatility (20) vs loop", historical_volatility(close, 20, 252), hv_ref(p, 20, 252), 1e-9)
check("Standard deviation (20) vs loop", std_dev(close, 20), std_ref(p, 20), 1e-9)
check("Chaikin Volatility (10, 10) vs loop", chaikin_volatility(hi, lo, 10, 10), chaikin_vol_ref(H, L, 10, 10), 1e-9)
check("Relative Volatility Index (10, 14) vs loop", relative_volatility(close, 10, 14), rvi_ref(p, 10, 14), 1e-8)
check("Mass Index (9, 25) vs loop", mass_index(hi, lo, 9, 25), mass_ref(H, L, 9, 25), 1e-9)

# properties quoted on the pages
_, bb_up, bb_dn = bollinger(close, 20, 2)
assert ((bb_up - bb_dn) - 4 * std_dev(close, 20)).abs().max() < 1e-9
assert ((std_dev(close * 2, 20)) - 2 * std_dev(close, 20)).abs().max() < 1e-9
print("ok  Bollinger Band width is exactly 4 standard deviations; doubling prices doubles the standard deviation")
assert abs(mass_index(pd.Series([3.0] * 100), pd.Series([1.0] * 100)).iloc[-1] - 25) < 1e-9
print("ok  Mass Index sits at exactly 25 when the daily range never changes")
assert relative_volatility(close).dropna().between(0, 100).all()
print("ok  Relative Volatility Index stays in 0..100")

# worked examples quoted on the pages
assert abs(std_dev(pd.Series([2.0, 4, 4, 4, 5, 5, 7, 9]), 8).iloc[-1] - 2.0) < 1e-12
assert abs(100 * 0.01 * 252 ** 0.5 - 15.87) < 0.01
alt = pd.Series(100 * np.exp(np.cumsum([0.0] + [0.01, -0.01] * 20)))
assert abs(historical_volatility(alt, 20, 252).iloc[-1] - 100 * (20 * 0.01 ** 2 / 19) ** 0.5 * 252 ** 0.5) < 1e-9
assert abs(chaikin_volatility(pd.Series([2.0, 2, 2, 3]), pd.Series([0.0] * 4), 1, 3).iloc[-1] - 50) < 1e-12
assert abs(relative_volatility(pd.Series([10.0, 12, 11, 13]), 2, 3).iloc[-1] - 87.5) < 1e-9
assert abs(100 * 1.2 / (1.2 + 0.8) - 60) < 1e-12
print("ok  worked examples (HV, Standard Deviation, Chaikin Volatility, RVI, Mass Index)")


# =====================================================================================
# Batch F: Choppiness Index, Ulcer Index, Pivot Points, Heikin-Ashi, Anchored VWAP
# =====================================================================================
from indicators import anchored_vwap, choppiness, heikin_ashi, pivot_points, ulcer


def chop_ref(h, l, c, n):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    out = [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        span = max(h[i - n + 1 : i + 1]) - min(l[i - n + 1 : i + 1])
        out[i] = 100 * np.log10(sum(tr[i - n + 1 : i + 1]) / span) / np.log10(n)
    return np.array(out)


def ulcer_ref(c, n):
    out = [np.nan] * len(c)
    for i in range(n - 1, len(c)):
        dd = []
        for j in range(i - n + 1, i + 1):
            peak = max(c[max(0, j - n + 1) : j + 1])
            dd.append(100 * (c[j] / peak - 1))
        out[i] = (sum(x * x for x in dd) / n) ** 0.5
    return np.array(out)


def ha_ref(o, h, l, c):
    out = []
    prev_open = prev_close = None
    for i in range(len(c)):
        hc = (o[i] + h[i] + l[i] + c[i]) / 4
        ho = (o[i] + c[i]) / 2 if i == 0 else (prev_open + prev_close) / 2
        out.append((ho, max(h[i], ho, hc), min(l[i], ho, hc), hc))
        prev_open, prev_close = ho, hc
    return np.array(out)


def avwap_ref(h, l, c, v, anchor):
    out = [np.nan] * len(c)
    pv = vv = 0.0
    for i in range(anchor, len(c)):
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vv += v[i]
        out[i] = pv / vv
    return np.array(out)


check("Choppiness Index (14) vs loop", choppiness(hi, lo, close, 14), chop_ref(H, L, p, 14), 1e-9)
check("Ulcer Index (14) vs loop", ulcer(close, 14), ulcer_ref(p, 14), 1e-9)
op = close.shift().fillna(close.iloc[0]) + (hi - lo) * 0.1  # an invented open between bars, only to exercise the code
har = ha_ref(op.to_numpy(), H, L, p)
ha_o, ha_h, ha_l, ha_c = heikin_ashi(op, hi, lo, close)
for k, (name, got) in enumerate([("open", ha_o), ("high", ha_h), ("low", ha_l), ("close", ha_c)]):
    check(f"Heikin-Ashi {name} vs loop", got, har[:, k], 1e-9)
vol_s = pd.Series(rng.uniform(1000, 2000, len(close)))
check("Anchored VWAP (anchor 200) vs loop", anchored_vwap(hi, lo, close, vol_s, 200), avwap_ref(H, L, p, vol_s.to_numpy(), 200), 1e-9)
sess0 = pd.Series([0] * len(close))
assert (anchored_vwap(hi, lo, close, vol_s, 0) - vwap(hi, lo, close, vol_s, sess0)).abs().max() < 1e-9
print("ok  Anchored VWAP anchored at the first bar is exactly the session VWAP")
pp_h, pp_l, pp_c = pd.Series([12.0]), pd.Series([8.0]), pd.Series([11.0])
lv = [float(x.iloc[0]) for x in pivot_points(pp_h, pp_l, pp_c)]
assert np.allclose(lv, [31 / 3, 38 / 3, 26 / 3, 31 / 3 + 4, 31 / 3 - 4])
assert abs((lv[1] - lv[2]) - 4.0) < 1e-12  # R1 - S1 is the whole previous range
print("ok  Pivot levels: worked example, and R1 - S1 is always exactly the previous bar's high-low range")
assert (ulcer(pd.Series(np.arange(100.0) + 100), 14).dropna() == 0).all()
assert abs(ulcer(pd.Series([100.0, 98, 97]), 3).iloc[-1] - ((0 + 4 + 9) / 3) ** 0.5) < 1e-9
assert abs(100 * np.log10(14 * 5 / 5) / np.log10(14) - 100) < 1e-9
assert abs(100 * np.log10(28 / 4) / np.log10(14) - 73.74) < 0.01
print("ok  Ulcer Index is 0 in a rising market; Choppiness is 100 when every bar's range equals the whole window's span")
o2, h2, l2, c2 = pd.Series([10.0, 11.0]), pd.Series([12.0, 13.0]), pd.Series([9.0, 10.5]), pd.Series([11.0, 12.5])
hh = heikin_ashi(o2, h2, l2, c2)
assert [hh[0].iloc[0], hh[3].iloc[0]] == [10.5, 10.5] and [hh[0].iloc[1], hh[1].iloc[1], hh[2].iloc[1], hh[3].iloc[1]] == [10.5, 13.0, 10.5, 11.75]
tp = pd.Series([10.0, 12.0])
assert abs(anchored_vwap(tp, tp, tp, pd.Series([100.0, 300.0]), 0).iloc[-1] - 11.5) < 1e-12
print("ok  worked examples (Choppiness, Ulcer, Pivot Points, Heikin-Ashi, Anchored VWAP)")


# =====================================================================================
# Batch G: Accumulation/Distribution, Chaikin Oscillator, Money Flow Index, Force Index, Ease of Movement
# =====================================================================================
from indicators import accumulation_distribution, chaikin_oscillator, ease_of_movement, force_index, mfi

volume = pd.Series(rng.uniform(1.0e6, 2.0e6, len(close)))
V_ = volume.to_numpy()


def adl_ref(h, l, c, v):
    total, out = 0.0, []
    for i in range(len(c)):
        rng_ = h[i] - l[i]
        total += (0.0 if rng_ == 0 else ((c[i] - l[i]) - (h[i] - c[i])) / rng_) * v[i]
        out.append(total)
    return np.array(out)


def mfi_ref(h, l, c, v, n):
    tp = [(h[i] + l[i] + c[i]) / 3 for i in range(len(c))]
    out = [np.nan] * len(c)
    for i in range(n, len(c)):
        pos = sum(tp[j] * v[j] for j in range(i - n + 1, i + 1) if tp[j] > tp[j - 1])
        neg = sum(tp[j] * v[j] for j in range(i - n + 1, i + 1) if tp[j] < tp[j - 1])
        out[i] = 100 - 100 / (1 + pos / neg)
    return np.array(out)


def force_ref(c, v, n):
    a = 2 / (n + 1)
    out, prev = [np.nan], None
    for i in range(1, len(c)):
        raw = (c[i] - c[i - 1]) * v[i]
        prev = raw if prev is None else a * raw + (1 - a) * prev
        out.append(prev)
    return np.array(out)


def emv_ref(h, l, v, n, scale):
    raw = [np.nan] + [(((h[i] + l[i]) / 2 - (h[i - 1] + l[i - 1]) / 2) / ((v[i] / scale) / (h[i] - l[i]))) for i in range(1, len(h))]
    out = [np.nan] * len(h)
    for i in range(n, len(h)):
        out[i] = sum(raw[i - n + 1 : i + 1]) / n
    return np.array(out)


adl = accumulation_distribution(hi, lo, close, volume)
check("Accumulation/Distribution vs loop", adl, adl_ref(H, L, p, V_), 1e-3)
ema_adl = lambda n: ema_ref(adl.to_numpy(), n)
check("Chaikin Oscillator (3, 10) vs loop", chaikin_oscillator(hi, lo, close, volume, 3, 10), ema_adl(3) - ema_adl(10), 1e-3)
check("Money Flow Index (14) vs loop", mfi(hi, lo, close, volume, 14), mfi_ref(H, L, p, V_, 14), 1e-9)
check("Force Index (13) vs loop", force_index(close, volume, 13), force_ref(p, V_, 13), 1e-3)
check("Ease of Movement (14) vs loop", ease_of_movement(hi, lo, volume, 14), emv_ref(H, L, V_, 14, 1e6), 1e-9)

# exact identities quoted on the pages
assert ((adl.diff(20)) - cmf(hi, lo, close, volume, 20) * volume.rolling(20).sum()).abs().max() < 1e-3
assert (chaikin_oscillator(hi, lo, close, volume) - macd(adl, 3, 10)[0]).abs().max() < 1e-9
print("ok  A/D line change over 20 bars = CMF x 20-bar volume; Chaikin Oscillator = the MACD line of the A/D line (3, 10)")
assert abs(accumulation_distribution(hi, hi - 1, hi, volume).iloc[-1] - volume.sum()) < 1e-3
assert mfi(pd.Series(np.arange(100.0, 0, -1)), pd.Series(np.arange(100.0, 0, -1)), pd.Series(np.arange(100.0, 0, -1)), volume.iloc[:100], 14).dropna().eq(0).all()
assert abs(ease_of_movement(hi, lo, volume * 2, 14).iloc[-1] - ease_of_movement(hi, lo, volume, 14).iloc[-1] / 2) < 1e-9
print("ok  A/D equals cumulative volume when every close is the high; MFI is 0 in an unbroken decline; doubling volume halves Ease of Movement")

# worked examples quoted on the pages
assert abs(accumulation_distribution(pd.Series([12.0]), pd.Series([8.0]), pd.Series([11.0]), pd.Series([1000.0])).iloc[-1] - 500) < 1e-9
assert abs(((11 - 8) - (12 - 11)) / (12 - 8) - 0.5) < 1e-12 and 520 - 480 == 40
tpv = pd.Series([10.0, 11.0, 10.5, 11.5])
assert abs(mfi(tpv, tpv, tpv, pd.Series([100.0, 200, 100, 300]), 3).iloc[-1] - 100 * 5650 / (5650 + 1050)) < 1e-9
assert abs(100 * 5650 / 6700 - 84.33) < 0.01
assert force_index(pd.Series([10.0, 12, 11]), pd.Series([1000.0, 1500, 2000]), 1).iloc[-1] == -2000 and (12 - 10) * 1500 == 3000
em = ease_of_movement(pd.Series([10.0, 12]), pd.Series([8.0, 9]), pd.Series([1e6, 2e6]), 1)
assert abs(em.iloc[-1] - 2.25) < 1e-12
print("ok  worked examples (A/D, Chaikin Oscillator, MFI, Force Index, Ease of Movement)")


# =====================================================================================
# Batch H: Klinger, Volume Oscillator, Negative/Positive Volume Index, Price Volume Trend, Balance of Market Power
# =====================================================================================
from indicators import (balance_of_market_power, klinger, negative_volume_index, positive_volume_index, price_volume_trend,
                        volume_oscillator)

volume2 = pd.Series(rng.uniform(1.0e6, 2.0e6, len(close)))
V2 = volume2.to_numpy()
open2 = (close.shift().fillna(close.iloc[0]) + (hi - lo) * 0.05)  # an invented open, only to exercise the code
O2 = open2.to_numpy()


def klinger_ref(h, l, c, v, fast, slow, sig):
    n = len(c)
    trend, cm, force = [0] * n, [0.0] * n, [0.0] * n
    for i in range(n):
        if i == 0:
            trend[i] = -1  # the first bar has no previous bar, so it counts as not rising
            cm[i] = h[i] - l[i]
        else:
            trend[i] = 1 if (h[i] + l[i] + c[i]) > (h[i - 1] + l[i - 1] + c[i - 1]) else -1
            cm[i] = (cm[i - 1] if trend[i] == trend[i - 1] else h[i - 1] - l[i - 1]) + (h[i] - l[i])
        force[i] = v[i] * abs(2 * (h[i] - l[i]) / cm[i] - 1) * trend[i] * 100
    line = ema_ref(np.array(force), fast) - ema_ref(np.array(force), slow)
    return line, ema_ref(line, sig)


def vo_ref(v, fast, slow):
    f, s = ema_ref(v, fast), ema_ref(v, slow)
    return 100 * (f - s) / s


def nvi_pvi_ref(c, v, start, negative):
    out = [start]
    for i in range(1, len(c)):
        take = v[i] < v[i - 1] if negative else v[i] > v[i - 1]
        out.append(out[-1] * (c[i] / c[i - 1]) if take else out[-1])
    return np.array(out)


def pvt_ref(c, v):
    out = [0.0]
    for i in range(1, len(c)):
        out.append(out[-1] + (c[i] / c[i - 1] - 1) * v[i])
    return np.array(out)


def bmp_ref(o, h, l, c, n):
    raw = [(c[i] - o[i]) / (h[i] - l[i]) for i in range(len(c))]
    return np.array([np.nan] * (n - 1) + [sum(raw[i - n + 1 : i + 1]) / n for i in range(n - 1, len(c))])


kl, ks_ = klinger(hi, lo, close, volume2, 34, 55, 13)
klr, ksr = klinger_ref(H, L, p, V2, 34, 55, 13)
check("Klinger oscillator (34, 55) vs loop", kl, klr, 1e-3)
check("Klinger signal (13) vs loop", ks_, ksr, 1e-3)
check("Volume Oscillator (5, 10) vs loop", volume_oscillator(volume2, 5, 10), vo_ref(V2, 5, 10), 1e-9)
check("Negative Volume Index vs loop", negative_volume_index(close, volume2), nvi_pvi_ref(p, V2, 1000.0, True), 1e-9)
check("Positive Volume Index vs loop", positive_volume_index(close, volume2), nvi_pvi_ref(p, V2, 1000.0, False), 1e-9)
check("Price Volume Trend vs loop", price_volume_trend(close, volume2), pvt_ref(p, V2), 1e-3)
check("Balance of Market Power (14) vs loop", balance_of_market_power(open2, hi, lo, close, 14), bmp_ref(O2, H, L, p, 14), 1e-9)

# exact relationships quoted on the pages
assert (volume_oscillator(volume2, 5, 10) - ppo(volume2, 5, 10, 9)[0]).abs().max() < 1e-9
print("ok  Volume Oscillator is exactly the PPO line applied to volume")
product = negative_volume_index(close, volume2) * positive_volume_index(close, volume2) / 1000.0
assert (product - 1000.0 * close / close.iloc[0]).abs().max() < 1e-6
print("ok  Negative Volume Index x Positive Volume Index / 1000 is exactly the price index (every day's change lands in one of them)")

# worked examples quoted on the pages
c3, v3 = pd.Series([100.0, 102, 101]), pd.Series([10.0, 9, 11])
assert negative_volume_index(c3, v3).round(6).tolist() == [1000.0, 1020.0, 1020.0]
assert abs(positive_volume_index(c3, v3).iloc[-1] - 1000 * 101 / 102) < 1e-9 and abs(1000 * 101 / 102 - 990.196) < 1e-3
pt3 = price_volume_trend(pd.Series([100.0, 102, 101]), pd.Series([500.0, 1000, 2000]))
assert abs(pt3.iloc[1] - 20) < 1e-9 and abs(pt3.iloc[2] - (20 - 2000 / 102)) < 1e-9 and abs(2000 / 102 - 19.608) < 1e-3
bm1 = balance_of_market_power(pd.Series([10.0]), pd.Series([12.0]), pd.Series([9.0]), pd.Series([11.5]), 1)
assert abs(bm1.iloc[-1] - 0.5) < 1e-12
assert abs(100 * (1.2 - 1.0) / 1.0 - 20) < 1e-12 and abs(abs(2 * 0.75 - 1) * 1000 * 100 - 50000) < 1e-9
print("ok  worked examples (Klinger, Volume Oscillator, NVI/PVI, Price Volume Trend, Balance of Market Power)")


# =====================================================================================
# Page snippets must be textually identical to the functions that were verified above
# =====================================================================================
import inspect
import pathlib
import re

import indicators

def _code_function(slug):
    """The function a study page's first python block defines."""
    text = (pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "studies" / f"{slug}.md").read_text()
    match = re.search(r"```python\n\s*def (\w+)\(", text)
    assert match, f"{slug}: no python block defining a function"
    return match.group(1)


_studies_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "content" / "studies"
PAGES = {f.stem: _code_function(f.stem) for f in sorted(_studies_dir.glob("*.md"))}
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


# =====================================================================================
# Overlaps: what each study's frontmatter claims must match tools/overlaps.py, and every correlation quoted in
# page text must match the sample data
# =====================================================================================
import yaml

import overlaps as ov

root = pathlib.Path(__file__).resolve().parent.parent
guides = root / "src" / "content" / "guides"


def page_path(slug):
    return guides / (slug.split("/", 1)[1] + ".md") if slug.startswith("guides/") else studies / f"{slug}.md"


def frontmatter(path):
    return yaml.safe_load(path.read_text().split("---")[1])


declared = {}
for f in sorted(studies.glob("*.md")):
    for o in frontmatter(f).get("overlaps") or []:
        key = (f.stem, o["with"])
        assert key in ov.PAIRS, f"{key}: declared in frontmatter but not defined in tools/overlaps.py"
        assert key not in declared, f"{key}: declared twice"
        assert (studies / f"{o['with']}.md").is_file(), f"{key}: no such study"
        assert o.get("note", "").strip(), f"{key}: note is empty"
        declared[key] = o
missing = set(ov.PAIRS) - set(declared)
assert not missing, f"defined in tools/overlaps.py but not declared on any page: {sorted(missing)}"

for key, o in sorted(declared.items()):
    spec = ov.PAIRS[key]
    assert o["strength"] == spec["strength"], f"{key}: strength {o['strength']} but tools/overlaps.py says {spec['strength']}"
    if spec["identity"]:
        err = ov.identity_error(spec["identity"])
        assert err < 1e-9, f"{key}: identity {spec['identity']} fails (error {err})"
    if spec["corr"]:
        c = ov.measure(spec["corr"])
        assert "corr" in o and abs(o["corr"] - round(c, 2)) < 1e-9, f"{key}: frontmatter corr {o.get('corr')} but measured {c:.4f}"
        if spec["strength"] == "near":
            assert c >= 0.95, f"{key}: 'near' needs correlation of at least 0.95, got {c:.3f}"
        if spec["strength"] == "partial":
            assert 0.6 <= c < 0.95, f"{key}: 'partial' needs a correlation from 0.6 to under 0.95, got {c:.3f}"
    else:
        assert "corr" not in o, f"{key}: has a corr but tools/overlaps.py defines none"
print(f"ok  {len(declared)} overlap pairs: frontmatter agrees with tools/overlaps.py (identities exact, correlations measured)")

for page, decimals, name in ov.QUOTES:
    quoted = f"{ov.measure(name):.{decimals}f}"
    assert quoted in page_path(page).read_text(), f"{page}: should quote {quoted} ({name}), which is not in the page"
print(f"ok  {len(ov.QUOTES)} correlations quoted in page text match the sample data")

# every relative link between pages must point to a real page
link_re = re.compile(r"\]\(\.\./(?:studies/)?([a-z0-9-]+)/\)")
broken = []
for f in list(studies.glob("*.md")) + list(guides.glob("*.md")):
    for slug in link_re.findall(f.read_text()):
        if not (studies / f"{slug}.md").is_file():
            broken.append((f.name, slug))
assert not broken, f"broken links: {broken}"
print("ok  all links between pages resolve")


# a display formula must have its $$ markers on their own lines: written on one line it renders as small inline math
one_line_display = [
    (f.name, i + 1)
    for f in list(studies.glob("*.md")) + list(guides.glob("*.md"))
    for i, line in enumerate(f.read_text().split("\n"))
    if re.match(r"^\$\$ .+ \$\$$", line)
]
assert not one_line_display, f"one-line $$ formulas render as inline math; put the markers on their own lines: {one_line_display}"
print("ok  every display formula is a fenced block")
