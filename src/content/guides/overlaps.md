---
title: Which studies do you actually need?
summary: Many studies measure nearly the same thing. This guide shows which ones overlap, how strongly, and what is worth keeping on a chart.
status: draft
---

> **In plain English.** Technical studies are built from a small set of ingredients: price changes, moving averages, the high-to-low range, and volume. So many of them end up measuring the same thing in a different costume. Putting two near-identical studies on a chart does not give you two confirmations. It gives you the same evidence twice. This page maps the overlaps so you can keep what adds something and drop what does not.
>
> **How it was checked:** every overlap below is tested by the site's own check script. Each one is either an exact mathematical identity or a measured correlation on the site's sample data.

## How strong is an overlap?

- **Same measurement.** An exact mathematical relationship: one study can be computed from the other with a fixed formula, on any data. For example, Williams %R is the stochastic's raw reading minus 100.
- **Nearly the same.** Not an exact identity, but the two lines move together almost perfectly: a correlation of at least 0.95 on the sample data.
- **Partly overlaps.** Related ideas that still carry some separate information: a correlation from 0.6 up to 0.95, or a shared exact event.

A high correlation means two lines rise and fall together. It does not guarantee they give the same *signals* at the moments that matter. The correlations come from this site's synthetic sample data, so read them as direction: 0.98 means "nearly the same line" and 0.7 means "related but different". Exact identities do not depend on the data.

## The families

### Momentum from moving averages: MACD and its relatives

[MACD](../studies/macd/), [Percentage Price Oscillator](../studies/percentage-price-oscillator/), [Awesome Oscillator](../studies/awesome-oscillator/), [TRIX](../studies/trix/) and [Rate of Change](../studies/rate-of-change/).

- The Percentage Price Oscillator is MACD on a percentage scale (the same measurement, exactly).
- The Awesome Oscillator is nearly the same line as MACD (correlation 0.98).
- TRIX is the same idea, smoother and later (0.93).
- Rate of Change is related but compares only two prices (0.71).

**What to keep (my view):** one of them. MACD is the most widely used, so it is the easiest to compare with other people's charts. Use the Percentage Price Oscillator instead if you compare instruments or the price level changes a lot.

### Bounded oscillators: RSI and its relatives

[Relative Strength Index](../studies/relative-strength-index/), [Stochastic Oscillator](../studies/stochastic-oscillator/), [Williams %R](../studies/williams-percent-r/), [Chande Momentum Oscillator](../studies/chande-momentum-oscillator/), [Ultimate Oscillator](../studies/ultimate-oscillator/) and [Commodity Channel Index](../studies/commodity-channel-index/).

- Williams %R is the stochastic's raw reading minus 100 (the same measurement).
- The Chande Momentum Oscillator is RSI's unsmoothed form on a different scale (the same measurement as Cutler's RSI, and a correlation of 0.85 with the standard RSI).
- The stochastic and RSI overlap partly (0.81), as do the Ultimate Oscillator and RSI (0.81) and the Commodity Channel Index and RSI (0.82).

**What to keep (my view):** RSI. If you want a second view, the stochastic measures something different (where the close sits in the range, not the balance of gains and losses). The others add little, unless one specific feature matters to you, such as the Ultimate Oscillator counting gaps.

### Bands and channels

[Bollinger Bands](../studies/bollinger-bands/), [Keltner Channels](../studies/keltner-channels/), [Donchian Channels](../studies/donchian-channels/) and [Average True Range](../studies/average-true-range/).

- The Commodity Channel Index is nearly the same as Bollinger %B (0.98), and so is redundant if you use Bollinger Bands.
- Keltner and Bollinger widths are related but different (0.68). Keltner's is steadier.
- Donchian is a different kind of envelope, built from the extremes and not from volatility.
- Average True Range is the ingredient that sets Keltner's width, and it is a different tool: it measures bar size and is mainly used for stops and position size.

**What to keep (my view):** Bollinger Bands or Keltner Channels, not both, plus Average True Range for stops and sizing. Add Donchian if you want clear breakout levels.

### Trend lines and trend filters

[Simple Moving Average](../studies/simple-moving-average/), [Exponential Moving Average](../studies/exponential-moving-average/), [Ichimoku Cloud](../studies/ichimoku-cloud/), [Parabolic SAR](../studies/parabolic-sar/), [Average Directional Index](../studies/average-directional-index/) and [Aroon](../studies/aroon/).

- Same-length simple and exponential averages are nearly the same (0.98, measured on distance from price).
- Aroon at 100 is exactly the same event as a Donchian breakout.
- Three of Ichimoku's lines are exactly Donchian middle lines.
- **ADX and Aroon do *not* overlap much.** Their correlation is only 0.20, because they answer different questions: ADX says how strong a trend is, and Aroon says how recently it made a new extreme. Together they carry more than either alone.

**What to keep (my view):** one moving average (they are close enough that the choice matters little), and ADX if you want a measure of trend strength. Parabolic SAR is worth considering only as a trailing stop.

### Volume

[On-Balance Volume](../studies/on-balance-volume/), [Chaikin Money Flow](../studies/chaikin-money-flow/) and [Volume Weighted Average Price](../studies/volume-weighted-average-price/).

- Chaikin Money Flow and On-Balance Volume overlap partly (0.84). This is likely overstated, because the sample's volume and bar shapes were generated from the same price moves.
- VWAP is a different tool: a price reference and not a flow of volume.

**What to keep (my view):** one of On-Balance Volume or Chaikin Money Flow, if the instrument has reliable volume. VWAP is for intraday use.

### Moving averages and their cousins

[Simple Moving Average](../studies/simple-moving-average/), [Exponential Moving Average](../studies/exponential-moving-average/), [Weighted Moving Average](../studies/weighted-moving-average/), [Double Exponential Moving Average](../studies/double-exponential-moving-average/), [Triple Exponential Moving Average](../studies/triple-exponential-moving-average/), [Hull Moving Average](../studies/hull-moving-average/), [Kaufman Adaptive Moving Average](../studies/kaufman-adaptive-moving-average/), [McGinley Dynamic](../studies/mcginley-dynamic/), [Linear Regression](../studies/linear-regression/) and [Moving Average Envelope](../studies/moving-average-envelope/).

- The McGinley Dynamic is nearly an EMA (0.99, measured on distance from price). The Weighted Moving Average is close to both the SMA (0.97) and the EMA (0.96).
- The Double and Triple Exponential Moving Averages and the Hull Moving Average cut lag by extrapolating. That makes them genuinely different from an EMA (the DEMA correlates only 0.68 with it), but the difference is in lag and overshoot and not in information.
- The Kaufman Adaptive Moving Average changes speed with how directional the market is, and correlates 0.78 with an EMA.
- Linear Regression fits a line instead of averaging, and its distance from price correlates only 0.34 with the SMA's.
- The Moving Average Envelope is a fixed-percentage channel and overlaps partly with Bollinger Bands (0.82).

**What to keep (my view):** one average. If lag bothers you, try a Hull or a Double Exponential average, and check the overshoot on the page before you trust it.

### More momentum: smoothed changes and range oscillators

- The True Strength Index is nearly the same line as MACD (0.98), and the Know Sure Thing nearly so (0.95). The Know Sure Thing and the True Strength Index overlap partly (0.94).
- The Coppock Curve is a smoothed momentum line that overlaps partly with Rate of Change (0.86).
- The Stochastic RSI overlaps partly with the Stochastic (0.82) and much less with RSI (0.55). The Stochastic Momentum Index overlaps partly with the Stochastic (0.90), and the Fisher Transform less so (0.75).
- The Relative Momentum Index is exactly RSI when its step is 1 bar, and correlates 0.90 with RSI at its usual step of 5. Connors RSI correlates 0.85 with a 3-bar RSI, which is one third of it.
- The Money Flow Index is a volume-weighted RSI, and correlates 0.73 with RSI. The Relative Volatility Index is built like RSI and correlates 0.83 with it, though its name suggests it measures volatility.
- Momentum is the Rate of Change in points instead of percent (0.997 with it), and the Disparity Index is the distance from an EMA in percent (0.997 with that distance).
- The Schaff Trend Cycle is a stochastic of MACD: it overlaps partly with the Stochastic (0.84) and only a little with MACD itself (0.38). The Double Smoothed Stochastic overlaps partly with the Stochastic too (0.77), and the Price Zone Oscillator with RSI (0.73).
- Woodie's CCI is the ordinary CCI (14 bars, exactly) plus a faster 6-bar line.
- The Detrended Price Oscillator is a different kind of tool: it removes the trend to show cycles, and is not for timing.

**What to keep (my view):** nothing new. RSI and MACD still cover this ground. Pick a relative only if one specific feature matters to you, such as the Stochastic RSI's sensitivity.

### Volatility and trendiness

[Average True Range](../studies/average-true-range/), [Historical Volatility](../studies/historical-volatility/), [Standard Deviation](../studies/standard-deviation/), [Chaikin Volatility](../studies/chaikin-volatility/), [Ulcer Index](../studies/ulcer-index/), [Mass Index](../studies/mass-index/) and [Choppiness Index](../studies/choppiness-index/).

- Historical Volatility correlates 0.87 with ATR. It is the same idea in percent, which is what lets you compare instruments.
- Standard Deviation is exactly a quarter of the distance between the upper and lower Bollinger Bands. It also mixes trend into its reading, and correlates only 0.63 with ATR.
- Chaikin Volatility is the change in the smoothed range. Its swings correlate 0.90 with the 10-bar change in ATR.
- The Ulcer Index counts only falls from a peak, and correlates 0.74 with Historical Volatility.
- The Choppiness Index runs opposite to ADX (a correlation of -0.58): high means choppy, where ADX high means trending.
- The Mass Index measures something unusual (range widening), and is the one study here with almost no relatives.

**What to keep (my view):** ATR for stops, and Historical Volatility if you compare instruments or size positions by risk.

### More volume studies

- Chaikin Money Flow is exactly the 20-bar change in the Accumulation/Distribution Line divided by the 20-bar volume. The Chaikin Oscillator is exactly the MACD line of the Accumulation/Distribution Line.
- The Volume Oscillator is exactly the Percentage Price Oscillator applied to volume. Anchored VWAP is exactly VWAP when anchored at the start of a session.
- The Accumulation/Distribution Line and On-Balance Volume overlap partly (0.84), and the Chaikin Oscillator and Chaikin Money Flow also (0.71).
- The Price Volume Trend is nearly just price momentum: its 20-bar change correlates 0.98 with a 20-bar Rate of Change. Ease of Movement correlates 0.90 with a 12-bar Rate of Change, and the Force Index 0.87.
- The Negative and Positive Volume Index split each day's price change between them: multiplied together, they give the price index exactly.

**What to keep (my view):** the same one volume study as before. Most of the others add a layer to the same ingredients.

### Levels and chart styles

[Pivot Points](../studies/pivot-points/), [Volume Profile](../studies/volume-profile/), [Anchored VWAP](../studies/anchored-vwap/) and [Heikin-Ashi](../studies/heikin-ashi/) are not oscillators, and do not overlap with the studies above. Pivot Points come from the last period's range, a Volume Profile from where volume traded, and an Anchored VWAP from the volume since a chosen event. Heikin-Ashi is a way of drawing the same bars.

## A minimal kit (opinion)

If you wanted the fewest studies that still cover the ground:

1. **One trend line**: a simple or exponential moving average.
2. **One momentum oscillator**: RSI.
3. **One volatility measure**: Average True Range, for stops and sizing.
4. **One envelope**: Bollinger Bands.
5. **One volume reading**, if volume is reliable for your instrument: Chaikin Money Flow or On-Balance Volume.
6. **Optionally ADX**, as a filter for whether trend-following tools are likely to work.

That is a judgment, not a finding. It is a reasonable default that avoids paying twice for the same information. Read each study's own page for when it earns a place beyond the default.

## When overlap is not a reason to drop a study

- **Different units.** The Percentage Price Oscillator is the same information as MACD, but the percentage scale is what lets you compare instruments.
- **Different smoothing.** The raw stochastic and the slow stochastic differ in how jumpy they are, which matters if you use crossovers.
- **Workflow.** If a display or color convention helps you read a chart faster, that is a legitimate reason to prefer one near-identical study.
- **Cross-checking, but not confirming.** A near-identical study can catch a charting mistake, because the two should agree. But two studies that agree are not two independent signals.
