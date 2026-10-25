"""Draws the example chart for each study page, in light and dark variants.

Run: python3 tools/make_charts.py     (needs pandas, numpy, matplotlib)
Reads data/sample_daily.csv and data/sample_intraday.csv, which are SYNTHETIC (see
tools/make_sample_data.py). Writes public/charts/<study-slug>-light.svg and -dark.svg.

Indicators come from tools/indicators.py, the same code the study pages show and
tools/verify_studies.py checks. The site build does not run this script; the SVGs are committed.
"""
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

import indicators as ind
import palette

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "charts"

# Series colors come from tools/palette.py (pink first, then teal, gold, blue), validated in both modes.
THEMES = {
    "light": dict(surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#8a8984", grid="#e6e5e1",
                  band="#f3f2ee", **{k: palette.LIGHT[k] for k in ("pink", "teal", "gold", "blue")}),
    "dark": dict(surface="#1a1a19", ink="#f0efec", ink2="#c3c2b7", muted="#8b8a84", grid="#2e2e2c",
                 band="#222221", **{k: palette.DARK[k] for k in ("pink", "teal", "gold", "blue")}),
}

plt.rcParams.update({
    "svg.fonttype": "path",          # text as outlines: identical look on every machine
    "svg.hashsalt": "finance-feast",  # stable ids, so re-running gives identical files
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.linewidth": 0,
})

LINE = 1.5   # about 2px
PRICE = 1.1  # the price line is the backdrop, so it is slightly thinner

daily = pd.read_csv(ROOT / "data" / "sample_daily.csv", index_col=0)
intraday = pd.read_csv(ROOT / "data" / "sample_intraday.csv", index_col=0)
H, L, C, V = daily["high"], daily["low"], daily["close"], daily["volume"]


def regimes():
    """(name, first bar, last bar) for each regime of the daily data."""
    out, start = [], 0
    names = daily["regime"].tolist()
    for i in range(1, len(names) + 1):
        if i == len(names) or names[i] != names[start]:
            out.append((names[start], start, i - 1))
            start = i
    return out


def new_fig(t, ratios, height, top=None):
    fig = plt.figure(figsize=(8.4, height), facecolor=t["surface"])
    gs = fig.add_gridspec(len(ratios), 1, height_ratios=ratios, hspace=0.42, left=0.07, right=0.985,
                          top=top or (0.90 if len(ratios) == 1 else 0.87), bottom=0.085)
    axes = [fig.add_subplot(gs[i]) for i in range(len(ratios))]
    for ax in axes:
        ax.set_facecolor(t["surface"])
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color=t["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, colors=t["ink2"], labelsize=8.5)
    return fig, axes


def heading(fig, t, text):
    fig.text(0.07, 0.965, text, color=t["ink"], fontsize=11.5, fontweight="bold", va="top", ha="left")


def panel_label(ax, t, text):
    ax.text(0, 1.04, text, transform=ax.transAxes, color=t["ink2"], fontsize=9, va="bottom", ha="left")


def legend(ax, t, handles, labels, left=False):
    leg = ax.legend(handles, labels, loc="lower left" if left else "lower right",
                    bbox_to_anchor=(0.0, 1.0) if left else (1.0, 1.0), ncol=len(labels),
                    frameon=False, fontsize=8.5, handlelength=1.6, columnspacing=1.4)
    for txt in leg.get_texts():
        txt.set_color(t["ink2"])


def shade_regimes(ax, t, lo=None, hi=None, labels=True, xlim=None):
    lo = lo if lo is not None else 0
    hi = hi if hi is not None else len(daily) - 1
    for k, (name, a, b) in enumerate(regimes()):
        if k % 2 == 1:
            ax.axvspan(max(a, lo) - 0.5, min(b, hi) + 0.5, color=t["band"], linewidth=0, zorder=0)
    if labels:
        for name, a, b in regimes():
            a2, b2 = max(a, lo), min(b, hi)
            if b2 - a2 >= 14:
                ax.text((a2 + b2) / 2, 0.97, name.capitalize(), transform=ax.get_xaxis_transform(),
                        color=t["muted"], fontsize=8.5, ha="center", va="top")


def x_axis(ax, t, lo=0, hi=None, label="Bar (synthetic daily data)"):
    hi = hi if hi is not None else len(daily) - 1
    ax.set_xlim(lo - 0.5, hi + 0.5)
    ax.set_xticks([x for x in range(0, len(daily), 50) if lo <= x <= hi])
    ax.set_xlabel(label, color=t["muted"], fontsize=8.5, labelpad=6)


def price_panel(ax, t, lo=0, hi=None, label="Close"):
    hi = hi if hi is not None else len(daily) - 1
    ax.plot(C.index, C, color=t["ink2"], linewidth=PRICE, solid_capstyle="round", label=label, zorder=3)
    seg = C.loc[lo:hi]
    pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)  # headroom for the regime labels
    shade_regimes(ax, t, lo, hi)
    x_axis(ax, t, lo, hi)


def hide_x(ax):
    ax.tick_params(labelbottom=False)
    ax.set_xlabel("")


def warm(series, n):
    """Hide the first n values. Recursive averages start from a seed, so the pages tell readers to
    distrust the first few dozen values; the charts do not draw them."""
    out = series.copy().astype(float)
    out.iloc[:n] = np.nan
    return out


def hline(ax, t, y, lw=0.8):
    ax.axhline(y, color=t["muted"], linewidth=lw, zorder=1)


def save(fig, slug, mode):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{slug}-{mode}.svg", format="svg", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)


# ---- one function per chart ----------------------------------------------------------
def chart_sma(t):
    fig, (ax,) = new_fig(t, [1], 4.3)
    heading(fig, t, "Simple moving averages on synthetic daily data")
    price_panel(ax, t)
    ax.plot(ind.sma(C, 20), color=t["pink"], linewidth=LINE, label="SMA 20", zorder=4)
    ax.plot(ind.sma(C, 100), color=t["teal"], linewidth=LINE, label="SMA 100", zorder=4)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, h, l)
    return fig


def chart_ema(t):
    lo = 170
    fig, (ax,) = new_fig(t, [1], 4.3)
    heading(fig, t, "EMA 20 versus SMA 20 through a turn")
    price_panel(ax, t, lo)
    ax.plot(ind.ema(C, 20), color=t["pink"], linewidth=LINE, label="EMA 20", zorder=4)
    ax.plot(ind.sma(C, 20), color=t["teal"], linewidth=LINE, label="SMA 20", zorder=4)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, h, l)
    return fig


def chart_rsi(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "RSI (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    r = warm(ind.rsi(C, 14), 30)
    for y in (30, 70):
        hline(ax2, t, y)
    ax2.plot(r, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 30, 50, 70, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "RSI (14), with the 30 and 70 lines")
    return fig


def chart_stochastic(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Slow stochastic (14, 3, 3) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    _, k, d = ind.stochastic(H, L, C)
    for y in (20, 80):
        hline(ax2, t, y)
    ax2.plot(k, color=t["pink"], linewidth=LINE, label="%K", zorder=4)
    ax2.plot(d, color=t["teal"], linewidth=LINE, label="%D", zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 20, 50, 80, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Stochastic, with the 20 and 80 lines")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_macd(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "MACD (12, 26, 9) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    line, sig, hist = (warm(x, 40) for x in ind.macd(C))
    hline(ax2, t, 0)
    ax2.bar(hist.index, hist, width=0.8, color=t["ink2"], alpha=0.35, linewidth=0, label="Histogram", zorder=2)
    ax2.plot(line, color=t["pink"], linewidth=LINE, label="MACD", zorder=4)
    ax2.plot(sig, color=t["teal"], linewidth=LINE, label="Signal", zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "MACD, signal line and histogram")
    h, l = ax2.get_legend_handles_labels()
    by_label = dict(zip(l, h))
    legend(ax2, t, [by_label[k] for k in ("MACD", "Signal", "Histogram")], ["MACD", "Signal", "Histogram"])
    return fig


def chart_bollinger(t):
    fig, (ax,) = new_fig(t, [1], 4.3)
    heading(fig, t, "Bollinger Bands (20, 2) on synthetic daily data")
    price_panel(ax, t)
    mid, up, lo_ = ind.bollinger(C, 20, 2)
    pad = (up.max() - lo_.min()) * 0.06
    ax.set_ylim(lo_.min() - pad, up.max() + pad * 3.2)
    ax.fill_between(C.index, lo_, up, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(up, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(lo_, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(mid, color=t["pink"], linewidth=LINE, label="SMA 20", zorder=4)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], Patch(facecolor=t["pink"], alpha=0.25, linewidth=0)] , [l[0], "Bands: 2 standard deviations"])
    return fig


def chart_atr(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Average True Range (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    a = warm(ind.atr(H, L, C, 14), 30)
    ax2.plot(a, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, a.max() * 1.12)  # a.max() ignores the hidden warm-up values
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "ATR (14), in price units")
    return fig


def chart_obv(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "On-Balance Volume on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    o = ind.obv(C, V) / 1e6
    ax2.plot(o, color=t["pink"], linewidth=LINE, zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "OBV, in millions of shares (the level is arbitrary; watch the shape)")
    return fig


def chart_vwap(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.1], 5.4)
    heading(fig, t, "VWAP restarts every session")
    s = intraday["session"]
    v = ind.vwap(intraday["high"], intraday["low"], intraday["close"], intraday["volume"], s)
    n = len(intraday)
    ax.plot(intraday["close"], color=t["ink2"], linewidth=PRICE, label="Close", zorder=3)
    for sess in sorted(s.unique()):
        idx = intraday.index[s == sess]
        ax.plot(v.loc[idx], color=t["pink"], linewidth=LINE, label="VWAP" if sess == 0 else None, zorder=4)
        ax.text((idx[0] + idx[-1]) / 2, 0.97, f"Session {sess + 1}", transform=ax.get_xaxis_transform(),
                color=t["muted"], fontsize=8.5, ha="center", va="top")
        if sess:
            for a_ in (ax, ax2):
                a_.axvline(idx[0] - 0.5, color=t["muted"], linewidth=0.8, zorder=1)
    lo, hi = intraday["close"].min(), intraday["close"].max()
    pad = (hi - lo) * 0.08
    ax.set_ylim(lo - pad, hi + pad * 3.2)
    h, l = ax.get_legend_handles_labels(); legend(ax, t, h, l)
    ax.tick_params(labelbottom=False)
    ax2.bar(intraday.index, intraday["volume"] / 1000, width=0.8, color=t["ink2"], alpha=0.35, linewidth=0, zorder=2)
    for a_ in (ax, ax2):
        a_.set_xlim(-0.5, n - 0.5)
    ax2.set_xticks([0, 78, 156]); ax2.set_xlabel("Bar (synthetic 5-minute data)", color=t["muted"], fontsize=8.5, labelpad=6)
    panel_label(ax2, t, "Volume, in thousands of shares")
    return fig


def chart_adx(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "ADX (14) with +DI and -DI on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    a, pdi, mdi = (warm(x, 40) for x in ind.adx(H, L, C, 14))
    hline(ax2, t, 25)
    ax2.plot(pdi, color=t["teal"], linewidth=LINE, label="+DI", zorder=4)
    ax2.plot(mdi, color=t["blue"], linewidth=LINE, label="-DI", zorder=4)
    ax2.plot(a, color=t["pink"], linewidth=LINE + 0.3, label="ADX", zorder=5)
    ax2.set_ylim(0, 60); ax2.set_yticks([0, 25, 50])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "ADX, +DI and -DI, with the 25 line")
    h, l = ax2.get_legend_handles_labels()
    by_label = dict(zip(l, h))
    legend(ax2, t, [by_label[k] for k in ("ADX", "+DI", "-DI")], ["ADX", "+DI", "-DI"])
    return fig


def chart_psar(t):
    fig, (ax,) = new_fig(t, [1], 4.3)
    heading(fig, t, "Parabolic SAR (0.02, 0.2) on synthetic daily data")
    price_panel(ax, t)
    sar = ind.psar(H, L)
    # Dots are 3.5px, smaller than the 8px marker spec, because 320 bars share about 700px.
    ax.plot(sar, linestyle="none", marker="o", markersize=2.6, markeredgewidth=0, color=t["pink"], label="Parabolic SAR", zorder=4)
    seg = pd.concat([C, sar])
    pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, h, l)
    return fig


def chart_cci(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Commodity Channel Index (20) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    c = ind.cci(H, L, C, 20)
    for y in (-100, 100):
        hline(ax2, t, y)
    ax2.plot(c, color=t["pink"], linewidth=LINE, zorder=4)
    lim = max(abs(c.min()), abs(c.max())) * 1.08
    ax2.set_ylim(-lim, lim); ax2.set_yticks([-200, -100, 0, 100, 200])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "CCI (20), with the +100 and -100 lines")
    return fig


def chart_williams(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Williams %R (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    w = ind.williams_r(H, L, C, 14)
    for y in (-20, -80):
        hline(ax2, t, y)
    ax2.plot(w, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(-100, 0); ax2.set_yticks([-100, -80, -50, -20, 0])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Williams %R (14), with the -20 and -80 lines")
    return fig


def chart_roc(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Rate of Change (12) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    r = ind.roc(C, 12)
    hline(ax2, t, 0)
    ax2.plot(r, color=t["pink"], linewidth=LINE, zorder=4)
    lim = max(abs(r.min()), abs(r.max())) * 1.08
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "ROC (12), percent change over 12 bars")
    return fig


def chart_aroon(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Aroon (25) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    up, down, _ = ind.aroon(H, L, 25)
    for y in (30, 70):
        hline(ax2, t, y)
    ax2.plot(up, color=t["pink"], linewidth=LINE, label="Aroon Up", zorder=4)
    ax2.plot(down, color=t["teal"], linewidth=LINE, label="Aroon Down", zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 30, 50, 70, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Aroon Up and Aroon Down, with the 30 and 70 lines")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_donchian(t):
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "Donchian Channels (20) on synthetic daily data")
    price_panel(ax, t)
    upper, mid, lower = ind.donchian(H, L, 20)
    ax.fill_between(C.index, lower, upper, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(upper, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(lower, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(mid, color=t["pink"], linewidth=LINE, label="Middle", zorder=4)
    pad = (upper.max() - lower.min()) * 0.06
    ax.set_ylim(lower.min() - pad, upper.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], h[1], Patch(facecolor=t["pink"], alpha=0.25, linewidth=0)], [l[0], l[1], "20-bar highest high and lowest low"], left=True)
    return fig


def chart_keltner(t):
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "Keltner Channels and Bollinger Bands on synthetic daily data")
    price_panel(ax, t)
    km, ku, kl = (warm(x, 40) for x in ind.keltner(H, L, C, 20, 10, 2))
    bm, bu, bl = ind.bollinger(C, 20, 2)
    ax.fill_between(C.index, kl, ku, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(ku, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(kl, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(km, color=t["pink"], linewidth=LINE, zorder=4)
    ax.plot(bu, color=t["teal"], linewidth=1.3, zorder=5)
    ax.plot(bl, color=t["teal"], linewidth=1.3, zorder=5)
    lo_, hi_ = min(kl.min(), bl.min()), max(ku.max(), bu.max())
    pad = (hi_ - lo_) * 0.06
    ax.set_ylim(lo_ - pad, hi_ + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    from matplotlib.lines import Line2D
    legend(ax, t, [h[0], Patch(facecolor=t["pink"], alpha=0.25, linewidth=0), Line2D([], [], color=t["teal"], linewidth=1.3)],
           [l[0], "Keltner (EMA 20, 2 x ATR 10)", "Bollinger (20, 2)"], left=True)
    return fig


def chart_cmf(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Chaikin Money Flow (20) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    c = ind.cmf(H, L, C, V, 20)
    hline(ax2, t, 0)
    ax2.plot(c, color=t["pink"], linewidth=LINE, zorder=4)
    lim = max(abs(c.min()), abs(c.max())) * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "CMF (20), from -1 to +1")
    return fig


def chart_ichimoku(t):
    from matplotlib.lines import Line2D
    ahead = 26
    fig, (ax,) = new_fig(t, [1], 4.8, top=0.85)
    heading(fig, t, "Ichimoku (9, 26, 52) on synthetic daily data")
    price_panel(ax, t, 0, len(daily) - 1 + ahead)
    tenkan, kijun, a, b, _ = ind.ichimoku(H, L, C)
    both = pd.concat([a, b], axis=1).dropna()
    ax.fill_between(both.index, both.iloc[:, 0], both.iloc[:, 1], color=t["blue"], alpha=0.14, linewidth=0, zorder=2)
    ax.plot(a, color=t["blue"], linewidth=0.9, zorder=3)
    ax.plot(b, color=t["blue"], linewidth=0.9, zorder=3)
    ax.plot(kijun, color=t["teal"], linewidth=LINE, label="Kijun (26)", zorder=4)
    ax.plot(tenkan, color=t["pink"], linewidth=LINE, label="Tenkan (9)", zorder=5)
    ax.axvline(len(daily) - 0.5, color=t["muted"], linewidth=0.8, zorder=1)
    ax.text(len(daily) + 1, 0.04, "projected\ncloud", transform=ax.get_xaxis_transform(), color=t["muted"], fontsize=7.5, va="bottom", ha="left")
    lo_ = min(C.min(), both.min().min()); hi_ = max(C.max(), both.max().max())
    pad = (hi_ - lo_) * 0.06
    ax.set_ylim(lo_ - pad, hi_ + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], h[2], h[1], Patch(facecolor=t["blue"], alpha=0.3, linewidth=0)], [l[0], l[2], l[1], "Cloud (Senkou A and B)"], left=True)
    return fig


def chart_awesome(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Awesome Oscillator (5, 34) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    a = ind.awesome(H, L, 5, 34)
    rising = a.diff() >= 0
    hline(ax2, t, 0)
    ax2.bar(a.index[rising], a[rising], width=0.8, color=t["pink"], linewidth=0, label="Higher than the previous bar", zorder=3)
    ax2.bar(a.index[~rising], a[~rising], width=0.8, color=t["teal"], linewidth=0, label="Lower than the previous bar", zorder=3)
    lim = a.abs().max() * 1.08
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Awesome Oscillator, in price units")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_trix(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "TRIX (15) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.trix(C, 15), 60)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "TRIX (15), percent change of the triple-smoothed average per bar")
    return fig


def chart_ultimate(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Ultimate Oscillator (7, 14, 28) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    u = ind.ultimate(H, L, C, 7, 14, 28)
    for y in (30, 70):
        hline(ax2, t, y)
    ax2.plot(u, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 30, 50, 70, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Ultimate Oscillator, with the 30 and 70 lines")
    return fig


def chart_cmo(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Chande Momentum Oscillator (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    c = ind.cmo(C, 14)
    for y in (-50, 50):
        hline(ax2, t, y)
    hline(ax2, t, 0, 0.5)
    ax2.plot(c, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(-100, 100); ax2.set_yticks([-100, -50, 0, 50, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "CMO (14), with the -50 and +50 lines")
    return fig


def chart_ppo(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Percentage Price Oscillator (12, 26, 9) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    line, sig, hist = (warm(x, 40) for x in ind.ppo(C))
    hline(ax2, t, 0)
    ax2.bar(hist.index, hist, width=0.8, color=t["ink2"], alpha=0.35, linewidth=0, label="Histogram", zorder=2)
    ax2.plot(line, color=t["pink"], linewidth=LINE, label="PPO", zorder=4)
    ax2.plot(sig, color=t["teal"], linewidth=LINE, label="Signal", zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "PPO, signal line and histogram, in percent")
    h, l = ax2.get_legend_handles_labels()
    by_label = dict(zip(l, h))
    legend(ax2, t, [by_label[k] for k in ("PPO", "Signal", "Histogram")], ["PPO", "Signal", "Histogram"])
    return fig


def _ma_versus(t, heading_text, main, main_label, ref, ref_label, lo=170):
    """A moving average (pink) against a reference average (teal), over price. lo zooms to a turn."""
    fig, (ax,) = new_fig(t, [1], 4.3)
    heading(fig, t, heading_text)
    price_panel(ax, t, lo)
    ax.plot(main, color=t["pink"], linewidth=LINE, label=main_label, zorder=4)
    ax.plot(ref, color=t["teal"], linewidth=LINE, label=ref_label, zorder=4)
    seg = pd.concat([C.loc[lo:], main.loc[lo:], ref.loc[lo:]])
    pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, h, l)
    return fig


def chart_wma(t):
    return _ma_versus(t, "WMA 20 versus SMA 20 through a turn", ind.wma(C, 20), "WMA 20", ind.sma(C, 20), "SMA 20")


def chart_dema(t):
    return _ma_versus(t, "DEMA 20 versus EMA 20 through a turn", ind.dema(C, 20), "DEMA 20", ind.ema(C, 20), "EMA 20")


def chart_tema(t):
    return _ma_versus(t, "TEMA 20 versus EMA 20 through a turn", ind.tema(C, 20), "TEMA 20", ind.ema(C, 20), "EMA 20")


def chart_hma(t):
    return _ma_versus(t, "HMA 21 versus WMA 21 through a turn", ind.hma(C, 21), "HMA 21", ind.wma(C, 21), "WMA 21")


def chart_kama(t):
    return _ma_versus(t, "KAMA versus EMA 20 on synthetic daily data", ind.kama(C), "KAMA", ind.ema(C, 20), "EMA 20", lo=0)


def chart_mcginley(t):
    return _ma_versus(t, "McGinley Dynamic versus EMA 14 through a turn", ind.mcginley(C), "McGinley (14)", ind.ema(C, 14), "EMA 14")


def chart_envelope(t):
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "Moving Average Envelope (20, 2.5%) and Bollinger Bands on synthetic daily data")
    price_panel(ax, t)
    m, u, lo_ = ind.envelope(C, 20, 2.5)
    bm, bu, bl = ind.bollinger(C, 20, 2)
    ax.fill_between(C.index, lo_, u, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(u, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(lo_, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(m, color=t["pink"], linewidth=LINE, zorder=4)
    ax.plot(bu, color=t["teal"], linewidth=1.3, zorder=5)
    ax.plot(bl, color=t["teal"], linewidth=1.3, zorder=5)
    lo2, hi2 = min(lo_.min(), bl.min()), max(u.max(), bu.max())
    pad = (hi2 - lo2) * 0.06
    ax.set_ylim(lo2 - pad, hi2 + pad * 3.2)
    from matplotlib.lines import Line2D
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], Patch(facecolor=t["pink"], alpha=0.25, linewidth=0), Line2D([], [], color=t["teal"], linewidth=1.3)],
           [l[0], "Envelope (SMA 20, 2.5% each side)", "Bollinger (20, 2)"], left=True)
    return fig


def chart_linreg(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Linear Regression (20) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    v, slope = ind.linreg(C, 20)
    ax.plot(v, color=t["pink"], linewidth=LINE, label="Linear regression 20", zorder=4)
    ax.plot(ind.sma(C, 20), color=t["teal"], linewidth=LINE, label="SMA 20", zorder=4)
    seg = pd.concat([C, v])
    pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels(); legend(ax, t, [h[0], h[1], h[2]], [l[0], l[1], l[2]])
    hline(ax2, t, 0)
    ax2.plot(slope, color=t["pink"], linewidth=LINE, zorder=4)
    lim = slope.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Slope of the fitted line, in price units per bar")
    return fig


def chart_supertrend(t):
    from matplotlib.lines import Line2D
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "Supertrend (10, 3) on synthetic daily data")
    price_panel(ax, t)
    st = ind.supertrend(H, L, C, 10, 3)
    long = C > st
    ax.plot(st.where(long), color=t["pink"], linewidth=LINE, zorder=4)
    ax.plot(st.where(~long), color=t["teal"], linewidth=LINE, zorder=4)
    seg = pd.concat([C, st]); pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], Line2D([], [], color=t["pink"], linewidth=LINE), Line2D([], [], color=t["teal"], linewidth=LINE)],
           [l[0], "Supertrend, below price (long)", "Supertrend, above price (short)"], left=True)
    return fig


def chart_vortex(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Vortex Indicator (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    vp, vm = ind.vortex(H, L, C, 14)
    hline(ax2, t, 1.0)
    ax2.plot(vp, color=t["pink"], linewidth=LINE, label="VI+", zorder=4)
    ax2.plot(vm, color=t["teal"], linewidth=LINE, label="VI-", zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Vortex lines VI+ and VI-, with the 1.0 line")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def _osc_two(t, title, line, sig, line_label, sig_label, panel_text, levels=(0,), ylim=None, yticks=None, warm_bars=60):
    """Price on top, an oscillator line (pink) and its signal line (teal) below, with reference levels."""
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, title)
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    line, sig = warm(line, warm_bars), warm(sig, warm_bars)
    for y in levels:
        hline(ax2, t, y)
    ax2.plot(line, color=t["pink"], linewidth=LINE, label=line_label, zorder=4)
    ax2.plot(sig, color=t["teal"], linewidth=LINE, label=sig_label, zorder=4)
    if ylim is None:
        lim = line.abs().max() * 1.1
        ylim = (-lim, lim)
    ax2.set_ylim(*ylim)
    if yticks:
        ax2.set_yticks(yticks)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, panel_text)
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_stoch_rsi(t):
    k, d = ind.stoch_rsi(C)
    return _osc_two(t, "Stochastic RSI (14, 3, 3) on synthetic daily data", k, d, "%K", "%D",
                    "Stochastic RSI, with the 20 and 80 lines", levels=(20, 80), ylim=(0, 100), yticks=[0, 20, 50, 80, 100])


def chart_smi(t):
    line, sig = ind.smi(H, L, C)
    return _osc_two(t, "Stochastic Momentum Index (10, 3, 3) on synthetic daily data", line, sig, "SMI", "Signal (10-bar EMA)",
                    "Stochastic Momentum Index, with the -40, 0 and +40 lines", levels=(-40, 0, 40), ylim=(-100, 100), yticks=[-100, -40, 0, 40, 100])


def chart_tsi(t):
    line, sig = ind.tsi(C)
    return _osc_two(t, "True Strength Index (25, 13, 7) on synthetic daily data", line, sig, "TSI", "Signal (7-bar EMA)",
                    "True Strength Index, with the zero line")


def chart_kst(t):
    line, sig = ind.kst(C)
    return _osc_two(t, "Know Sure Thing (default settings) on synthetic daily data", line, sig, "KST", "Signal (9-bar average)",
                    "Know Sure Thing, with the zero line")


def chart_dpo(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Detrended Price Oscillator (20) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    ax.plot(ind.sma(C, 20), color=t["teal"], linewidth=LINE, label="SMA 20", zorder=4)
    h, l = ax.get_legend_handles_labels(); legend(ax, t, h, l)
    x = warm(ind.dpo(C, 20), 60)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "DPO (20): the close 11 bars ago minus today's SMA 20, in price units")
    return fig


def chart_coppock(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Coppock Curve (14, 11, 10) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.coppock(C), 60)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Coppock Curve, with the zero line")
    return fig


def chart_fisher(t):
    line, sig = ind.fisher(H, L)
    return _osc_two(t, "Fisher Transform (10) on synthetic daily data", line, sig, "Fisher", "Trigger (previous bar)",
                    "Fisher Transform, with the -2, 0 and +2 lines", levels=(-2, 0, 2))


def chart_rmi(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Relative Momentum Index (14, 5) and RSI (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    for y in (30, 70):
        hline(ax2, t, y)
    ax2.plot(warm(ind.rsi(C, 14), 60), color=t["teal"], linewidth=LINE, label="RSI 14", zorder=4)
    ax2.plot(warm(ind.rmi(C, 14, 5), 60), color=t["pink"], linewidth=LINE, label="RMI (14, 5)", zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 30, 50, 70, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "RMI and RSI, with the 30 and 70 lines")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["RMI (14, 5)"], by["RSI 14"]], ["RMI (14, 5)", "RSI 14"])
    return fig


def chart_elder(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Elder Ray (13) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    ax.plot(ind.ema(C, 13), color=t["teal"], linewidth=LINE, label="EMA 13", zorder=4)
    h, l = ax.get_legend_handles_labels(); legend(ax, t, h, l)
    bull, bear = ind.elder_ray(H, L, C, 13)
    hline(ax2, t, 0)
    ax2.bar(bull.index, warm(bull, 30), width=0.8, color=t["pink"], linewidth=0, label="Bull Power (high - EMA)", zorder=3)
    ax2.bar(bear.index, warm(bear, 30), width=0.8, color=t["teal"], linewidth=0, label="Bear Power (low - EMA)", zorder=3)
    lim = max(bull.iloc[30:].abs().max(), bear.iloc[30:].abs().max()) * 1.08
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Bull Power and Bear Power, in price units")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_connors(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Connors RSI (3, 2, 100) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    for y in (10, 90):
        hline(ax2, t, y)
    ax2.plot(ind.connors_rsi(C), color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 10, 50, 90, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Connors RSI, with the 10 and 90 lines (needs 101 bars before its first value)")
    return fig


def chart_hv(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Historical Volatility (20, annualized) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.historical_volatility(C, 20), 30)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, x.max() * 1.12)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Historical volatility, in percent per year")
    return fig


def chart_stddev(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Standard Deviation (20) and ATR (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    sd, at = warm(ind.std_dev(C, 20), 30), warm(ind.atr(H, L, C, 14), 30)
    ax2.plot(sd, color=t["pink"], linewidth=LINE, label="Standard deviation of price (20)", zorder=4)
    ax2.plot(at, color=t["teal"], linewidth=LINE, label="ATR (14)", zorder=4)
    ax2.set_ylim(0, max(sd.max(), at.max()) * 1.12)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Both in price units")
    h, l = ax2.get_legend_handles_labels(); legend(ax2, t, h, l)
    return fig


def chart_chaikin_vol(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Chaikin Volatility (10, 10) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.chaikin_volatility(H, L, 10, 10), 30)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Chaikin Volatility, percent change in the smoothed daily range over 10 bars")
    return fig


def chart_rvi(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Relative Volatility Index (10, 14) and RSI (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    hline(ax2, t, 50)
    ax2.plot(warm(ind.rsi(C, 14), 60), color=t["teal"], linewidth=LINE, label="RSI 14", zorder=4)
    ax2.plot(warm(ind.relative_volatility(C), 60), color=t["pink"], linewidth=LINE, label="RVI (10, 14)", zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 30, 50, 70, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "RVI and RSI, with the 50 line")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["RVI (10, 14)"], by["RSI 14"]], ["RVI (10, 14)", "RSI 14"])
    return fig


def chart_mass(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Mass Index (9, 25) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.mass_index(H, L), 60)
    for y in (26.5, 27):
        hline(ax2, t, y)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(22, 28); ax2.set_yticks([22, 24, 25, 26.5, 27, 28])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Mass Index, with the 26.5 and 27 lines")
    return fig


def chart_choppiness(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Choppiness Index (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    for y in (38.2, 61.8):
        hline(ax2, t, y)
    ax2.plot(warm(ind.choppiness(H, L, C, 14), 30), color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 38.2, 50, 61.8, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Choppiness Index, with the 38.2 and 61.8 lines")
    return fig


def chart_ulcer(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Ulcer Index (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.ulcer(C, 14), 30)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, x.max() * 1.12)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Ulcer Index, in percent drawdown")
    return fig


def _candles(ax, t, o, h, l, c, lo, hi):
    idx = list(range(lo, hi + 1))
    for i in idx:
        up = c.iloc[i] >= o.iloc[i]
        col = t["teal"] if up else t["pink"]
        ax.vlines(i, l.iloc[i], h.iloc[i], color=col, linewidth=0.9, zorder=3)
        ax.bar(i, max(abs(c.iloc[i] - o.iloc[i]), 0.02), bottom=min(o.iloc[i], c.iloc[i]), width=0.7, color=col, linewidth=0, zorder=4)


def chart_heikin(t):
    O = daily["open"]
    lo, hi = 190, 290
    ho, hh, hl, hc = ind.heikin_ashi(O, H, L, C)
    fig, (ax, ax2) = new_fig(t, [1, 1], 6.4)
    heading(fig, t, "Ordinary and Heikin-Ashi candles, bars 190 to 290 of synthetic daily data")
    _candles(ax, t, O, H, L, C, lo, hi)
    _candles(ax2, t, ho, hh, hl, hc, lo, hi)
    lim = (min(L.loc[lo:hi].min(), hl.loc[lo:hi].min()) - 1, max(H.loc[lo:hi].max(), hh.loc[lo:hi].max()) + 1)
    for a_ in (ax, ax2):
        a_.set_ylim(*lim); shade_regimes(a_, t, lo, hi, labels=False)
    ax.set_xlim(lo - 1, hi + 1); hide_x(ax)
    x_axis(ax2, t, lo, hi)
    panel_label(ax, t, "Ordinary candles (teal: close at or above open, pink: below)")
    panel_label(ax2, t, "Heikin-Ashi candles of the same bars")
    return fig


def chart_pivots(t):
    fig, (ax,) = new_fig(t, [1], 4.6, top=0.85)
    heading(fig, t, "Pivot Points from the previous session, on synthetic 5-minute data")
    s = intraday["session"]
    ax.plot(intraday["close"], color=t["ink2"], linewidth=PRICE, label="Close", zorder=3)
    colors = {"P": t["pink"], "R1": t["teal"], "R2": t["teal"], "S1": t["blue"], "S2": t["blue"]}
    for sess in (1, 2):
        prev = intraday[s == sess - 1]
        lv = ind.pivot_points(prev["high"].max(), prev["low"].min(), prev["close"].iloc[-1])
        idx = intraday.index[s == sess]
        for name, y in zip(["P", "R1", "S1", "R2", "S2"], lv):
            ax.hlines(y, idx[0], idx[-1], color=colors[name], linewidth=1.5 if name == "P" else 1.1,
                      linestyle="-" if name in ("P", "R1", "S1") else (0, (4, 3)), zorder=4)
            if sess == 1:
                ax.text(idx[0] + 2, y, name, color=colors[name], fontsize=8, va="bottom", ha="left")
        ax.axvline(idx[0] - 0.5, color=t["muted"], linewidth=0.8, zorder=1)
    ax.set_xlim(-0.5, len(intraday) - 0.5)
    levels = []
    for sess in (1, 2):
        prev = intraday[s == sess - 1]
        levels += list(ind.pivot_points(prev["high"].max(), prev["low"].min(), prev["close"].iloc[-1]))
    lo_, hi_ = min(intraday["low"].min(), min(levels)), max(intraday["high"].max(), max(levels))
    pad = (hi_ - lo_) * 0.08
    ax.set_ylim(lo_ - pad, hi_ + pad)
    ax.set_xticks([0, 78, 156]); ax.set_xlabel("Bar (synthetic 5-minute data)", color=t["muted"], fontsize=8.5, labelpad=6)
    from matplotlib.lines import Line2D
    legend(ax, t, [Line2D([], [], color=t["ink2"], linewidth=PRICE), Line2D([], [], color=t["pink"], linewidth=1.5),
                   Line2D([], [], color=t["teal"], linewidth=1.1), Line2D([], [], color=t["blue"], linewidth=1.1)],
           ["Close", "Pivot", "Resistance R1, R2", "Support S1, S2"], left=True)
    return fig


def chart_avwap(t):
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "Anchored VWAP from two anchors, on synthetic daily data")
    price_panel(ax, t, 170)
    a1 = ind.anchored_vwap(H, L, C, V, 200)
    a2 = ind.anchored_vwap(H, L, C, V, 249)
    ax.plot(a1, color=t["pink"], linewidth=LINE, label="Anchored at bar 200 (selloff starts)", zorder=4)
    ax.plot(a2, color=t["teal"], linewidth=LINE, label="Anchored at bar 249 (price low)", zorder=4)
    for a_, c_ in ((200, t["pink"]), (249, t["teal"])):
        ax.plot([a_], [C.iloc[a_]], marker="o", markersize=5, color=c_, zorder=5)
    h, l = ax.get_legend_handles_labels(); legend(ax, t, h, l, left=True)
    return fig


def chart_adl(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Accumulation/Distribution line and On-Balance Volume on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    ad = ind.accumulation_distribution(H, L, C, V) / 1e6
    ob = ind.obv(C, V) / 1e6
    ax2.plot(ob, color=t["teal"], linewidth=LINE, label="OBV", zorder=4)
    ax2.plot(ad, color=t["pink"], linewidth=LINE, label="Accumulation/Distribution", zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Both in millions of shares, each starting from zero")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["Accumulation/Distribution"], by["OBV"]], ["Accumulation/Distribution", "OBV"])
    return fig


def chart_chaikin_osc(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Chaikin Oscillator (3, 10) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.chaikin_oscillator(H, L, C, V), 30) / 1e6
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Chaikin Oscillator, in millions of shares")
    return fig


def chart_mfi(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Money Flow Index (14) and RSI (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    for y in (20, 80):
        hline(ax2, t, y)
    ax2.plot(warm(ind.rsi(C, 14), 30), color=t["teal"], linewidth=LINE, label="RSI 14", zorder=4)
    ax2.plot(ind.mfi(H, L, C, V, 14), color=t["pink"], linewidth=LINE, label="MFI 14", zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 20, 50, 80, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "MFI and RSI, with the 20 and 80 lines")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["MFI 14"], by["RSI 14"]], ["MFI 14", "RSI 14"])
    return fig


def chart_force(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Force Index (13) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.force_index(C, V, 13), 30) / 1e6
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Force Index (13), in millions of price-times-share units")
    return fig


def chart_emv(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Ease of Movement (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.ease_of_movement(H, L, V, 14), 30)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Ease of Movement (14), with volume scaled to millions")
    return fig


def chart_klinger(t):
    line, sig = ind.klinger(H, L, C, V)
    return _osc_two(t, "Klinger Oscillator (34, 55, 13) on synthetic daily data", line / 1e6, sig / 1e6, "Klinger", "Signal (13-bar EMA)",
                    "Klinger Oscillator, in millions", warm_bars=60)


def chart_volume_osc(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Volume Oscillator (5, 10) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.volume_oscillator(V, 5, 10), 30)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    lim = x.abs().max() * 1.1
    ax2.set_ylim(-lim, lim)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Volume Oscillator, percent difference between a 5-bar and a 10-bar average of volume")
    return fig


def _volume_index(t, title, series, label):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, title)
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    ax2.plot(1000 * C / C.iloc[0], color=t["ink2"], linewidth=PRICE, label="Price index (close, starting at 1000)", zorder=3)
    ax2.plot(series, color=t["pink"], linewidth=LINE, label=label, zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Index, starting at 1000")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by[label], by["Price index (close, starting at 1000)"]], [label, "Price index (close, starting at 1000)"])
    return fig


def chart_nvi(t):
    return _volume_index(t, "Negative Volume Index on synthetic daily data", ind.negative_volume_index(C, V), "Negative Volume Index")


def chart_pvi(t):
    return _volume_index(t, "Positive Volume Index on synthetic daily data", ind.positive_volume_index(C, V), "Positive Volume Index")


def chart_pvt(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Price Volume Trend on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    ax2.plot(ind.price_volume_trend(C, V) / 1e3, color=t["pink"], linewidth=LINE, zorder=4)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Price Volume Trend, in thousands of shares")
    return fig


def chart_bmp(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Balance of Market Power (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(ind.balance_of_market_power(daily["open"], H, L, C, 14), 30)
    hline(ax2, t, 0)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(-0.6, 0.6)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Balance of Market Power, from -1 (sellers) to +1 (buyers)")
    return fig


def chart_volume_profile(t):
    fig = plt.figure(figsize=(8.4, 4.8), facecolor=t["surface"])
    gs = fig.add_gridspec(1, 2, width_ratios=[3.2, 1], wspace=0.04, left=0.07, right=0.985, top=0.83, bottom=0.10)
    ax, axh = fig.add_subplot(gs[0]), fig.add_subplot(gs[1], sharey=None)
    for a_ in (ax, axh):
        a_.set_facecolor(t["surface"])
        for side in ("top", "right", "left", "bottom"):
            a_.spines[side].set_visible(False)
        a_.grid(axis="y", color=t["grid"], linewidth=0.8); a_.set_axisbelow(True)
        a_.tick_params(length=0, colors=t["ink2"], labelsize=8.5)
    heading(fig, t, "Volume Profile (24 price bins, 70% value area) on synthetic daily data")
    profile, poc, val, vah = ind.volume_profile(H, L, C, V, 24, 0.7)
    lo_, hi_ = L.min(), H.max()
    pad = (hi_ - lo_) * 0.04
    ax.plot(C.index, C, color=t["ink2"], linewidth=PRICE, label="Close", zorder=3)
    ax.axhspan(val, vah, color=t["teal"], alpha=0.10, linewidth=0, zorder=1)
    ax.axhline(poc, color=t["pink"], linewidth=LINE, zorder=4)
    ax.set_ylim(lo_ - pad, hi_ + pad); ax.set_xlim(-0.5, len(C) - 0.5)
    x_axis(ax, t)
    width = (hi_ - lo_) / 24
    inside = (profile.index > val) & (profile.index < vah)
    axh.barh(profile.index, profile / 1e6, height=width * 0.9, color=t["ink2"], alpha=0.35, linewidth=0, zorder=2)
    axh.barh(profile.index[inside], profile[inside] / 1e6, height=width * 0.9, color=t["teal"], alpha=0.6, linewidth=0, zorder=3)
    axh.barh([poc], [profile.loc[poc] / 1e6], height=width * 0.9, color=t["pink"], linewidth=0, zorder=4)
    axh.set_ylim(lo_ - pad, hi_ + pad); axh.tick_params(labelleft=False)
    axh.set_xlabel("Volume in bin (millions)", color=t["muted"], fontsize=8.5, labelpad=6)
    from matplotlib.lines import Line2D
    legend(ax, t, [Line2D([], [], color=t["ink2"], linewidth=PRICE), Line2D([], [], color=t["pink"], linewidth=LINE),
                   Patch(facecolor=t["teal"], alpha=0.35, linewidth=0)],
           ["Close", "Point of control", "Value area (70% of volume)"], left=True)
    return fig


def _single_panel(t, title, series, panel_text, levels=(0,), ylim=None, yticks=None, warm_bars=60):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, title)
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    x = warm(series, warm_bars)
    for y in levels:
        hline(ax2, t, y)
    ax2.plot(x, color=t["pink"], linewidth=LINE, zorder=4)
    if ylim is None:
        lim = x.abs().max() * 1.1
        ylim = (-lim, lim)
    ax2.set_ylim(*ylim)
    if yticks:
        ax2.set_yticks(yticks)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, panel_text)
    return fig


def chart_momentum(t):
    return _single_panel(t, "Momentum (10) on synthetic daily data", ind.momentum(C, 10), "Momentum (10), in price points, with the zero line", warm_bars=30)


def chart_disparity(t):
    return _single_panel(t, "Disparity Index (14) on synthetic daily data", ind.disparity_index(C, 14), "Disparity Index (14), percent from the 14-bar EMA", warm_bars=30)


def chart_pzo(t):
    return _single_panel(t, "Price Zone Oscillator (14) on synthetic daily data", ind.price_zone_oscillator(C, 14),
                         "Price Zone Oscillator (14), with lines at -40, 0 and +40", levels=(-40, 0, 40), warm_bars=30)


def chart_stc(t):
    return _single_panel(t, "Schaff Trend Cycle (10, 23, 50) on synthetic daily data", ind.schaff_trend_cycle(C),
                         "Schaff Trend Cycle, with the 25 and 75 lines", levels=(25, 75), ylim=(0, 100), yticks=[0, 25, 50, 75, 100], warm_bars=60)


def chart_woodie(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Woodie's CCI (14 and 6) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    main, turbo = ind.woodies_cci(H, L, C, 14, 6)
    for y in (-100, 0, 100):
        hline(ax2, t, y)
    ax2.plot(warm(turbo, 30), color=t["teal"], linewidth=1.2, label="Turbo CCI (6)", zorder=4)
    ax2.plot(warm(main, 30), color=t["pink"], linewidth=LINE, label="CCI (14)", zorder=5)
    ax2.set_ylim(-250, 250)
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Two CCI lines, with the -100, 0 and +100 lines")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["CCI (14)"], by["Turbo CCI (6)"]], ["CCI (14)", "Turbo CCI (6)"])
    return fig


def chart_dss(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Double Smoothed Stochastic (13, 8) and the Stochastic on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    for y in (20, 80):
        hline(ax2, t, y)
    ax2.plot(warm(ind.stochastic(H, L, C)[1], 60), color=t["teal"], linewidth=1.2, label="Stochastic %K (14, 3)", zorder=4)
    ax2.plot(warm(ind.double_smoothed_stochastic(H, L, C), 60), color=t["pink"], linewidth=LINE, label="Double Smoothed (13, 8)", zorder=5)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 20, 50, 80, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Both oscillators, with the 20 and 80 lines")
    h, l = ax2.get_legend_handles_labels()
    by = dict(zip(l, h)); legend(ax2, t, [by["Double Smoothed (13, 8)"], by["Stochastic %K (14, 3)"]], ["Double Smoothed (13, 8)", "Stochastic %K (14, 3)"])
    return fig


def chart_tma(t):
    return _ma_versus(t, "Triangular MA versus SMA, 20 bars", ind.triangular_ma(C, 20), "Triangular MA 20", ind.sma(C, 20), "SMA 20")


def chart_vidya(t):
    return _ma_versus(t, "Variable MA versus EMA 21", ind.variable_ma(C), "Variable MA (21, 9)", ind.ema(C, 21), "EMA 21")


def chart_displaced(t):
    return _ma_versus(t, "Displaced EMA versus plain EMA", ind.displaced_ema(C, 20, 5), "EMA 20 displaced 5 bars", ind.ema(C, 20), "EMA 20")


def chart_ribbon(t):
    fig, (ax,) = new_fig(t, [1], 4.6, top=0.85)
    heading(fig, t, "Moving Average Ribbon: eight EMAs from 10 to 80 bars on synthetic daily data")
    price_panel(ax, t)
    ribbon, width = ind.ema_ribbon(C)
    cols = list(ribbon.columns)
    for i, n in enumerate(cols):
        mix = i / (len(cols) - 1)
        ax.plot(ribbon[n], color=t["pink"] if i < len(cols) // 2 else t["teal"], linewidth=1.5 if i in (0, len(cols) - 1) else 0.9,
                alpha=1.0 if i in (0, len(cols) - 1) else 0.55, zorder=4)
    seg = pd.concat([C, ribbon[cols[0]], ribbon[cols[-1]]]); pad = (seg.max() - seg.min()) * 0.08
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    from matplotlib.lines import Line2D
    h, l = ax.get_legend_handles_labels()
    legend(ax, t, [h[0], Line2D([], [], color=t["pink"], linewidth=1.5), Line2D([], [], color=t["teal"], linewidth=1.5)],
           [l[0], "Faster EMAs (10 to 40)", "Slower EMAs (50 to 80)"], left=True)
    return fig


def chart_starc(t):
    fig, (ax,) = new_fig(t, [1], 4.4, top=0.85)
    heading(fig, t, "STARC Bands (6, 15, 2) on synthetic daily data")
    price_panel(ax, t)
    m, u, lo_ = ind.starc_bands(H, L, C)
    ax.fill_between(C.index, lo_, u, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(u, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(lo_, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(m, color=t["pink"], linewidth=LINE, label="6-bar SMA", zorder=4)
    seg = pd.concat([C, u, lo_]); pad = (seg.max() - seg.min()) * 0.06
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    h, l = ax.get_legend_handles_labels()
    from matplotlib.lines import Line2D
    legend(ax, t, [h[0], h[1], Patch(facecolor=t["pink"], alpha=0.25, linewidth=0)], [l[0], l[1], "6-bar SMA plus and minus 2 ATR (15)"], left=True)
    return fig


def chart_projection(t):
    fig, (ax, ax2) = new_fig(t, [3, 1.7], 5.9)
    heading(fig, t, "Projection Bands and Projection Oscillator (14) on synthetic daily data")
    price_panel(ax, t); hide_x(ax); panel_label(ax, t, "Close")
    pu, pl, po = ind.projection_bands(H, L, C, 14)
    ax.fill_between(C.index, pl, pu, color=t["pink"], alpha=0.10, linewidth=0, zorder=2)
    ax.plot(pu, color=t["pink"], linewidth=1.0, zorder=4)
    ax.plot(pl, color=t["pink"], linewidth=1.0, zorder=4)
    seg = pd.concat([C, pu, pl]); pad = (seg.max() - seg.min()) * 0.06
    ax.set_ylim(seg.min() - pad, seg.max() + pad * 3.2)
    for y in (20, 80):
        hline(ax2, t, y)
    ax2.plot(warm(po, 30), color=t["pink"], linewidth=LINE, zorder=4)
    ax2.set_ylim(0, 100); ax2.set_yticks([0, 20, 50, 80, 100])
    shade_regimes(ax2, t, labels=False); x_axis(ax2, t); panel_label(ax2, t, "Projection Oscillator: where the close sits between the bands, with the 20 and 80 lines")
    return fig


CHARTS = {
    "simple-moving-average": chart_sma,
    "exponential-moving-average": chart_ema,
    "relative-strength-index": chart_rsi,
    "stochastic-oscillator": chart_stochastic,
    "macd": chart_macd,
    "bollinger-bands": chart_bollinger,
    "average-true-range": chart_atr,
    "on-balance-volume": chart_obv,
    "volume-weighted-average-price": chart_vwap,
    "average-directional-index": chart_adx,
    "parabolic-sar": chart_psar,
    "commodity-channel-index": chart_cci,
    "williams-percent-r": chart_williams,
    "rate-of-change": chart_roc,
    "aroon": chart_aroon,
    "donchian-channels": chart_donchian,
    "keltner-channels": chart_keltner,
    "chaikin-money-flow": chart_cmf,
    "ichimoku-cloud": chart_ichimoku,
    "awesome-oscillator": chart_awesome,
    "trix": chart_trix,
    "ultimate-oscillator": chart_ultimate,
    "chande-momentum-oscillator": chart_cmo,
    "percentage-price-oscillator": chart_ppo,
    "weighted-moving-average": chart_wma,
    "double-exponential-moving-average": chart_dema,
    "triple-exponential-moving-average": chart_tema,
    "hull-moving-average": chart_hma,
    "kaufman-adaptive-moving-average": chart_kama,
    "mcginley-dynamic": chart_mcginley,
    "moving-average-envelope": chart_envelope,
    "linear-regression": chart_linreg,
    "supertrend": chart_supertrend,
    "vortex-indicator": chart_vortex,
    "stochastic-rsi": chart_stoch_rsi,
    "stochastic-momentum-index": chart_smi,
    "true-strength-index": chart_tsi,
    "know-sure-thing": chart_kst,
    "detrended-price-oscillator": chart_dpo,
    "coppock-curve": chart_coppock,
    "fisher-transform": chart_fisher,
    "relative-momentum-index": chart_rmi,
    "elder-ray": chart_elder,
    "connors-rsi": chart_connors,
    "historical-volatility": chart_hv,
    "standard-deviation": chart_stddev,
    "chaikin-volatility": chart_chaikin_vol,
    "relative-volatility-index": chart_rvi,
    "mass-index": chart_mass,
    "choppiness-index": chart_choppiness,
    "ulcer-index": chart_ulcer,
    "heikin-ashi": chart_heikin,
    "pivot-points": chart_pivots,
    "anchored-vwap": chart_avwap,
    "accumulation-distribution": chart_adl,
    "chaikin-oscillator": chart_chaikin_osc,
    "money-flow-index": chart_mfi,
    "force-index": chart_force,
    "ease-of-movement": chart_emv,
    "klinger-oscillator": chart_klinger,
    "volume-oscillator": chart_volume_osc,
    "negative-volume-index": chart_nvi,
    "positive-volume-index": chart_pvi,
    "price-volume-trend": chart_pvt,
    "balance-of-market-power": chart_bmp,
    "volume-profile": chart_volume_profile,
    "momentum": chart_momentum,
    "disparity-index": chart_disparity,
    "price-zone-oscillator": chart_pzo,
    "schaff-trend-cycle": chart_stc,
    "woodies-cci": chart_woodie,
    "double-smoothed-stochastic": chart_dss,
    "triangular-moving-average": chart_tma,
    "variable-moving-average": chart_vidya,
    "displaced-ema": chart_displaced,
    "moving-average-ribbon": chart_ribbon,
    "starc-bands": chart_starc,
    "projection-bands": chart_projection,
}

if __name__ == "__main__":
    for slug, fn in CHARTS.items():
        for mode, theme in THEMES.items():
            save(fn(theme), slug, mode)
        print("wrote", slug)
