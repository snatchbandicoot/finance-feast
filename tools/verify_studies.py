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
