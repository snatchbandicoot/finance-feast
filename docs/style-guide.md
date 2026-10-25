# Style guide

**Audience.** Someone who trades or studies charts but does not have a quant background.

**Tone.** Plain, direct, opinionated, honest about uncertainty. Say "this mostly duplicates X"
when it does. Avoid hype and avoid hedging every sentence.

**Claims.**
- No performance claims ("wins 70% of the time") without a cited source.
- Separate what the math guarantees from what traders believe or hope it implies.
- Where evidence is weak or contested, say so.

**Math.** Put the `$$` markers of a display formula on their own lines. A formula written as `$$ ... $$` on one line renders as small inline math, and the check script rejects it. Define every symbol. Give a small worked numeric example. Code snippets are short
pandas and must be verified against an independent reference before `status: reviewed`.

**Platforms.** Platform-neutral by default. Mention a platform only when a study exists on that
platform alone (`platform:` field) or when implementations differ in a way that changes results.

**Original text.** Write explanations from scratch. Do not copy descriptions from any vendor's
documentation. Standard formulas are fine.

**Summary first.** Every page opens with the "In plain English" block, followed by "Good for" and
"Watch out for" lines. A reader who stops there should still come away with the right idea. Write it
last, after the rest of the page, so it matches what the page actually says. The verdict is shown
automatically from the `verdict` frontmatter field, so don't repeat it in the summary.

**Sections.** Follow `docs/study-template.md` in order. Drop "Implementation variations" if empty.

**Status.** New pages are `draft`. Only the owner moves a page to `reviewed`, after checking the
"Avoid when" and "Is it useful?" sections.

**Charts.** One example chart per page, placed at the top of "How to read it", with a caption that
states only what the chart shows, with the numbers checked against the data. Charts are drawn by
`tools/make_charts.py` from synthetic data, never hand-edited, and are always described as synthetic.
Hide warm-up values of recursive indicators. Use pink first and teal second for series (gold only as a third, with a legend), with neutral ink
for price, a legend whenever a panel has two or more series, and a light and a dark variant.

**Color.** Pink is the primary highlight, sampled from the project's mascot image (`#d21a52`). The palette
lives in `tools/palette.py`, which the charts read, and is mirrored as CSS tokens in `src/layouts/Base.astro`.
The check script fails if they differ. Series order is pink, teal, gold, blue. Teal is pink's true complement;
a lighter, orangier pink failed the colorblind check against teal, but the real pink passes. Text and links use
`pink_text` (the same pink in light mode, a lighter pink in dark mode) so they stay readable.

**Footer.** Every page carries the site-wide "educational content, not investment advice" footer.
