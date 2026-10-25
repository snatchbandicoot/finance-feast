"""Brand and chart colors. The site's CSS tokens (src/layouts/Base.astro) must use the same values;
tools/verify_studies.py fails if the two drift apart.

The primary highlight is the raspberry pink sampled from the project's mascot image (#d21a52). Teal is its
true complement and gold and blue complete the set, in series order: pink, teal, gold, blue. Both teal and
gold also appear in the mascot image.

Validated with the dataviz palette validator, all four in order, in both modes:
  light  all checks pass. Worst colorblind separation 9.8 (target 8), normal-vision 24 (floor 15).
         Gold is 2.2:1 on the surface, so it is never the only cue: charts with a gold series carry a legend.
  dark   all checks pass, every color at least 3:1 on the surface. Worst colorblind separation 8.9 (target 8),
         which is close to the line: keep pink and teal on different lines of a chart only with a legend.
Three-series charts (ADX with +DI and -DI) use pink, teal and blue, skipping gold, whose light-mode
contrast is weak. That triple also passes in both modes; its closest pair for blue-yellow colorblind readers
(teal against blue) sits in the 6 to 8 band, so those charts always carry a legend.
"pink_text" is the pink used for text, links and button fills, which needs 4.5:1: the brand pink itself in
light mode (5.2:1) and a lighter pink in dark mode (7.7:1).
Note: an earlier, lighter pink with teal failed the colorblind check; the real pink does not.
"""

LIGHT = dict(pink="#d21a52", teal="#0e9f93", gold="#e0a100", blue="#2a78d6", pink_text="#d21a52")
DARK = dict(pink="#dc2a5f", teal="#10a79a", gold="#c98500", blue="#3987e5", pink_text="#ff7aa8")
