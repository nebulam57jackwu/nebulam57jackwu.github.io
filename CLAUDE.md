<!-- dual-agent-kit:start -->
## Multi-agent project index

- Read `.dual-agent-kit.json` and its canonical handoff before substantial work.
- Confirm the handoff writer is released, inspect Git state, and run `./scripts/verify.sh` before editing.
- With v4.1, use `python3 scripts/agent-workflow.py claim --owner <unique-session>` before editing.
- Transfer in order: `agent-workflow.py verify`, refresh handoff, `release --owner <session>`, then `./scripts/agent-handoff.sh`.
- Use solo mode for small tasks; add independent review/research only when the task warrants it.
- Read `docs/agent/PROJECT.md` or `DECISIONS.md` only when relevant; the handoff is the only active state.
- Treat Grok/research lanes as read-only unless the handoff explicitly transfers writer ownership.
- Use the dual-agent-workflow skill for setup, handoff, checkpoints, or worktrees.
<!-- dual-agent-kit:end -->
