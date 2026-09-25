/* Everything a variant is allowed to share: the client's real brand facts and
   icons. Fill these from the client's own repo (content JSON, the live DOM, or
   their asset folder) rather than inventing values, so every option is judged
   on real copy. */

export const BRAND = {
  name: '{{CLIENT}}',
  tagline: 'One line of the client\'s real positioning copy.',
  copyright: '© 2026 {{CLIENT}} · All rights reserved.',
  email: 'bookings@example.com',
  /* The mark that goes on the component. Use the client's approved logo, and
     prefer an asset with transparency. */
  logo: '/assets/brand/logo.png',
};

export const NAV = [
  { label: 'Home', href: '#' },
  { label: 'Events', href: '#' },
];

export const LEGAL = [
  { label: 'Terms & Conditions', href: '#' },
  { label: 'Privacy Policy', href: '#' },
];

export const SOCIALS = [
  { label: 'Instagram', href: 'https://example.com' },
];

/* Background art used by the variants. Copy the files into this gallery rather
   than hotlinking the live site, so the review cannot break when the site
   redeploys. */
export const PLATES = {
  hero: '/assets/bg/plate-a.jpg',
};

export function socialIcon(label, className = 'icon') {
  const name = label.toLowerCase();
  if (name.includes('instagram')) {
    return `<svg class="${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.2"/><circle cx="12" cy="12" r="4.4"/><circle cx="17.4" cy="6.6" r="1.2" fill="currentColor" stroke="none"/></svg>`;
  }
  if (name.includes('youtube')) {
    return `<svg class="${className}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22.5 7.2a2.75 2.75 0 0 0-1.94-1.95C18.85 4.8 12 4.8 12 4.8s-6.85 0-8.56.45A2.75 2.75 0 0 0 1.5 7.2 28.6 28.6 0 0 0 1.05 12c0 1.62.15 3.23.45 4.8a2.75 2.75 0 0 0 1.94 1.95c1.71.45 8.56.45 8.56.45s6.85 0 8.56-.45a2.75 2.75 0 0 0 1.94-1.95c.3-1.57.45-3.18.45-4.8 0-1.62-.15-3.23-.45-4.8ZM9.8 15.3V8.7l5.7 3.3-5.7 3.3Z"/></svg>`;
  }
  if (name.includes('tiktok')) {
    return `<svg class="${className}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.6 2.8h-2.9v12.4a2.5 2.5 0 1 1-2.5-2.5c.24 0 .47.03.7.1v-3a5.6 5.6 0 1 0 4.7 5.5V8.8a6.7 6.7 0 0 0 3.9 1.25V7.15A3.9 3.9 0 0 1 16.6 3.3v-.5Z"/></svg>`;
  }
  if (name.includes('spotify')) {
    return `<svg class="${className}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.25a9.75 9.75 0 1 0 0 19.5 9.75 9.75 0 0 0 0-19.5Zm4.47 14.03a.72.72 0 0 1-.99.24c-2.72-1.66-6.15-2.04-10.18-1.11a.72.72 0 1 1-.32-1.41c4.42-1.01 8.21-.57 11.25 1.28.34.2.44.65.24 1Zm1.33-2.96a.9.9 0 0 1-1.24.3c-3.12-1.92-7.88-2.47-11.58-1.35a.9.9 0 1 1-.52-1.72c4.22-1.28 9.47-.66 13.04 1.53.42.25.55.81.3 1.24Zm.11-3.08C14.17 8 8.05 7.8 4.49 8.88a1.08 1.08 0 1 1-.63-2.07c4.09-1.24 10.89-.99 14.91 1.4a1.08 1.08 0 0 1-.86 2.03Z"/></svg>`;
  }
  return `<span class="${className}" aria-hidden="true">◆</span>`;
}

/* Furniture every variant must carry, so the comparison is fair: same links,
   same sign-up, same socials. */
export function componentFurniture() {
  return {
    socialRow: SOCIALS.map(
      (s) => `<a class="social" href="${s.href}" aria-label="${s.label}">${socialIcon(s.label)}</a>`,
    ).join(''),
    socialList: SOCIALS.map(
      (s) => `<a class="social-line" href="${s.href}" aria-label="${s.label}">${socialIcon(s.label)}<span>${s.label}</span></a>`,
    ).join(''),
    navLinks: NAV.map((n) => `<a href="${n.href}">${n.label}</a>`).join(''),
    legalLinks: LEGAL.map((n) => `<a href="${n.href}">${n.label}</a>`).join(''),
    newsletter: `
      <form class="newsletter" onsubmit="return false">
        <label class="newsletter-label" for="nl">Stay in the loop</label>
        <div class="newsletter-row">
          <input id="nl" type="email" placeholder="you@email.com" aria-label="Email address" />
          <button type="submit">Subscribe</button>
        </div>
      </form>`,
  };
}
