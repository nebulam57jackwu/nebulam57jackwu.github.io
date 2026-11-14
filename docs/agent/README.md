# Agent workflow

Read the manifest-selected handoff first. Keep stable context in PROJECT.md and decisions in DECISIONS.md.

1. Inspect Git and establish the verification baseline.
2. Run `python3 scripts/agent-workflow.py claim --owner <unique-session>`.
3. Work on one objective. Use solo for small tasks, pipeline for independent review, phase-shift for module relay.
4. Run `python3 scripts/agent-workflow.py verify`; review the diff and update the handoff.
5. Run `python3 scripts/agent-workflow.py release --owner <same-session>` and stop writing.
6. Run `./scripts/agent-handoff.sh` to check release and verification freshness.

Only commit when requested; a new HEAD requires a fresh verification receipt.
Parallel writers require separate branches/worktrees. Research is read-only by default.
