# Vercel Deploy Skill

## Description
Deploy the SISO Internal Lab codebase to Vercel.

## Usage
Run from the codebase directory:
```bash
cd /Users/shaansisodia/SISO_Workspace/SISO_Internal_Lab/codebase
vercel --prod --yes
```

## Prerequisites
- Vercel CLI installed
- Authenticated with `vercel whoami`
- Project linked with `.vercel/project.json`

## What it does
1. Builds the project (Vite + API)
2. Deploys to Vercel production
3. Returns the deployment URL

## Output
Returns the production URL after deployment.
