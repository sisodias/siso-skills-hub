# Component review gallery

A small static site for showing the client several versions of one component at a time,
built with their real logo, links, social icons, copy and background art. They open one
link on a phone, look through the options, and reply with a number.

## What the client sees

- `/` lists the components under review
- `/review.html?c=<component>` is the gallery: option tabs, a Desktop/Mobile switch, and
  every option previewed live at true proportions
- `/render.html?c=<component>&v=<option>` is one option on its own, full size, shareable

Every state lives in the URL, so "option 3 on mobile" is a link that can be pasted into a
message:

```
https://PROJECT.pages.dev/review.html?c=footer&v=3&view=mobile
```

The Pages project name for this gallery is in `gallery.config.json`.

## Files

```
deploy.sh              checks, then deploys site/ to Cloudflare Pages
gallery.config.json    client, Pages project, credentials file
scripts/check.mjs      every variant's fields + every referenced asset
scripts/shots.mjs      renders every option at both sizes
site/                  the static site itself
```

## Adding a component

Create `site/components/<component>.js`, then point `site/components/registry.js` at it:

```js
import footer from './footer.js';
export const COMPONENTS = { footer };
export const ORDER = ['footer'];
```

The file that generated this folder ships a worked footer example with six variants,
including a `defaultVariantId` for the client's current design. Start from that shape.

## Deploying

```bash
./deploy.sh --dry-run   # run the checks only
./deploy.sh             # check, then publish
```

The gallery deploys to its own Pages project, deliberately separate from the client's live
site, so a review deploy can never touch production. `site/_headers` sends
`X-Robots-Tag: noindex` on everything, so the link stays out of search results even though
it is not password protected.
