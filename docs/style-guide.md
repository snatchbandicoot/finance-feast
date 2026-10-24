# Style guide

**Audience.** Someone who trades or studies charts but does not have a quant background.

**Tone.** Plain, direct, opinionated, honest about uncertainty. Say "this mostly duplicates X"
when it does. Avoid hype and avoid hedging every sentence.

**Claims.**
- No performance claims ("wins 70% of the time") without a cited source.
- Separate what the math guarantees from what traders believe or hope it implies.
- Where evidence is weak or contested, say so.

**Math.** Define every symbol. Give a small worked numeric example. Code snippets are short
pandas and must be verified against an independent reference before `status: reviewed`.

**Platforms.** Platform-neutral by default. Mention a platform only when a study exists on that
platform alone (`platform:` field) or when implementations differ in a way that changes results.

**Original text.** Write explanations from scratch. Do not copy descriptions from any vendor's
documentation. Standard formulas are fine.

**Sections.** Follow `docs/study-template.md` in order. Drop "Implementation variations" if empty.

**Status.** New pages are `draft`. Only the owner moves a page to `reviewed`, after checking the
"Avoid when" and "Is it useful?" sections.

**Footer.** Every page carries the site-wide "educational content, not investment advice" footer.
