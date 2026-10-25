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


def mcginley(close, n=14, k=0.6):
    values = close.to_numpy(dtype=float)
    out = np.empty(len(values))
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = out[i - 1] + (values[i] - out[i - 1]) / (k * n * (values[i] / out[i - 1]) ** 4)
    return pd.Series(out, index=close.index)


def envelope(close, n=20, percent=2.5):
    middle = close.rolling(n).mean()
    return middle, middle * (1 + percent / 100), middle * (1 - percent / 100)


def linreg(close, n=20):
    x = np.arange(n)
    centered = x - x.mean()
    slope = close.rolling(n).apply(lambda y: (centered * (y - y.mean())).sum() / (centered ** 2).sum(), raw=True)
    value = close.rolling(n).mean() + slope * (n - 1 - x.mean())
    return value, slope


def supertrend(high, low, close, n=10, k=3):
    mid = (high + low) / 2
    width = k * atr(high, low, close, n)
    basic_up, basic_down = (mid - width).to_numpy(), (mid + width).to_numpy()
    c = close.to_numpy(dtype=float)
    up, down, line = basic_up.copy(), basic_down.copy(), np.empty(len(c))
    trend = 1
    line[0] = up[0]
    for i in range(1, len(c)):
        if c[i - 1] > up[i - 1]:
            up[i] = max(basic_up[i], up[i - 1])
        if c[i - 1] < down[i - 1]:
            down[i] = min(basic_down[i], down[i - 1])
        if trend == -1 and c[i] > down[i - 1]:
            trend = 1
        elif trend == 1 and c[i] < up[i - 1]:
            trend = -1
        line[i] = up[i] if trend == 1 else down[i]
    return pd.Series(line, index=close.index)


def vortex(high, low, close, n=14):
    prev_close = close.shift()
    true_range = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    plus = (high - low.shift()).abs()
    minus = (low - high.shift()).abs()
    total = true_range.rolling(n).sum()
    return plus.rolling(n).sum() / total, minus.rolling(n).sum() / total


def stoch_rsi(close, n=14, smooth_k=3, smooth_d=3):
    r = rsi(close, n)
    low, high = r.rolling(n).min(), r.rolling(n).max()
    raw = 100 * (r - low) / (high - low).replace(0, np.nan)
    k = raw.rolling(smooth_k).mean()
    return k, k.rolling(smooth_d).mean()


def smi(high, low, close, n=10, smooth1=3, smooth2=3, signal=10):
    highest, lowest = high.rolling(n).max(), low.rolling(n).min()
    offset = close - (highest + lowest) / 2
    span = highest - lowest

    def twice(x):
        return x.ewm(span=smooth1, adjust=False).mean().ewm(span=smooth2, adjust=False).mean()

    line = 100 * twice(offset) / (twice(span) / 2)
    return line, line.ewm(span=signal, adjust=False).mean()


def tsi(close, long=25, short=13, signal=7):
    change = close.diff()

    def twice(x):
        return x.ewm(span=long, adjust=False).mean().ewm(span=short, adjust=False).mean()

    line = 100 * twice(change) / twice(change.abs())
    return line, line.ewm(span=signal, adjust=False).mean()


def kst(close, signal=9):
    parts = [(10, 10, 1), (15, 10, 2), (20, 10, 3), (30, 15, 4)]
    line = sum(w * (100 * (close / close.shift(r) - 1)).rolling(s).mean() for r, s, w in parts)
    return line, line.rolling(signal).mean()


def dpo(close, n=20):
    return close.shift(n // 2 + 1) - close.rolling(n).mean()


def coppock(close, long_roc=14, short_roc=11, wma_n=10):
    total = 100 * (close / close.shift(long_roc) - 1) + 100 * (close / close.shift(short_roc) - 1)
    weights = np.arange(1, wma_n + 1)
    return total.rolling(wma_n).apply(lambda w: (w * weights).sum() / weights.sum(), raw=True)


def fisher(high, low, n=10):
    mid = (high + low) / 2
    highest, lowest = mid.rolling(n).max(), mid.rolling(n).min()
    position = 2 * ((mid - lowest) / (highest - lowest).replace(0, np.nan) - 0.5)
    value, line = 0.0, 0.0
    out = []
    for x in position:
        if np.isnan(x):
            out.append(np.nan)
            continue
        value = max(-0.999, min(0.999, 0.33 * x + 0.67 * value))
        line = 0.5 * np.log((1 + value) / (1 - value)) + 0.5 * line
        out.append(line)
    out = pd.Series(out, index=mid.index)
    return out, out.shift(1)


def rmi(close, n=14, momentum=5):
    delta = close.diff(momentum)
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + avg_gain / avg_loss)


def elder_ray(high, low, close, n=13):
    trend = close.ewm(span=n, adjust=False).mean()
    return high - trend, low - trend


def connors_rsi(close, rsi_n=3, streak_n=2, rank_n=100):
    streak = [0.0]
    for change in close.diff().iloc[1:]:
        if change > 0:
            streak.append(streak[-1] + 1 if streak[-1] > 0 else 1.0)
        elif change < 0:
            streak.append(streak[-1] - 1 if streak[-1] < 0 else -1.0)
        else:
            streak.append(0.0)
    streak = pd.Series(streak, index=close.index)
    daily = close.pct_change()
    rank = daily.rolling(rank_n + 1).apply(lambda w: 100 * (w[:-1] < w[-1]).mean(), raw=True)
    return (rsi(close, rsi_n) + rsi(streak, streak_n) + rank) / 3


def historical_volatility(close, n=20, periods_per_year=252):
    returns = np.log(close / close.shift())
    return 100 * returns.rolling(n).std(ddof=1) * np.sqrt(periods_per_year)


def std_dev(close, n=20):
    return close.rolling(n).std(ddof=0)


def chaikin_volatility(high, low, n=10, change=10):
    smoothed = (high - low).ewm(span=n, adjust=False).mean()
    return 100 * (smoothed / smoothed.shift(change) - 1)


def relative_volatility(close, std_n=10, n=14):
    sd = close.rolling(std_n).std(ddof=0)
    change = close.diff()
    up = sd.where(change > 0, 0.0).where(sd.notna())
    down = sd.where(change < 0, 0.0).where(sd.notna())
    avg_up = up.ewm(alpha=1 / n, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / n, adjust=False).mean()
    return 100 * avg_up / (avg_up + avg_down)


def mass_index(high, low, n=9, total=25):
    spread = (high - low).ewm(span=n, adjust=False).mean()
    ratio = spread / spread.ewm(span=n, adjust=False).mean()
    return ratio.rolling(total).sum()
