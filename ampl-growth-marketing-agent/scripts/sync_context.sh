#!/usr/bin/env bash
# Syncs AMPLITUDE_CONTEXT.md from the funnel-optimization-agent into this agent.
# Run from anywhere inside the repo:  bash ampl-growth-marketing-agent/scripts/sync_context.sh
#
# The source is the single source of truth:
#   funnel-optimization-agent/AMPLITUDE_CONTEXT.md
# The copy here is consumed by the growth marketing agent / LLM prompts.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
SRC="$REPO_ROOT/funnel-optimization-agent/AMPLITUDE_CONTEXT.md"
DST="$REPO_ROOT/ampl-growth-marketing-agent/agent/AMPLITUDE_CONTEXT.md"

if [ ! -f "$SRC" ]; then
  echo "ERROR: source not found at $SRC" >&2
  exit 1
fi

# Prepend a sync header, then append the source content
{
  echo "<!-- SYNCED FROM: funnel-optimization-agent/AMPLITUDE_CONTEXT.md -->"
  echo "<!-- To update: run scripts/sync_context.sh from the repo root -->"
  echo ""
  cat "$SRC"
} > "$DST"

echo "✅  Synced $SRC → $DST"
