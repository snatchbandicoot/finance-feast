import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const studies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/studies' }),
  schema: z.object({
    title: z.string(),
    aliases: z.array(z.string()).default([]),
    category: z.enum(['trend', 'momentum', 'volatility', 'volume', 'other']),
    summary: z.string(),
    display: z.enum(['overlay', 'panel']),
    inputs: z.array(z.object({ name: z.string(), default: z.union([z.string(), z.number()]) })).default([]),
    verdict: z.enum(['essential', 'situational', 'redundant', 'skip']),
    status: z.enum(['draft', 'reviewed']).default('draft'),
    platform: z.string().optional(),
    related: z.array(z.string()).default([]),
    overlaps: z
      .array(
        z.object({
          with: z.string(),
          strength: z.enum(['identical', 'near', 'partial']),
          corr: z.number().optional(),
          note: z.string(),
        }),
      )
      .default([]),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    status: z.enum(['draft', 'reviewed']).default('draft'),
  }),
});

export const collections = { studies, guides };
