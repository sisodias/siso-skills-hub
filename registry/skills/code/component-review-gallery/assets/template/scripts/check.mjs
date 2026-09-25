import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { COMPONENTS, ORDER } from '../site/components/registry.js';

/* Gate that runs before every deploy: every variant carries the fields the
   gallery needs, every referenced asset exists on disk, and nothing rendered
   an "undefined" into the markup. The failure that matters here is a missing
   background or a broken link slipping out to the client. */

const here = dirname(fileURLToPath(import.meta.url));
const siteDir = join(here, '..', 'site');

const problems = [];
const assetRefs = new Set();
let variantCount = 0;

for (const id of ORDER) {
  const component = COMPONENTS[id];
  if (!component) {
    problems.push(`registry lists "${id}" but no component is registered under that id`);
    continue;
  }
  if (component.id !== id) problems.push(`component "${id}" declares id "${component.id}"`);
  for (const field of ['label', 'summary', 'brief', 'baseCss']) {
    if (!component[field]) problems.push(`${id}: missing ${field}`);
  }
  if (!Array.isArray(component.variants) || component.variants.length < 2) {
    problems.push(`${id}: needs at least two variants to be worth showing`);
    continue;
  }
  if (
    component.defaultVariantId &&
    !component.variants.some((v) => v.id === component.defaultVariantId)
  ) {
    problems.push(`${id}: defaultVariantId "${component.defaultVariantId}" matches no variant`);
  }

  const seen = new Set();
  for (const variant of component.variants) {
    variantCount += 1;
    const tag = `${id} variant ${variant.id ?? 'with no id'}`;
    for (const field of ['id', 'name', 'note', 'html', 'css']) {
      if (!variant[field]) problems.push(`${tag}: missing ${field}`);
    }
    if (seen.has(variant.id)) problems.push(`${tag}: duplicate id`);
    seen.add(variant.id);

    const source = `${component.baseCss}${variant.css}${variant.html}`;
    if (source.includes('undefined')) problems.push(`${tag}: rendered the word "undefined"`);

    for (const match of source.matchAll(/\/assets\/[A-Za-z0-9._/-]+/g)) {
      assetRefs.add(match[0]);
    }
  }
}

for (const ref of [...assetRefs].sort()) {
  if (!existsSync(join(siteDir, ref))) problems.push(`missing asset: ${ref}`);
}

if (problems.length) {
  console.error('check failed:');
  for (const problem of problems) console.error('  - ' + problem);
  process.exit(1);
}

console.log(
  `ok: ${ORDER.length} component(s), ${variantCount} variants, ${assetRefs.size} referenced assets all present`,
);
for (const id of ORDER) {
  const component = COMPONENTS[id];
  console.log(
    `    ${component.label}: ${component.variants.map((v) => `${v.id} ${v.name}`).join(' | ')}`,
  );
}
