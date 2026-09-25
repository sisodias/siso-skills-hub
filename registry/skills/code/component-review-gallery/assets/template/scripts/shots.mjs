import { mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { COMPONENTS, ORDER } from '../site/components/registry.js';

/* Renders every option at both sizes straight from the render page. This is the
   visual check before a deploy, and the PNGs double as images that can be sent
   to the client.

     node scripts/shots.mjs                 against http://127.0.0.1:8781
     node scripts/shots.mjs https://<project>.pages.dev

   Playwright is looked up in this folder, then in the parent, then as a normal
   package. Point PLAYWRIGHT_MODULE at another install's index.js if needed. */

const here = dirname(fileURLToPath(import.meta.url));
const origin = process.argv[2] ?? 'http://127.0.0.1:8781';
const outDir = join(here, '..', 'shots');

async function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_MODULE,
    join(here, '..', 'node_modules', 'playwright', 'index.js'),
    join(here, '..', '..', 'node_modules', 'playwright', 'index.js'),
  ].filter(Boolean);

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      const mod = await import(pathToFileURL(candidate).href);
      return mod.default ?? mod;
    }
  }
  try {
    const mod = await import('playwright');
    return mod.default ?? mod;
  } catch {
    console.error(
      'playwright not found. Run `npm i -D playwright` here, or set PLAYWRIGHT_MODULE to another install.',
    );
    process.exit(1);
  }
}

const { chromium } = await loadPlaywright();

const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
};

await mkdir(outDir, { recursive: true });
const browser = await chromium.launch();
const failures = [];

for (const id of ORDER) {
  const component = COMPONENTS[id];
  for (const variant of component.variants) {
    for (const [view, size] of Object.entries(VIEWPORTS)) {
      const page = await browser.newPage({ viewport: size });
      const errors = [];
      page.on('pageerror', (e) => errors.push(String(e)));
      page.on('requestfailed', (r) => errors.push('failed request ' + r.url()));

      await page.goto(`${origin}/render.html?c=${component.id}&v=${variant.id}&view=${view}`, {
        waitUntil: 'networkidle',
      });

      const rendered = page.locator('footer, section, header, main').first();
      if ((await rendered.count()) === 0) {
        failures.push(`${component.id} ${variant.id} ${view}: nothing rendered`);
        await page.close();
        continue;
      }

      const box = await rendered.boundingBox();
      if (!box || box.height < 120) {
        failures.push(
          `${component.id} ${variant.id} ${view}: only ${Math.round(box?.height ?? 0)}px tall`,
        );
      } else if (box.width > size.width + 1) {
        failures.push(`${component.id} ${variant.id} ${view}: overflows horizontally`);
      }

      const file = join(outDir, `${component.id}-${variant.id}-${view}.png`);
      await rendered.screenshot({ path: file });
      if (errors.length) failures.push(`${component.id} ${variant.id} ${view}: ${errors.join('; ')}`);
      console.log(
        `${component.id} ${variant.id} ${view} -> ${file.replace(here + '/', '')} (${Math.round(box?.height ?? 0)}px)`,
      );
      await page.close();
    }
  }
}

for (const [view, size] of Object.entries(VIEWPORTS)) {
  const page = await browser.newPage({ viewport: size });
  await page.goto(`${origin}/review.html?view=${view}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  const file = join(outDir, `gallery-${view}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`gallery ${view} -> ${file.replace(here + '/', '')}`);
  await page.close();
}

await browser.close();

if (failures.length) {
  console.error('\nvisual check failed:');
  for (const failure of failures) console.error('  - ' + failure);
  process.exit(1);
}
console.log('\nok: every option rendered at both sizes with no errors');
