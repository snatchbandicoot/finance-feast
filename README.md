# finance-feast

A plain-language library of technical-analysis studies: what each one measures, how it is
calculated, how to read it, and when to use or avoid it. One markdown page per study, built into
a static site with Astro and published on GitHub Pages.

## Working on the site

```
npm install
npm run dev        # local site with live reload
npm run build      # static site in dist/, plus the search index
```

Study pages live in `src/content/studies/`. Copy the structure in `docs/study-template.md` and
follow `docs/style-guide.md`. New pages start as `status: draft` until reviewed.

## Checking the math

```
pip install -r tools/requirements.txt
python3 tools/verify_studies.py
```

The indicator code shown on each page lives in `tools/indicators.py`. The check compares it with
independent plain-loop implementations, asserts the worked examples quoted on the pages, and fails
if a page's code block differs from the function it claims to show. CI runs it before deploying.

## Example charts

```
python3 tools/make_sample_data.py   # only if the sample data needs regenerating
python3 tools/make_charts.py
```

Charts are drawn from **synthetic** sample data (`data/`) using the same indicator functions, in a
light and a dark variant, and written to `public/charts/`. The SVGs are committed, so building
the site needs no Python. Each page says its chart uses synthetic data.
