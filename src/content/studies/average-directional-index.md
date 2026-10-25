---
title: Average Directional Index
aliases: [ADX, DMI, Directional Movement Index, "+DI", "-DI", Wilder's ADX]
category: trend
summary: A gauge of how strongly price is trending, without saying which way, with two companion lines for direction.
display: panel
inputs:
  - { name: length, default: 14 }
verdict: situational
status: draft
related: [average-true-range, macd, parabolic-sar, simple-moving-average]
---

> **In plain English.** ADX scores how strongly price has been trending, from near 0 to somewhere around 60, and says nothing about direction. A high ADX means movement has been consistently one-sided. A low ADX means price has been drifting or churning sideways. Two companion lines, +DI and −DI, show whether the upward or the downward movement has been stronger.
>
> **Good for:** telling a trending market from a sideways one, so you can decide which other tools to trust.
>
> **Watch out for:** lag. It confirms a trend after much of the move has happened. Also, a high ADX in a falling market is as "strong" as one in a rising market.

## What it measures

How one-sided recent price movement has been. For each bar, it asks how far the high and low pushed beyond the previous bar's. Pushes up and pushes down are tracked separately, smoothed, and compared against the typical size of a bar. The result is two lines (+DI for upward movement, −DI for downward) and a third, ADX, that measures the gap between them relative to their total.

A big gap between +DI and −DI, in either direction, means movement has been lopsided, which is what a trend looks like. A small gap means up and down movement have been about equal, which is what a sideways market looks like.

## Calculation

Compare each bar with the one before. The up move is $H_t - H_{t-1}$ and the down move is $L_{t-1} - L_t$. The directional movement of the bar is whichever is larger, if it is positive, and zero otherwise:

$$ +DM_t = \begin{cases} H_t - H_{t-1} & \text{if it is larger than } L_{t-1} - L_t \text{ and positive} \\ 0 & \text{otherwise} \end{cases} $$

and $-DM_t$ is the mirror image. Let $TR$ be the true range from the [Average True Range](../average-true-range/) page. Smooth each series with Wilder's method (an exponential average with $\alpha = 1/N$), written $\overline{\cdot}$:

$$ +DI = 100 \cdot \frac{\overline{+DM}}{\overline{TR}} \qquad -DI = 100 \cdot \frac{\overline{-DM}}{\overline{TR}} $$

$$ DX = 100 \cdot \frac{\lvert +DI - (-DI) \rvert}{+DI + (-DI)} \qquad ADX = \overline{DX} $$

**Worked example.** One bar makes a high of 12 after a previous high of 11, and a low of 10 after a previous low of 9.5. The up move is $12 - 11 = 1$ and the down move is $9.5 - 10 = -0.5$, so $+DM = 1$ and $-DM = 0$.

If, after smoothing, $+DI = 30$ and $-DI = 10$, then $DX = 100 \times 20/40 = 50$. ADX is a smoothed average of such DX values.

```python
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
```

ADX smooths twice (first the three series, then DX), so it takes longer to settle than most studies. On test data the version above agreed with Wilder's textbook seeding to within 0.001 after about 250 bars. Treat the first 40 or more values of any ADX as unreliable.

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/average-directional-index-dark.svg">
<img src="../../charts/average-directional-index-light.svg" alt="Price above, and ADX with +DI and -DI below with a line at 25" width="840" height="590">
</picture>
<figcaption>Synthetic data. The first 40 values are hidden while the averages warm up. ADX (pink) averaged 17 in the range, where only 5% of bars were above 25, and peaked at 52.6, three bars after the price low. It first crossed 25 at bar 239, when price had already fallen 18% of the 27% it would fall in total. The +DI and -DI lines crossed 14 times in the 100-bar range against twice in the uptrend.</figcaption>
</figure>

- **Level of ADX.** Below about 20 is usually read as little or no trend, above 25 as a trend, and above 40 as a strong one. These are conventions and not laws.
- **Rising or falling ADX.** Rising means the trend is strengthening, in either direction. Falling means the movement is becoming less one-sided, which can be a trend fading or just a pause. A falling ADX from a high level is not by itself a reversal signal.
- **+DI against −DI.** When +DI is above −DI, upward movement has been stronger, and the reverse. Crossovers between them are the study's direction signal. In a sideways market they cross constantly.
- **ADX and price.** ADX often peaks near or after the end of the move's fastest stretch, not before it.

What it does not tell you: where price goes next, or how long a trend will last.

## Best used when

- You want a **filter** that tells you whether trend-following tools such as moving average crossovers are likely to be useful or are about to chop. A common rule is to ignore crossovers when ADX is below about 20. Whether that rule improves results is something to test, not assume.
- You need a rough sense of **trend strength** across several instruments.

## Avoid when

- You want **direction**. ADX alone cannot give it. Use +DI and −DI or another tool.
- You want an **early warning**. It is smoothed twice, so it confirms rather than anticipates.
- You treat a **single threshold** as a switch. A reading of 24 and a reading of 26 mean nearly the same thing.
- Price has just had **one huge bar**. A big gap or spike feeds into the directional movement and the true range, and its effect lingers for many bars.

## Settings and tuning

- **Length 14** is Wilder's default.
- **Shorter** (such as 7 or 10): faster and noisier, and it crosses the thresholds more often.
- **Longer** (such as 20 or 25): smoother and later.
- **Thresholds.** 20 and 25 are the usual lines. Moving them to fit past charts is a common way to fool yourself.

## Implementation variations

- **Smoothing.** Wilder's smoothing is standard. Some tools use a simple or standard exponential average instead, which changes every value.
- **Seeding.** Early values depend on how the averages are started. Tools can disagree for the first 100 bars or more.
- **Naming.** "DMI" and "ADX" are used loosely. Sometimes DMI means the +DI and −DI pair, and sometimes the whole set.
- **Extra lines.** Some platforms add ADXR (a smoothed ADX) or plot DX. Those are different studies.

## Is it useful?

**Situational.** It answers a real and useful question, namely whether the market is trending or not, and few simple studies do. But it is a lagging answer: in this study's sample the selloff had already cost 18% before ADX confirmed a trend, out of 27% in total. It is best as a background filter, not a trigger. It also overlaps in purpose with price-and-moving-average readings of trend, so if you already judge trend by eye, it will mostly confirm what you see, a little late.

## Pairs well with / See also

- [Average True Range](../average-true-range/): ADX is built on the same true range and the same Wilder smoothing.
- [MACD](../macd/): a different way of reading trend, based on moving averages. MACD says more about direction and ADX more about strength.
- [Parabolic SAR](../parabolic-sar/): a trailing-stop study that works in trends. ADX can tell you whether there is one.
- [Simple Moving Average](../simple-moving-average/): the lines whose crossovers ADX is often used to filter.
