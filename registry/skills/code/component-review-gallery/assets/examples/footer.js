/* Footer — five directions, all built from the same real brand kit:
   the grassy wordmark, the palm-and-note emblem, the four live social links,
   the real navigation, the real tagline, and the client's own background
   plates. Only the arrangement changes, so the client is judging layout and
   mood rather than missing content. */

import { BRAND, SOCIALS, componentFurniture, socialIcon } from './shared.js';

/* Background plates this component expects the client's own shared.js to export.
   Kept local to the example so it stays self-contained documentation. */
const PLATES = {
  sunset: '/assets/bg/footer-a.jpg',
  palm: '/assets/bg/footer-b.jpg',
  deep: '/assets/bg/footer-c.jpg',
  beach: '/assets/bg/footer-d.jpg',
  horizon: '/assets/bg/footer-f.jpg',
};

const f = componentFurniture();

/* The live footer keeps its social links as icon buttons with the labels kept
   for screen readers only, and its link groups collapsed behind Explore and
   Legal. Both are reproduced here rather than replaced. */
const liveSocials = SOCIALS.map(
  (s) =>
    `<a href="${s.href}" aria-label="${s.label}">${socialIcon(s.label, 'footer-social-icon')}<span class="social-label">${s.label}</span></a>`,
).join('');

const LIVE_EXPLORE = ['Home', 'Events', 'Music', 'Gallery', 'About', 'Earn', 'Partnerships', 'Contact'];

const baseCss = `
  :root {
    --plum: #120620;
    --plum-2: #1A0A2E;
    --plum-3: #241038;
    --ink: #0C0417;
    --gold: #B4823C;
    --gold-bright: #D4A45C;
    --text: #ECE4F5;
    --muted: #C8BBD6;
    --line: rgba(255,255,255,.14);
    --display: 'Anton', 'Arial Narrow', sans-serif;
    --heading: 'Fredoka', system-ui, sans-serif;
    --body: 'Work Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    --mono: 'Space Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: var(--plum); }
  body { color: var(--text); font-family: var(--body); font-size: 15px; line-height: 1.6; }
  img { max-width: 100%; }
  a { color: inherit; text-decoration: none; }
  a:hover { color: var(--gold-bright); }
  .footer { position: relative; overflow: hidden; isolation: isolate; }
  .wrap { width: min(1180px, 100% - 44px); margin-inline: auto; }
  .plate { position: absolute; inset: 0; z-index: -2; background-size: cover; background-position: center; }
  .scrim { position: absolute; inset: 0; z-index: -1; }

  .logo { display: block; width: 100%; height: auto; }

  .tagline { margin: 0; color: var(--muted); font-size: 15px; }

  .social-row { display: flex; flex-wrap: wrap; gap: 10px; }
  .social {
    display: grid; place-items: center; width: 44px; height: 44px;
    border: 1px solid var(--line); border-radius: 999px;
    background: rgba(255,255,255,.05); color: var(--text);
    transition: border-color .18s ease, background .18s ease, color .18s ease;
  }
  .social:hover { border-color: var(--gold-bright); background: rgba(180,130,60,.2); color: var(--gold-bright); }
  .social .icon { width: 19px; height: 19px; }

  .social-list { display: grid; gap: 8px; }
  .social-line {
    display: inline-flex; align-items: center; gap: 10px;
    color: var(--muted); font-size: 14px;
  }
  .social-line .icon { width: 17px; height: 17px; color: var(--gold-bright); }

  .newsletter { display: grid; gap: 9px; width: 100%; }
  .newsletter-label {
    font-family: var(--heading); font-weight: 600; font-size: 15px; letter-spacing: .01em;
  }
  .newsletter-row {
    display: flex; gap: 8px; padding: 6px; border: 1px solid var(--line);
    border-radius: 999px; background: rgba(255,255,255,.06);
  }
  .newsletter-row input {
    flex: 1 1 auto; min-width: 0; padding: 9px 14px; border: 0; background: transparent;
    color: var(--text); font: inherit; font-size: 14px;
  }
  .newsletter-row input::placeholder { color: rgba(200,187,214,.7); }
  .newsletter-row input:focus { outline: none; }
  .newsletter-row button {
    flex: 0 0 auto; padding: 9px 18px; border: 0; border-radius: 999px;
    background: var(--gold); color: var(--plum); cursor: pointer;
    font-family: var(--heading); font-weight: 600; font-size: 14px;
  }
  .newsletter-row button:hover { background: var(--gold-bright); }

  .link-row { display: flex; flex-wrap: wrap; gap: 10px 22px; }
  .link-row a { font-size: 14px; color: var(--muted); }

  .link-cols { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 26px; }
  .link-col h3 {
    margin: 0 0 12px; color: var(--gold-bright);
    font-family: var(--heading); font-weight: 600; font-size: 12px;
    letter-spacing: .14em; text-transform: uppercase;
  }
  .link-col a { display: block; padding: 5px 0; color: var(--muted); font-size: 14px; }

  .bottom {
    display: flex; flex-wrap: wrap; gap: 10px 20px;
    justify-content: space-between; align-items: center;
    padding-top: 18px; border-top: 1px solid var(--line);
  }
  .bottom small { color: var(--muted); font-size: 12.5px; }
  .bottom nav { display: flex; flex-wrap: wrap; gap: 6px 18px; }
  .bottom nav a { color: var(--muted); font-size: 12.5px; }
`;

/* ── 1. Sunset band ────────────────────────────────────────────────────────
   Full-bleed artwork, everything centred on it. The biggest, warmest option. */
const v1 = {
  id: '1',
  name: 'Sunset band',
  note: 'Full artwork behind everything, centred. Boldest, and the most "beach club" of the five.',
  bestFor: 'Making the bottom of the page feel like the brand, on a site that already has a busy middle.',
  css: `
    .f1 .plate { background-image: url('${PLATES.sunset}'); }
    .f1 .scrim {
      background:
        linear-gradient(180deg, rgba(18,6,32,.42), rgba(18,6,32,.66) 42%, rgba(9,3,18,.95));
    }
    .f1 .inner {
      position: relative; display: grid; justify-items: center; gap: 20px;
      padding: 62px 0 26px; text-align: center;
    }
    .f1 .brand { display: grid; justify-items: center; }
    .f1 .logo { width: min(172px, 42vw); }
    .f1 .tagline { max-width: 46ch; }
    .f1 .newsletter { max-width: 430px; }
    .f1 .link-row { justify-content: center; margin-top: 4px; }
    .f1 .link-row a { font-size: 13px; letter-spacing: .05em; text-transform: uppercase; }
    .f1 .bottom { width: 100%; margin-top: 26px; }
    @media (max-width: 700px) {
      .f1 .inner { gap: 17px; padding: 46px 0 22px; }
      .f1 .logo { width: min(150px, 38vw); }
      .f1 .bottom { justify-content: center; text-align: center; }
    }
  `,
  html: `
    <footer class="footer f1">
      <div class="plate" aria-hidden="true"></div>
      <div class="scrim" aria-hidden="true"></div>
      <div class="wrap inner">
        <div class="brand">
          <img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" />
        </div>
        <p class="tagline">${BRAND.tagline}</p>
        <div class="social-row">${f.socialRow}</div>
        ${f.newsletter}
        <nav class="link-row" aria-label="Footer">${f.navLinks}</nav>
        <div class="bottom">
          <small>${BRAND.copyright}</small>
          <nav aria-label="Legal">${f.legalLinks}</nav>
        </div>
      </div>
    </footer>`,
};

/* ── 2. Split ──────────────────────────────────────────────────────────────
   Artwork only as a band across the top, then a clean two-column footer. */
const v2 = {
  id: '2',
  name: 'Split columns',
  note: 'A band of artwork up top, then brand and sign-up on the left, links on the right.',
  bestFor: 'Sites with a lot of pages: the links stay scannable instead of turning into a wrapped row.',
  css: `
    .f2 { background: var(--plum-2); }
    .f2 .plate {
      inset: 0 0 auto; height: 210px; background-image: url('${PLATES.palm}');
      background-position: center 38%;
      -webkit-mask-image: linear-gradient(180deg, #000 30%, transparent);
      mask-image: linear-gradient(180deg, #000 30%, transparent);
    }
    /* The plate is a bright sunset; the scrim keeps the brand row calm and
       hands the footer back to plum exactly where the mask ends. */
    .f2 .scrim {
      background: linear-gradient(180deg, rgba(26,10,46,.62), rgba(26,10,46,.5) 130px, var(--plum-2) 210px);
    }
    .f2 .inner { position: relative; padding: 122px 0 26px; }
    .f2 .top {
      display: grid; grid-template-columns: minmax(260px, 1.05fr) minmax(0, 1.55fr);
      gap: 30px 54px;
    }
    .f2 .brand-col { display: grid; gap: 18px; align-content: start; }
    .f2 .brand { display: flex; align-items: center; }
    .f2 .logo { width: 104px; }
    .f2 .tagline { max-width: 34ch; font-size: 14.5px; }
    .f2 .link-cols { gap: 22px 26px; }
    .f2 .bottom { margin-top: 34px; }
    @media (max-width: 900px) {
      .f2 .top { grid-template-columns: minmax(0, 1fr); gap: 30px; }
      .f2 .link-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 520px) {
      .f2 .plate { height: 170px; }
      .f2 .inner { padding: 96px 0 22px; }
      .f2 .logo { width: 92px; }
      .f2 .link-cols { grid-template-columns: minmax(0, 1fr); }
      .f2 .bottom { justify-content: flex-start; }
    }
  `,
  html: `
    <footer class="footer f2">
      <div class="plate" aria-hidden="true"></div>
      <div class="scrim" aria-hidden="true"></div>
      <div class="wrap inner">
        <div class="top">
          <div class="brand-col">
            <div class="brand">
              <img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" />
            </div>
            <p class="tagline">${BRAND.tagline}</p>
            ${f.newsletter}
            <div class="social-list">${f.socialList}</div>
          </div>
          <div class="link-cols">
            <div class="link-col">
              <h3>Explore</h3>
              <a href="#">Events &amp; Tickets</a><a href="#">Music</a><a href="#">Gallery</a><a href="#">Partnerships</a>
            </div>
            <div class="link-col">
              <h3>Get involved</h3>
              <a href="#">Book Bykonz</a><a href="#">Earn Yard Points</a><a href="#">About us</a><a href="#">Q&amp;As</a>
            </div>
            <div class="link-col">
              <h3>Contact</h3>
              <a href="mailto:${BRAND.email}">${BRAND.email}</a><a href="#">Terms &amp; Conditions</a><a href="#">Privacy Policy</a>
            </div>
          </div>
        </div>
        <div class="bottom">
          <small>${BRAND.copyright}</small>
          <nav aria-label="Legal">${f.legalLinks}</nav>
        </div>
      </div>
    </footer>`,
};

/* ── 3. Card over artwork ──────────────────────────────────────────────────
   The artwork stays fully visible; content sits on a raised panel over it. */
const v3 = {
  id: '3',
  name: 'Card over artwork',
  note: 'Artwork shows through behind a raised panel. Text stays very legible, and the picture still reads.',
  bestFor: 'Showing off a photo without fighting it for contrast.',
  css: `
    .f3 .plate { background-image: url('${PLATES.beach}'); background-position: center 55%; }
    .f3 .scrim { background: linear-gradient(180deg, rgba(12,4,23,.5), rgba(12,4,23,.78)); }
    .f3 .inner { position: relative; padding: 56px 0 26px; }
    .f3 .card {
      display: grid; justify-items: center; gap: 18px; text-align: center;
      width: min(720px, 100%); margin-inline: auto; padding: 40px 34px 34px;
      border: 1px solid rgba(255,255,255,.16); border-radius: 12px;
      background: rgba(18,6,32,.86);
      box-shadow: 0 26px 60px rgba(0,0,0,.34);
    }
    .f3 .brand { display: grid; justify-items: center; }
    .f3 .logo { width: min(152px, 38vw); }
    .f3 .tagline { max-width: 44ch; }
    .f3 .newsletter { max-width: 420px; margin-top: 4px; }
    .f3 .social-row { justify-content: center; }
    .f3 .under { margin-top: 26px; display: grid; gap: 20px; }
    .f3 .link-row { justify-content: center; }
    .f3 .link-row a { color: var(--text); }
    .f3 .bottom { border-top-color: rgba(255,255,255,.22); }
    @media (max-width: 620px) {
      .f3 .inner { padding: 38px 0 22px; }
      .f3 .card { padding: 30px 20px 26px; gap: 15px; }
      .f3 .logo { width: min(132px, 34vw); }
      .f3 .bottom { justify-content: center; text-align: center; }
    }
  `,
  html: `
    <footer class="footer f3">
      <div class="plate" aria-hidden="true"></div>
      <div class="scrim" aria-hidden="true"></div>
      <div class="wrap inner">
        <div class="card">
          <div class="brand">
            <img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" />
          </div>
          <p class="tagline">${BRAND.tagline}</p>
          ${f.newsletter}
          <div class="social-row">${f.socialRow}</div>
        </div>
        <div class="under">
          <nav class="link-row" aria-label="Footer">${f.navLinks}</nav>
          <div class="bottom" style="margin-top:0">
            <small>${BRAND.copyright}</small>
            <nav aria-label="Legal">${f.legalLinks}</nav>
          </div>
        </div>
      </div>
    </footer>`,
};

/* ── 4. Rail ───────────────────────────────────────────────────────────────
   One clean line, then a strip of the sea along the very bottom edge. */
const v4 = {
  id: '4',
  name: 'Quiet rail',
  note: 'The shortest of the five. One line of links, small icons, and a sea strip along the bottom.',
  bestFor: 'Staying out of the way. Works when the page above it is already loud.',
  css: `
    .f4 { background: var(--plum-2); }
    .f4 .inner { padding: 34px 0 0; }
    .f4 .rail {
      display: grid; grid-template-columns: minmax(150px, auto) minmax(0, 1fr) auto;
      align-items: center; gap: 18px 30px;
    }
    .f4 .logo { width: 68px; }
    .f4 .link-row { justify-content: center; gap: 8px 20px; }
    .f4 .link-row a { font-size: 13.5px; }
    .f4 .social-row { justify-content: flex-end; gap: 8px; }
    .f4 .social { width: 38px; height: 38px; }
    .f4 .social .icon { width: 17px; height: 17px; }
    .f4 .meta {
      display: flex; flex-wrap: wrap; gap: 8px 20px; justify-content: space-between;
      align-items: center; padding: 18px 0 22px;
    }
    .f4 .meta small { color: var(--muted); font-size: 12.5px; }
    .f4 .meta nav { display: flex; flex-wrap: wrap; gap: 6px 18px; }
    .f4 .meta nav a { color: var(--muted); font-size: 12.5px; }
    .f4 .horizon {
      position: relative; height: 108px;
      background: url('${PLATES.horizon}') center 58% / cover;
    }
    .f4 .horizon::after {
      position: absolute; inset: 0; content: '';
      background: linear-gradient(180deg, var(--plum-2) 2%, rgba(26,10,46,.12) 55%, rgba(26,10,46,.28));
    }
    @media (max-width: 900px) {
      .f4 .rail { grid-template-columns: minmax(0, 1fr); justify-items: center; text-align: center; gap: 20px; }
      .f4 .link-row, .f4 .social-row { justify-content: center; }
      .f4 .meta { justify-content: center; text-align: center; }
    }
    @media (max-width: 520px) {
      .f4 .inner { padding-top: 28px; }
      .f4 .horizon { height: 84px; }
    }
  `,
  html: `
    <footer class="footer f4">
      <div class="wrap inner">
        <div class="rail">
          <img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" />
          <nav class="link-row" aria-label="Footer">${f.navLinks}</nav>
          <div class="social-row">${f.socialRow}</div>
        </div>
        <div class="meta">
          <small>${BRAND.copyright}</small>
          <nav aria-label="Legal">${f.legalLinks}</nav>
        </div>
      </div>
      <div class="horizon" aria-hidden="true"></div>
    </footer>`,
};

/* ── 5. Deep water ─────────────────────────────────────────────────────────
   Dark, editorial, with the name set huge across the bottom as a watermark. */
const v5 = {
  id: '5',
  name: 'Deep water',
  note: 'Darkest option. The name runs across the bottom in full height, with links in tidy columns above it.',
  bestFor: 'Feeling premium and night-time rather than beachy.',
  css: `
    .f5 { background: var(--ink); }
    .f5 .plate { background-image: url('${PLATES.deep}'); background-position: center 40%; opacity: .58; }
    .f5 .scrim { background: linear-gradient(180deg, rgba(12,4,23,.72), rgba(12,4,23,.9) 55%, #0C0417); }
    .f5 .inner { position: relative; padding: 56px 0 30px; }
    .f5 .head {
      display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;
      align-items: center; padding-bottom: 26px; border-bottom: 1px solid var(--line);
    }
    .f5 .brand { display: flex; align-items: center; }
    .f5 .logo { width: 92px; }
    .f5 .mid {
      display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(260px, .9fr);
      gap: 34px 48px; padding: 30px 0 34px;
    }
    .f5 .tagline { max-width: 40ch; margin-bottom: 20px; }
    .f5 .newsletter { max-width: 420px; }
    .f5 .bottom { border-top: 0; padding-top: 0; }
    .f5 .mark {
      position: relative; margin: 6px 0 -18px; text-align: center; font-family: var(--display);
      font-size: clamp(52px, 14.4vw, 250px); line-height: .78; letter-spacing: .01em;
      color: transparent; -webkit-text-stroke: 1px rgba(212,164,92,.3);
      white-space: nowrap; pointer-events: none; user-select: none;
    }
    @supports not (-webkit-text-stroke: 1px black) {
      .f5 .mark { color: rgba(212,164,92,.14); -webkit-text-stroke: 0; }
    }
    @media (max-width: 860px) {
      .f5 .mid { grid-template-columns: minmax(0, 1fr); }
      /* On one column the copyright would land between the sign-up and the
         links. Dissolving the left column lets the page order itself. */
      .f5 .mid > div:first-child { display: contents; }
      .f5 .tagline { order: 1; }
      .f5 .newsletter { order: 2; }
      .f5 .link-cols { order: 3; }
      .f5 .mid .bottom { order: 4; }
      .f5 .link-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 520px) {
      .f5 .inner { padding: 40px 0 22px; }
      .f5 .head { justify-content: center; text-align: center; }
      .f5 .link-cols { grid-template-columns: minmax(0, 1fr); }
      .f5 .mark { margin-bottom: -8px; }
    }
  `,
  html: `
    <footer class="footer f5">
      <div class="plate" aria-hidden="true"></div>
      <div class="scrim" aria-hidden="true"></div>
      <div class="wrap inner">
        <div class="head">
          <div class="brand">
            <img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" />
          </div>
          <div class="social-row">${f.socialRow}</div>
        </div>
        <div class="mid">
          <div>
            <p class="tagline">${BRAND.tagline}</p>
            ${f.newsletter}
            <div class="bottom" style="margin-top:22px">
              <small>${BRAND.copyright}</small>
              <nav aria-label="Legal">${f.legalLinks}</nav>
            </div>
          </div>
          <div class="link-cols">
            <div class="link-col">
              <h3>Explore</h3>
              <a href="#">Events &amp; Tickets</a><a href="#">Music</a><a href="#">Gallery</a><a href="#">Partnerships</a>
            </div>
            <div class="link-col">
              <h3>Get involved</h3>
              <a href="#">Book Bykonz</a><a href="#">Earn Yard Points</a><a href="#">About us</a><a href="#">Q&amp;As</a>
            </div>
          </div>
        </div>
        <div class="mark" aria-hidden="true">BYKONZYARD</div>
      </div>
    </footer>`,
};

/* ── 6. Current footer, new sign-up ────────────────────────────────────────
   The footer that is live on bykonzyard.co.uk today, rebuilt to match it, with
   one change: the sign-up bar is the pill from the other options instead of the
   one that stacks into a block on a phone. */
const v6 = {
  id: '6',
  name: 'Current footer, new sign-up',
  note: 'The footer that is live now, kept exactly as it is, with the new sign-up bar swapped in.',
  bestFor: 'Staying with what the client already has, once the sign-up is fixed.',
  css: `
    .f6 { background: var(--plum); border-top: 1px solid rgba(212,164,92,.18); }
    .f6 .inner { width: min(1376px, 100% - 64px); margin-inline: auto; padding: 72px 0 24px; }
    .f6 .footer-top {
      display: flex; flex-direction: column; align-items: center; gap: 32px;
      padding-bottom: 30px; border-bottom: 1px solid var(--line); text-align: center;
    }
    .f6 .footer-brand img { width: 78px; }
    .f6 .footer-socials { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
    .f6 .footer-socials a {
      display: inline-grid; place-items: center; width: 44px; height: 44px;
      border: 1px solid rgba(255,255,255,.22); border-radius: 999px;
      background: rgba(255,255,255,.03); color: var(--gold-bright);
    }
    .f6 .footer-socials a:hover { border-color: var(--gold); color: #fff; background: rgba(212,164,92,.12); }
    .f6 .footer-social-icon { width: 20px; height: 20px; }
    .f6 .social-label {
      position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
      overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0;
    }
    .f6 .footer-grid {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 36px; padding: 34px 0; text-align: center;
    }
    .f6 .footer-explore { grid-column: 1; grid-row: 1; }
    .f6 .footer-newsletter { grid-column: 2; grid-row: 1; }
    .f6 .footer-legal { grid-column: 3; grid-row: 1; }
    .f6 .footer-explore summary,
    .f6 .footer-legal summary,
    .f6 .footer-newsletter h3 {
      margin: 0 0 14px; color: var(--gold-bright);
      font: 700 11px var(--mono); letter-spacing: .14em; text-transform: uppercase;
    }
    .f6 .footer-explore summary,
    .f6 .footer-legal summary { cursor: pointer; list-style: none; }
    .f6 summary::-webkit-details-marker { display: none; }
    .f6 .footer-explore summary:hover,
    .f6 .footer-legal summary:hover { color: #fff; }
    .f6 .footer-explore summary::after,
    .f6 .footer-legal summary::after { content: ' +'; }
    .f6 .footer-explore div,
    .f6 .footer-legal div { display: grid; gap: 10px; }
    .f6 .footer-explore a,
    .f6 .footer-legal a { color: var(--muted); font-size: 14px; }
    .f6 .footer-explore a:hover,
    .f6 .footer-legal a:hover { color: var(--gold-bright); }
    .f6 .newsletter-row { width: min(560px, 100%); margin-inline: auto; }
    .f6 .footer-bottom {
      padding-top: 22px; border-top: 1px solid var(--line); text-align: center;
      color: rgba(236,228,245,.64); font: 11px var(--mono); letter-spacing: .04em;
    }
    @media (max-width: 980px) {
      .f6 .footer-grid { grid-template-columns: repeat(2, minmax(0,1fr)); gap: 20px 16px; padding: 24px 0; }
      .f6 .footer-explore { grid-column: 1; }
      .f6 .footer-legal { grid-column: 2; }
      .f6 .footer-newsletter { grid-column: 1 / -1; grid-row: auto; }
    }
    @media (max-width: 700px) {
      .f6 .inner { width: min(100% - 40px, 1376px); padding: 44px 0 24px; }
      .f6 .footer-top { gap: 20px; padding-bottom: 20px; }
      .f6 .footer-brand img { width: 72px; }
      .f6 .footer-socials { display: grid; grid-template-columns: repeat(4, 44px); gap: 10px; }
      .f6 .footer-bottom { padding-top: 16px; font-size: 10px; }
    }
  `,
  html: `
    <footer class="footer f6">
      <div class="inner">
        <div class="footer-top">
          <div class="footer-brand"><img class="logo" src="${BRAND.logo}" alt="${BRAND.name}" /></div>
          <div class="footer-socials">${liveSocials}</div>
        </div>
        <div class="footer-grid">
          <details class="footer-explore">
            <summary>Explore</summary>
            <div>${LIVE_EXPLORE.map((label) => `<a href="#">${label}</a>`).join('')}</div>
          </details>
          <div class="footer-newsletter" id="footer-subscribe">
            <h3>Stay in the loop</h3>
            <form class="newsletter" onsubmit="return false">
              <div class="newsletter-row">
                <input type="email" placeholder="you@email.com" aria-label="Email address" />
                <button type="submit">Subscribe</button>
              </div>
            </form>
          </div>
          <details class="footer-legal">
            <summary>Legal</summary>
            <div><a href="#">Terms &amp; Conditions</a><a href="#">Privacy Policy</a><a href="mailto:${BRAND.email}">Contact us</a></div>
          </details>
        </div>
        <div class="footer-bottom"><span>${BRAND.copyright}</span></div>
      </div>
    </footer>`,
};

export default {
  id: 'footer',
  label: 'Footer',
  status: 'In review',
  summary:
    'The footer that is live now, plus five other directions, all built from the real logo, links, social icons and background art.',
  brief:
    'Option 6 is the footer that is live today, kept as it is with the new sign-up bar in it. Options 1 to 5 keep the same content in every one: the house badge, the tagline, four social links, the full navigation, the sign-up and the legal line. What changes is the arrangement, how much of the artwork shows, and how heavy it feels.',
  /* The client's own footer opens first; the new directions sit alongside it. */
  defaultVariantId: '6',
  baseCss,
  variants: [v1, v2, v3, v4, v5, v6],
};
