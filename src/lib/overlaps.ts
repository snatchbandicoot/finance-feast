import type { CollectionEntry } from 'astro:content';

type Study = CollectionEntry<'studies'>;

export const STRENGTH_LABEL = {
  identical: 'Same measurement',
  near: 'Nearly the same',
  partial: 'Partly overlaps',
} as const;

const RANK = { identical: 0, near: 1, partial: 2 } as const;

export interface OverlapRow {
  other: Study;
  strength: keyof typeof STRENGTH_LABEL;
  corr?: number;
  note: string;
}

/** Overlaps a study declares itself, plus those other studies declare with it, so both pages of a pair show the link. */
export function overlapsFor(id: string, all: Study[]): OverlapRow[] {
  const byId = new Map(all.map((s) => [s.id, s]));
  const rows: OverlapRow[] = [];
  for (const s of all) {
    for (const o of s.data.overlaps) {
      if (s.id === id) {
        const other = byId.get(o.with);
        if (other) rows.push({ other, strength: o.strength, corr: o.corr, note: o.note });
      } else if (o.with === id) {
        rows.push({ other: s, strength: o.strength, corr: o.corr, note: o.note });
      }
    }
  }
  return rows.sort((a, b) => RANK[a.strength] - RANK[b.strength] || a.other.data.title.localeCompare(b.other.data.title));
}

export interface PairRow {
  a: Study;
  b: Study;
  strength: keyof typeof STRENGTH_LABEL;
  corr?: number;
  note: string;
}

/** Every declared pair once, strongest first. */
export function allPairs(all: Study[]): PairRow[] {
  const byId = new Map(all.map((s) => [s.id, s]));
  const rows: PairRow[] = [];
  for (const s of all) {
    for (const o of s.data.overlaps) {
      const b = byId.get(o.with);
      if (b) rows.push({ a: s, b, strength: o.strength, corr: o.corr, note: o.note });
    }
  }
  return rows.sort(
    (x, y) => RANK[x.strength] - RANK[y.strength] || (y.corr ?? 1) - (x.corr ?? 1) || x.a.data.title.localeCompare(y.a.data.title),
  );
}
