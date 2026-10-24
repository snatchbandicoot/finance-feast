import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const studies = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/studies' }),
  schema: z.object({
    title: z.string(),
    aliases: z.array(z.string()).default([]),
    category: z.enum(['trend', 'momentum', 'volatility', 'volume', 'other']),
    summary: z.string(),
    verdict: z.enum(['essential', 'situational', 'redundant', 'skip']),
    status: z.enum(['draft', 'reviewed']).default('draft'),
    platform: z.string().optional(),
    related: z.array(z.string()).default([]),
  }),
});

export const collections = { studies };
