# Writing variants that are worth comparing

## The data shape

A component is a plain object. No build step, no framework, no JSX.

```js
export default {
  id: 'hero',
  label: 'Hero',
  status: 'In review',
  summary: 'One line for the index page.',
  brief: 'What the client is being asked to judge.',
  defaultVariantId: '6',            // optional: the client's current design
  baseCss: `...shared by every variant...`,
  variants: [
    {
      id: '1',
      name: 'Short name the client can say out loud',
      note: 'What is different about this one, in one sentence.',
      bestFor: 'When this one wins.',
      css: `...this variant only...`,
      html: `...this variant only...`,
    },
  ],
};
```

`render.html` injects `baseCss + variant.css` into the document and appends `variant.html`
to a page that is at least one viewport tall, so a footer sits at the bottom of a page
exactly as it would in production.

## What makes a good set

Four to six options is the useful range. Fewer does not cover the space; more turns the
comparison into a reading exercise.

Vary the axis that actually matters, and vary it once per option:

- how much artwork shows: none, a band, full bleed, a raised panel over it
- structure: centred stack, two columns, three columns, single rail
- weight: quiet and short versus loud and tall
- tone: brand artwork versus flat colour

Do not vary the content between options. If option 2 has the newsletter and option 5 does
not, the client is no longer comparing design, they are comparing features, and the answer
becomes "the one with the sign-up please".

Every option needs to survive a 390px phone unchanged in content. Text wraps, columns
become rows, nothing is hidden except labels that are already available to screen readers.

## CSS conventions

Namespace every rule with the variant class so options cannot leak into each other:

```css
.f1 .inner { ... }        /* footer option 1 */
@media (max-width: 700px) { .f1 .inner { ... } }
```

Keep the shared pieces (`.social`, `.newsletter-row`, `.link-row`, `.link-cols`, `.bottom`)
in `baseCss` and change only their arrangement per variant. That is what makes the
comparison fair, and it is much less CSS to write.

Use absolute paths (`/assets/bg/plate-a.jpg`) for background images: the stylesheet is
injected into three different pages and relative paths resolve differently.

## Things that bite

- **Wide wordmarks versus square badges.** A logo swap changes the layout maths. A wide
  wordmark at `min(330px, 62vw)` becomes a 370px-tall block as a square badge. Size logos
  from a shared `.logo` rule per variant and re-check every option after swapping one.
- **Dark artwork behind dark logos.** Check the render, not the intention: an embroidered
  or dark mark on a dark plum background can disappear. Looking at the PNG is the only
  reliable test.
- **Tall options.** The gallery grows the preview frame to the component's own height so
  nothing is cut off. A 1200px-tall footer is fine and honest; do not crop it to fit.
- **Letter-spacing and font size in em/rem with viewport scaling.** Avoid negative tracking
  and viewport-scaled font sizes; they break at one of the two review sizes.
- **Rebuilding an existing live component.** Measure the real one rather than trusting the
  repo's CSS: `getComputedStyle` and `getBoundingClientRect` on the live page give you the
  deployed values, which often differ from uncommitted local changes. Playwright is the
  quickest way to both measure it and screenshot it for comparison.

## Naming the options

The client will say these names out loud, in a voice note. Keep them to two or three words
and describe the look, not the technique: "Sunset band", "Quiet rail", "Deep water". Put
the technique in `note`.

Name the client's own current design plainly, for example "Current footer, new sign-up",
so it is obvious which option is the safe one.
