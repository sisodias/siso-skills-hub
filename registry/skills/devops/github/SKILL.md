---
name: github
description: Complete GitHub workflow for SISO Internal Lab codebase
version: 1.0.0
tags:
  - github
  - git
  - workflow
---

# GitHub Skill

Complete GitHub workflow for SISO Internal Lab codebase.

## Location
`${SISO_WORKSPACE}/SISO_Internal_Lab/codebase`

## Commands

### branch
Create new feature branch:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
git checkout -b feature/<name>
```

### commit
Stage and commit changes:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
git add -A && git commit -m "<message>"
```

### push
Push branch to GitHub:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
git push -u origin $(git branch --show-current)
```

### merge
Merge current branch to main:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
git checkout main
git merge <branch>
git push
```

## Rules

- NEVER push directly to main
- Always create feature branches
- Test before merging to main
