---
title: Relative Strength Index          # canonical, platform-neutral name
aliases: [RSI, Wilder's RSI]            # other names people search for
category: momentum                      # trend | momentum | volatility | volume | other
summary: One sentence, plain English.   # shown in the index
display: panel                          # overlay (on price) | panel (separate pane)
inputs:                                 # parameters and common defaults
  - { name: length, default: 14 }
verdict: situational                    # essential | situational | redundant | skip
status: draft                           # draft | reviewed
# platform: <name>                      # ONLY if the study exists on a single platform
related: [stochastic-oscillator]        # slugs of other studies
---

> **Takeaway.** One or two sentences: what it tells you and whether it is worth using.

## What it measures

Plain English, no jargon. What question does this study answer about price or volume?

## Calculation

Step by step, then the formula.

$$ \text{formula here} $$

Worked example with small numbers a reader can check by hand.

```python
# short pandas snippet; checked against an independent reference implementation
```

## How to read it

What the lines, levels and crossings mean. Reference an example chart in `public/charts/`.
Say what the reading does NOT tell you.

## Best used when

Market conditions, timeframes and pairings where it earns its place.

## Avoid when

Failure modes: where it misleads, lags, or produces constant false signals.

## Settings and tuning

What each input does, the default, and the tradeoff of changing it (faster vs noisier, etc.).

## Implementation variations

Only if sources genuinely differ in a way that changes results (e.g. smoothing method).
Name a platform only where the variation is specific to it. Delete this section otherwise.

## Is it useful?

Blunt verdict matching the `verdict` field. State what it duplicates, if anything,
and what you would use instead.

## Pairs well with / See also

Links to related studies and why they combine well.
