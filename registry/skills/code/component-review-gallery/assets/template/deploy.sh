#!/usr/bin/env bash
# Deploy this gallery to its own Cloudflare Pages project.
#
#   ./deploy.sh              check, then publish
#   ./deploy.sh --dry-run    run the checks only, no upload
#
# Client-specific values live in gallery.config.json. The Pages project is kept
# separate from the client's live site on purpose: a review deploy must never be
# able to touch production.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f gallery.config.json ]; then
  echo "FAIL: gallery.config.json is missing" >&2
  exit 1
fi

cfg() { node -e "process.stdout.write(String(require('./gallery.config.json')['$1'] ?? ''))"; }

PROJECT="$(cfg project)"
CREDS="$(cfg credentials)"
ACCOUNT_VAR="$(cfg accountIdVar)"
TOKEN_VAR="$(cfg tokenVar)"
CREDS="${CREDS/#\~/$HOME}"

echo "==> checking every variant and asset"
node scripts/check.mjs

if [ "${1:-}" = "--dry-run" ]; then
  echo "==> dry run: checks passed, nothing uploaded"
  exit 0
fi

if [ ! -f "$CREDS" ]; then
  echo "FAIL: credentials file not found: $CREDS" >&2
  exit 1
fi
set -a; . "$CREDS"; set +a

if [ -z "${!ACCOUNT_VAR:-}" ] || [ -z "${!TOKEN_VAR:-}" ]; then
  echo "FAIL: $CREDS must define $ACCOUNT_VAR and $TOKEN_VAR" >&2
  exit 1
fi

# First run on a new client: the project has to exist before anything uploads.
CLOUDFLARE_API_TOKEN="${!TOKEN_VAR}" CLOUDFLARE_ACCOUNT_ID="${!ACCOUNT_VAR}" \
  npx --yes wrangler@4 pages project create "$PROJECT" --production-branch=main >/dev/null 2>&1 || true

echo "==> deploying site/ to Pages project $PROJECT"
CLOUDFLARE_API_TOKEN="${!TOKEN_VAR}" CLOUDFLARE_ACCOUNT_ID="${!ACCOUNT_VAR}" \
  npx --yes wrangler@4 pages deploy site \
  --project-name="$PROJECT" --branch=main --commit-dirty=true

echo
echo "Review links:"
echo "  index   https://$PROJECT.pages.dev/"
echo "  gallery https://$PROJECT.pages.dev/review.html"
