"""The indicator code shown on the study pages, in one place.

tools/verify_studies.py checks these against independent loop implementations, and
tools/make_charts.py draws the example charts with them, so a page's snippet, its
verification, and its chart all use the same code. If you change a function here,
change the snippet on its study page to match.
"""
import numpy as np
import pandas as pd


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


def stochastic(high, low, close, n=14, smooth_k=3, smooth_d=3):
    lowest = low.rolling(n).min()
    highest = high.rolling(n).max()
    raw_k = 100 * (close - lowest) / (highest - lowest)
    k = raw_k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return raw_k, k, d


def vwap(high, low, close, volume, session):
    typical = (high + low + close) / 3
    cum_pv = (typical * volume).groupby(session).cumsum()
    cum_v = volume.groupby(session).cumsum()
    return cum_pv / cum_v


def obv(close, volume):
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


def roc(close, n=12):
    return 100 * (close / close.shift(n) - 1)


def williams_r(high, low, close, n=14):
    highest = high.rolling(n).max()
    lowest = low.rolling(n).min()
    return -100 * (highest - close) / (highest - lowest)


def cci(high, low, close, n=20):
    typical = (high + low + close) / 3
    mean = typical.rolling(n).mean()
    mean_dev = typical.rolling(n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (typical - mean) / (0.015 * mean_dev)


def adx(high, low, close, n=14):
    up = high.diff()
    down = -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    prev_close = close.shift()
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)

    def smooth(s):
        return s.ewm(alpha=1 / n, adjust=False).mean()

    plus_di = 100 * smooth(plus_dm) / smooth(tr)
    minus_di = 100 * smooth(minus_dm) / smooth(tr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return smooth(dx), plus_di, minus_di


def psar(high, low, step=0.02, step_max=0.2):
    h, l = high.to_numpy(), low.to_numpy()
    n = len(h)
    sar = np.empty(n)
    uptrend = h[1] >= h[0]
    ep = h[0] if uptrend else l[0]
    sar[0] = l[0] if uptrend else h[0]
    af = step
    for i in range(1, n):
        sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
        if uptrend:
            sar[i] = min(sar[i], l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < sar[i]:
                uptrend, sar[i], ep, af = False, ep, l[i], step
            elif h[i] > ep:
                ep, af = h[i], min(af + step, step_max)
        else:
            sar[i] = max(sar[i], h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > sar[i]:
                uptrend, sar[i], ep, af = True, ep, h[i], step
            elif l[i] < ep:
                ep, af = l[i], min(af + step, step_max)
    return pd.Series(sar, index=high.index)


def aroon(high, low, n=25):
    up = high.rolling(n + 1).apply(lambda w: 100 * (n - np.argmax(w[::-1])) / n, raw=True)
    down = low.rolling(n + 1).apply(lambda w: 100 * (n - np.argmin(w[::-1])) / n, raw=True)
    return up, down, up - down


def donchian(high, low, n=20):
    upper = high.rolling(n).max()
    lower = low.rolling(n).min()
    return upper, (upper + lower) / 2, lower


def keltner(high, low, close, n=20, atr_n=10, k=2):
    mid = close.ewm(span=n, adjust=False).mean()
    width = k * atr(high, low, close, atr_n)
    return mid, mid + width, mid - width


def cmf(high, low, close, volume, n=20):
    spread = (high - low).replace(0, np.nan)
    multiplier = (((close - low) - (high - close)) / spread).fillna(0)
    flow = multiplier * volume
    return flow.rolling(n).sum() / volume.rolling(n).sum()


def ichimoku(high, low, close, conversion=9, base=26, span_b=52, shift=26):
    def midpoint(n):
        return (high.rolling(n).max() + low.rolling(n).min()) / 2

    tenkan = midpoint(conversion)
    kijun = midpoint(base)
    senkou_a = (tenkan + kijun) / 2
    senkou_b = midpoint(span_b)
    # Each series is labelled with the bar it is drawn at: the cloud `shift` bars ahead, the lagging span behind.
    senkou_a.index = senkou_a.index + shift
    senkou_b.index = senkou_b.index + shift
    chikou = close.copy()
    chikou.index = chikou.index - shift
    return tenkan, kijun, senkou_a, senkou_b, chikou


def awesome(high, low, fast=5, slow=34):
    median = (high + low) / 2
    return median.rolling(fast).mean() - median.rolling(slow).mean()


def trix(close, n=15):
    triple = close.ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean().ewm(span=n, adjust=False).mean()
    return 100 * (triple / triple.shift(1) - 1)


def ultimate(high, low, close, short=7, mid=14, long=28):
    prev_close = close.shift()
    low_ref = pd.concat([low, prev_close], axis=1).min(axis=1)
    high_ref = pd.concat([high, prev_close], axis=1).max(axis=1)
    buying = close - low_ref
    true_range = high_ref - low_ref

    def average(n):
        return buying.rolling(n).sum() / true_range.rolling(n).sum()

    return 100 * (4 * average(short) + 2 * average(mid) + average(long)) / 7


def cmo(close, n=14):
    change = close.diff()
    up = change.clip(lower=0).rolling(n).sum()
    down = (-change).clip(lower=0).rolling(n).sum()
    return 100 * (up - down) / (up + down)


def ppo(close, fast=12, slow=26, signal=9):
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    line = 100 * (close.ewm(span=fast, adjust=False).mean() - slow_ema) / slow_ema
    sig = line.ewm(span=signal, adjust=False).mean()
    return line, sig, line - sig


def wma(close, n=20):
    weights = np.arange(1, n + 1)
    return close.rolling(n).apply(lambda w: np.dot(w, weights) / weights.sum(), raw=True)


def dema(close, n=20):
    first = close.ewm(span=n, adjust=False).mean()
    second = first.ewm(span=n, adjust=False).mean()
    return 2 * first - second


def tema(close, n=20):
    first = close.ewm(span=n, adjust=False).mean()
    second = first.ewm(span=n, adjust=False).mean()
    third = second.ewm(span=n, adjust=False).mean()
    return 3 * first - 3 * second + third


def hma(close, n=21):
    half = n // 2
    root = round(n ** 0.5)
    return wma(2 * wma(close, half) - wma(close, n), root)


def kama(close, n=10, fast=2, slow=30):
    change = (close - close.shift(n)).abs()
    path = close.diff().abs().rolling(n).sum()
    efficiency = (change / path.replace(0, np.nan)).fillna(0)
    fast_sc, slow_sc = 2 / (fast + 1), 2 / (slow + 1)
    smoothing = (efficiency * (fast_sc - slow_sc) + slow_sc) ** 2
    values = close.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    out[n] = values[n]
    for i in range(n + 1, len(values)):
        out[i] = out[i - 1] + smoothing.iloc[i] * (values[i] - out[i - 1])
    return pd.Series(out, index=close.index)
