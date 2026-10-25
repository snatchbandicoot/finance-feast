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


def new_fig(t, ratios, height):
    fig = plt.figure(figsize=(8.4, height), facecolor=t["surface"])
    gs = fig.add_gridspec(len(ratios), 1, height_ratios=ratios, hspace=0.42, left=0.07, right=0.985,
                          top=0.90 if len(ratios) == 1 else 0.87, bottom=0.085)
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


def legend(ax, t, handles, labels):
    leg = ax.legend(handles, labels, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=len(labels),
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
}

if __name__ == "__main__":
    for slug, fn in CHARTS.items():
        for mode, theme in THEMES.items():
            save(fn(theme), slug, mode)
        print("wrote", slug)
