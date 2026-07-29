---
name: vercel
description: Deploy SISO Internal Lab to Vercel
version: 1.0.0
tags:
  - deployment
  - vercel
---

# Vercel Skill

Deploy SISO Internal Lab to Vercel.

## Location
`${SISO_WORKSPACE}/SISO_Internal_Lab/codebase`

## Commands

### Preview
Deploy preview build for testing:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
vercel --yes
```

### Production
Deploy to production:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
vercel --prod --yes
```

## Project Details

- **GitHub Repo:** Lordsisodia/siso-agency-internal
- **Vercel Project:** siso-internal
- **Auto-deploy:** Enabled on push to main branch

## Usage

1. Make changes in a feature branch
2. Test locally with `npm run dev`
3. Run Playwright tests: `npm run test:e2e`
4. Push branch: `github push`
5. Test with Vercel preview
6. Merge to main → Vercel auto-deploys

## Rules

- Only deploy to production after testing
- Use preview for testing
- Main branch pushes trigger auto-deploy
