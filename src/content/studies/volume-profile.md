---
title: Volume Profile
aliases: [Volume by Price, Price by Volume, Market Profile Volume, Point of Control, Value Area]
category: volume
summary: A histogram turned on its side, showing how much volume traded at each price level instead of at each point in time. The busiest level is the point of control, and the band holding most of the volume is the value area.
display: overlay
inputs:
  - { name: price bins, default: 24 }
  - { name: value area share, default: 0.7 }
verdict: situational
status: draft
related: [volume-weighted-average-price, anchored-vwap, pivot-points]
---

> **In plain English.** Most volume charts answer "how much traded on each day". A volume profile answers "how much traded at each price". Split the price range into bands, add up the volume that traded in each, and draw the totals sideways next to the chart. Long bars are prices where the market spent a lot of time and money. Short bars are prices it passed through quickly.
>
> **Good for:** finding the price levels that many traders have a stake in, which are the ones most likely to be revisited, defended or abandoned.
>
> **Watch out for:** the choices hidden in it: how many bands, which prices count, and what period to include. Change them and the picture changes.

## What it measures

The distribution of traded volume across price. It is not a signal that is computed bar by bar: it summarizes a stretch of history, and it changes only when new bars are added.

Three reference points are read from it:

- **Point of control (POC):** the price band with the most volume.
- **Value area:** the contiguous band around the POC that holds a set share of the volume (70% by convention).
- **Low-volume nodes:** bands with little volume, where price moved through quickly.

## Calculation

1. Split the range from the lowest low to the highest high into $B$ equal price bands (24 here).
2. For each bar, take its typical price $(H + L + C)/3$ and add the bar's whole volume to the band that contains it.
3. The POC is the band with the largest total.
4. Start the value area at the POC. Repeatedly add whichever neighboring band (above or below) has more volume, until the area holds at least 70% of the total.

**Worked example.** Bands of width 1 from 10 to 13. Six bars of volume 100 each have typical prices 10.0, 11.5, 11.5, 11.5, 12.5 and 13.0. The bands collect:

| Band | Bars | Volume |
|---|---|---|
| 10 to 11 | 10.0 | 100 |
| 11 to 12 | 11.5 three times | 300 |
| 12 to 13 | 12.5 and 13.0 | 200 |

The POC is the 11 to 12 band, centred at 11.5. The total is 600 and 70% of it is 420. The POC alone holds 300. Its neighbors hold 100 (below) and 200 (above), so the area adds the upper one and reaches 500, which is at least 420. The value area is 11 to 13.

```python
def volume_profile(high, low, close, volume, bins=24, share=0.7):
    typical = (high + low + close) / 3
    edges = np.linspace(low.min(), high.max(), bins + 1)
    bucket = pd.cut(typical, edges, include_lowest=True, labels=False)
    totals = volume.groupby(bucket).sum().reindex(range(bins), fill_value=0.0)
    centers = (edges[:-1] + edges[1:]) / 2
    poc = int(totals.to_numpy().argmax())
    lo_bin = hi_bin = poc
    covered = totals.iloc[poc]
    while covered < share * totals.sum():
        below = totals.iloc[lo_bin - 1] if lo_bin > 0 else -1.0
        above = totals.iloc[hi_bin + 1] if hi_bin < bins - 1 else -1.0
        if above >= below:
            hi_bin += 1
            covered += above
        else:
            lo_bin -= 1
            covered += below
    profile = pd.Series(totals.to_numpy(), index=centers)
    return profile, centers[poc], edges[lo_bin], edges[hi_bin + 1]
```

## How to read it

<figure class="chart">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="../../charts/volume-profile-dark.svg">
<img src="../../charts/volume-profile-light.svg" alt="Price over time with the value area shaded and the point of control marked, and a sideways histogram of volume at each price on the right" width="840" height="480">
</picture>
<figcaption>Synthetic daily data, 320 bars, 24 price bands. The point of control (pink) is at 119.55. The value area (teal) runs from 100.44 to 124.90 and holds 76% of the volume. A second heavy node, outside the value area, sits near 98 to 101.</figcaption>
</figure>

- **The point of control** is the price with the most business. Price tends to be drawn back to it, and it is often read as a "fair price" for the period.
- **The value area** is where most of the trading happened. Price moving back inside it after leaving is read as a return to fair value. A decisive move out of it is read as a new value being established.
- **Low-volume nodes** are price levels the market did not accept. Price often moves through them quickly.
- **High-volume nodes** away from the POC are other levels where many traders have positions.

What it does not tell you: whether those traders were buying or selling, or what price will do next.

## Best used when

- You want **levels with a reason**, tied to where money actually traded.
- You study a **range or a particular period**, such as the time since a major low.
- Your market has **reliable volume**.

## Avoid when

- **Volume is unreliable** or split across venues, so that your data covers only part of the trading.
- You use a **very short** period or **too few bars**, which gives a patchy profile.
- You treat the levels as **certain**. They describe where trading was, and not where it will be.

## Settings and tuning

- **Number of bands.** 24 here. More bands give finer detail and more noise, and fewer bands give a coarser picture. On the sample, going from 12 bands to 48 moved the POC from 120.31 to 119.17, about 1.1 points.
- **The period.** The profile covers whatever bars you give it. A session, a week, a month or the time since an event are common choices.
- **The value area share.** 70% is the convention.

## Implementation variations

- **How volume is assigned.** This page puts a bar's whole volume in the band of its typical price. Many tools spread it across the bar's whole range, or use finer data, such as one-minute bars, for accuracy. A profile built from daily bars is much cruder than one built from intraday bars.
- **The value area rule.** Some tools add two bands at a time, which can give a slightly different area.
- **Contiguity.** The value area is one unbroken band by construction, so it can leave out a large node elsewhere. In the figure, the node near 98 holds more volume than most bands inside the value area, but lies outside it.
- **Naming.** Tools call it "Volume Profile", "Volume by Price" or "Price by Volume". "Market Profile" is a related but different method that counts time at each price.

## Is it useful?

**Situational.** It adds something most studies here do not: a view of the price axis. On the sample, the point of control was at 119.55, in the high plateau of the range. The value area ran from 100.44 to 124.90 and held 76% of all the volume. A second heavy node sat near 98 to 101, where price consolidated after the selloff, and a thin band near 104 marked a gap that the rebound crossed quickly. At the last close (102.44), 69% of the volume had traded at higher prices, which suggests that many of the people who bought during the range were still sitting on losses. It is that kind of context that makes the profile worth looking at. But it depends on its settings, and the sample's volume is synthetic. Use it to find levels that deserve attention, then check that they matter in your market.

## Pairs well with / See also

- [Volume Weighted Average Price](../volume-weighted-average-price/): a single average price from the same volume.
- [Anchored VWAP](../anchored-vwap/): the average price paid since a chosen event.
- [Pivot Points](../pivot-points/): another set of levels, from the last period's range.
